/*
  PASTILLERO V4 - Firmware ESP32 (solo botón)
  ------------------------------------------------------------
  Cada vez que se pulsa el botón, el rotor avanza UNA cavidad (30°) y
  cae UNA pastilla al bolsillo de la rampa. No hay horarios, WiFi ni hora.

  Mecánica:
    - Rotor con 12 cavidades, una cada 30°.
    - Giro ANTIHORARIO visto desde arriba. Nunca gira en reversa
      (el barredor de la reserva está colocado para ese sentido).

  Hardware:
    - ESP32 DevKit (Arduino core 2.x o 3.x). Sirve cualquier Arduino:
      solo cambia los pines.
    - Motor 28BYJ-48 (5 V) + placa driver ULN2003
    - Pulsador táctil de 6x6 mm arriba, en la tapa de servicio (a GND, usa el
      pull-up interno). Sus dos cables llevan un conector de 2 pines para poder
      quitar la tapa.
    - LED (el integrado en GPIO2) y zumbador activo opcional

  Comandos por Monitor Serie (115200 baudios), para calibrar:
    d = entregar 1 pastilla (igual que el botón)
    j = ajuste fino +1°   J = ajuste fino +5°   (alinear sin contar cavidad)
    v = prueba de vuelta completa: 12 cavidades, SIN pastillas

  AVISO: prototipo sin validación física. No lo uses como único medio para
  administrar medicación.
*/

// ================== CONFIGURACIÓN ==================

// --- Pines ---
const int PIN_IN1    = 16;  // ULN2003 IN1
const int PIN_IN2    = 17;  // ULN2003 IN2
const int PIN_IN3    = 18;  // ULN2003 IN3
const int PIN_IN4    = 19;  // ULN2003 IN4
const int PIN_BOTON  = 23;  // pulsador táctil 6x6 a GND
const int PIN_LED    = 2;   // LED integrado
const int PIN_BUZZER = 21;  // zumbador activo (pon -1 si no usas)

// --- Motor 28BYJ-48 en medio paso ---
// Relación real de la caja ≈ 63.684:1  ->  64 * 63.684 = 4075.77 medios pasos por vuelta.
// 30° = 4075.77 / 12 = 339.65 medios pasos. Como no es entero, cada entrega da
// 339 o 340 medios pasos según toque: el objetivo se calcula desde el arranque,
// así que el error nunca se acumula, aunque se entreguen miles de pastillas.
// Si en la prueba 'v' el disco se queda corto o se pasa siempre lo mismo, ajusta este valor.
const float    PASOS_POR_VUELTA = 4075.7728f;
const int      CAVIDADES        = 12;        // 360° / 12 = 30° por pastilla
const bool     INVERTIR_SENTIDO = false;     // cámbialo si gira horario visto desde arriba
const uint32_t US_PASO_RAPIDO   = 2000;      // µs por medio paso en crucero (más alto = más par)
const uint32_t US_PASO_LENTO    = 3500;      // µs por medio paso al arrancar y al frenar
const int      PASOS_RAMPA      = 60;

// --- Botón ---
const uint32_t MS_ANTIREBOTE = 15;    // filtra el rebote del contacto (un pulsador táctil rebota < 10 ms)
const uint32_t MS_BLOQUEO    = 800;   // tras terminar una entrega, ignora pulsaciones durante este tiempo.
                                      // Mientras el rotor gira (~0.75 s) tampoco se leen. Así un doble
                                      // toque no da dos pastillas, y se puede pedir otra a los ~1.6 s.

// ===================================================

const uint8_t SECUENCIA[8][4] = {
  {1,0,0,0}, {1,1,0,0}, {0,1,0,0}, {0,1,1,0},
  {0,0,1,0}, {0,0,1,1}, {0,0,0,1}, {1,0,0,1}
};
const int PINES_MOTOR[4] = {PIN_IN1, PIN_IN2, PIN_IN3, PIN_IN4};

int  fase = 0;               // índice en SECUENCIA
int  cavidad = 0;            // cavidad actual dentro de la vuelta: 0..11
long entregas = 0;           // pastillas entregadas desde el arranque
long cavidadesTotales = 0;   // cavidades avanzadas desde el arranque (entregas + pruebas)
long pasosTotales = 0;       // medios pasos dados desde el arranque al avanzar cavidades
uint32_t finUltimaEntregaMs = 0;

// ---------------- Motor ----------------

void escribirFase(int f) {
  for (int i = 0; i < 4; i++) digitalWrite(PINES_MOTOR[i], SECUENCIA[f][i]);
}

void apagarBobinas() {
  for (int i = 0; i < 4; i++) digitalWrite(PINES_MOTOR[i], LOW);
}

// Da n medios pasos en el sentido de trabajo, con rampa al arrancar y al frenar.
void darPasos(long n) {
  const int dir = INVERTIR_SENTIDO ? -1 : 1;
  for (long i = 0; i < n; i++) {
    fase = (fase + dir + 8) % 8;
    escribirFase(fase);
    long borde = min(i, n - 1 - i);  // pasos hasta el inicio o el final más cercano
    uint32_t t = US_PASO_RAPIDO;
    if (borde < PASOS_RAMPA) {
      t = US_PASO_LENTO - (US_PASO_LENTO - US_PASO_RAPIDO) * borde / PASOS_RAMPA;
    }
    delayMicroseconds(t);
    if ((i & 0x3F) == 0) yield();
  }
  apagarBobinas();  // la caja reductora mantiene la posición sin corriente
}

// Gira exactamente 30°: una cavidad = una pastilla. El objetivo se calcula
// desde el arranque (en doble precisión), así los decimales no se acumulan.
void avanzarUnaCavidad() {
  cavidadesTotales++;
  long objetivo = llround((double)cavidadesTotales * PASOS_POR_VUELTA / CAVIDADES);
  darPasos(objetivo - pasosTotales);
  pasosTotales = objetivo;
  cavidad = (cavidad + 1) % CAVIDADES;
}

// Ajuste fino de alineación: mueve el disco sin contar cavidad; la posición
// donde quede pasa a ser la "alineada".
void ajusteFino(float grados) {
  darPasos(lroundf(grados * PASOS_POR_VUELTA / 360.0f));
}

// ---------------- Avisos ----------------

void pitido(int veces, int ms) {
  for (int i = 0; i < veces; i++) {
    digitalWrite(PIN_LED, HIGH);
    if (PIN_BUZZER >= 0) digitalWrite(PIN_BUZZER, HIGH);
    delay(ms);
    digitalWrite(PIN_LED, LOW);
    if (PIN_BUZZER >= 0) digitalWrite(PIN_BUZZER, LOW);
    delay(ms);
  }
}

// ---------------- Entrega ----------------

void entregarPastilla(const char* motivo) {
  digitalWrite(PIN_LED, HIGH);               // LED encendido mientras gira
  avanzarUnaCavidad();
  digitalWrite(PIN_LED, LOW);
  finUltimaEntregaMs = millis();             // el bloqueo cuenta desde que el rotor se detiene
  entregas++;
  Serial.printf("[ENTREGA] %s -> pastilla %ld (cavidad %d de %d)\n",
                motivo, entregas, cavidad == 0 ? CAVIDADES : cavidad, CAVIDADES);
  pitido(1, 120);                            // aviso: la pastilla está en el bolsillo
}

// ---------------- Botón ----------------

// Entrega en cuanto se detecta la pulsación (no espera a soltar). Mientras
// se mantiene pulsado no repite: hay que soltar y volver a pulsar.
void revisarBoton() {
  static bool estadoEstable = HIGH, ultimaLectura = HIGH;
  static uint32_t cambioMs = 0;

  bool lectura = digitalRead(PIN_BOTON);
  if (lectura != ultimaLectura) { cambioMs = millis(); ultimaLectura = lectura; }
  if (millis() - cambioMs < MS_ANTIREBOTE || lectura == estadoEstable) return;

  estadoEstable = lectura;
  if (estadoEstable != LOW) return;          // solo actuamos al pulsar

  if (entregas > 0 && millis() - finUltimaEntregaMs < MS_BLOQUEO) {
    Serial.println("[BOTON] ignorado: espera un momento entre pastillas");
    digitalWrite(PIN_LED, HIGH); delay(60); digitalWrite(PIN_LED, LOW);   // aviso visual
    return;
  }
  entregarPastilla("boton");
}

// ---------------- Serie ----------------

void revisarSerie() {
  if (!Serial.available()) return;
  char c = Serial.read();
  switch (c) {
    case 'd': entregarPastilla("serie"); break;
    case 'j': ajusteFino(1.0f); Serial.println("Ajuste +1°"); break;
    case 'J': ajusteFino(5.0f); Serial.println("Ajuste +5°"); break;
    case 'v':
      Serial.println("Prueba: 12 cavidades = 1 vuelta. Debe terminar en la misma marca.");
      for (int i = 0; i < CAVIDADES; i++) { avanzarUnaCavidad(); delay(300); }
      Serial.println("Prueba terminada.");
      break;
    default: break;
  }
}

// ---------------- Setup / loop ----------------

void setup() {
  Serial.begin(115200);
  delay(200);
  Serial.println("\n=== Pastillero V4 - entrega con boton ===");

  for (int i = 0; i < 4; i++) pinMode(PINES_MOTOR[i], OUTPUT);
  apagarBobinas();
  pinMode(PIN_BOTON, INPUT_PULLUP);
  pinMode(PIN_LED, OUTPUT);
  if (PIN_BUZZER >= 0) pinMode(PIN_BUZZER, OUTPUT);

  Serial.printf("30 grados = %.2f medios pasos (339 o 340 por entrega)\n", PASOS_POR_VUELTA / CAVIDADES);
  Serial.println("Se asume que el disco arranca ALINEADO (cavidad justo sobre la salida).");
  Serial.println("Pulsa el boton para entregar una pastilla. Serie: d=entregar j/J=ajuste v=prueba vuelta");
  pitido(2, 80);
}

void loop() {
  revisarBoton();
  revisarSerie();
}
