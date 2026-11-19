/*
  PASTILLERO V3 - Firmware ESP32
  ------------------------------------------------------------
  Mecánica (según los planos de la carpeta prototp):
    - Disco/rotor con 12 cavidades, una cada 30°.
    - Giro de trabajo ANTIHORARIO visto desde arriba (nunca en reversa:
      el peine flexible está colocado para ese sentido).
    - La salida está en Y negativo (270°), bajo el techo fijo 235°..305°.
    - Entregar UNA pastilla = avanzar UNA cavidad (30°).

  Hardware:
    - ESP32 DevKit (Arduino core 2.x o 3.x)
    - Motor paso a paso 28BYJ-48 (5 V) + driver ULN2003
    - Pulsador (a GND, usa pull-up interno)
    - LED (el integrado en GPIO2) y zumbador activo opcional

  Disparo:
    - Horarios diarios (hora tomada de internet por WiFi/NTP).
    - Botón: pulsación corta = entregar 1 pastilla.
             pulsación larga (3 s) = "cebar": avanza 1 cavidad
             (úsalo después de rellenar la reserva; ver LEEME).

  Comandos por Monitor Serie (115200 baudios):
    d = entregar 1 pastilla        c = cebar (avanzar 1 cavidad)
    j = ajuste fino +1° (alinear)  J = ajuste fino +5°
    h = ver hora y horarios        v = prueba de vuelta completa (12 cavidades, SIN pastillas)

  AVISO: prototipo sin validación física. No lo uses como único medio para
  administrar medicación hasta haber hecho las pruebas del LEEME.
*/

#include <WiFi.h>
#include <time.h>
#include <Preferences.h>

// ================== CONFIGURACIÓN ==================

// --- WiFi ---
const char* WIFI_SSID     = "TU_RED_WIFI";
const char* WIFI_PASSWORD = "TU_CONTRASENA";

// --- Zona horaria (formato POSIX) ---
// México centro (sin horario de verano desde 2022): "CST6"
// Colombia/Perú: "<-05>5"   Argentina: "<-03>3"   España: "CET-1CEST,M3.5.0,M10.5.0/3"
const char* ZONA_HORARIA = "CST6";

// --- Horarios de entrega diaria (24 h). Agrega o quita filas. ---
struct Horario { uint8_t hora; uint8_t minuto; };
const Horario HORARIOS[] = {
  { 8, 0},
  {20, 0},
};
const int NUM_HORARIOS = sizeof(HORARIOS) / sizeof(HORARIOS[0]);

// --- Pines ---
const int PIN_IN1 = 16;   // ULN2003 IN1
const int PIN_IN2 = 17;   // ULN2003 IN2
const int PIN_IN3 = 18;   // ULN2003 IN3
const int PIN_IN4 = 19;   // ULN2003 IN4
const int PIN_BOTON  = 23;  // pulsador a GND
const int PIN_LED    = 2;   // LED integrado
const int PIN_BUZZER = 21;  // zumbador activo (pon -1 si no usas)

// --- Motor 28BYJ-48 en medio paso ---
// Relación real de la caja ≈ 63.684:1  ->  64 * 63.684 = 4075.77 medios pasos/vuelta.
// (No uses 4096: acumularía ~1.8° de error por vuelta.)
const float  PASOS_POR_VUELTA = 4075.7728f;
const int    CAVIDADES        = 12;
const bool   INVERTIR_SENTIDO = false;   // cámbialo si el disco gira horario visto desde arriba
const uint32_t US_PASO_RAPIDO = 2000;    // µs por medio paso en crucero (más alto = más par)
const uint32_t US_PASO_LENTO  = 3500;    // µs por medio paso al arrancar
const int    PASOS_RAMPA      = 60;

// --- Botón ---
const uint32_t MS_PULSACION_LARGA = 3000;
const uint32_t MS_ANTIREBOTE      = 40;
const uint32_t MS_ANTIREPETICION  = 5000;  // bloqueo entre entregas manuales

// ===================================================

const uint8_t SECUENCIA[8][4] = {
  {1,0,0,0}, {1,1,0,0}, {0,1,0,0}, {0,1,1,0},
  {0,0,1,0}, {0,0,1,1}, {0,0,0,1}, {1,0,0,1}
};
const int PINES_MOTOR[4] = {PIN_IN1, PIN_IN2, PIN_IN3, PIN_IN4};

int  fase = 0;           // índice en SECUENCIA
long pasosAcumulados = 0; // medios pasos dados desde el arranque (solo hacia adelante)
long cavidadActual = 0;   // cavidades avanzadas desde el arranque

Preferences prefs;
uint32_t ultimaEntregaManualMs = 0;
bool horaValida = false;

// ---------------- Motor ----------------

void escribirFase(int f) {
  for (int i = 0; i < 4; i++) digitalWrite(PINES_MOTOR[i], SECUENCIA[f][i]);
}

void apagarBobinas() {
  for (int i = 0; i < 4; i++) digitalWrite(PINES_MOTOR[i], LOW);
}

// Da n medios pasos hacia adelante (sentido de trabajo) con rampa de arranque.
void darPasos(long n) {
  const int dir = INVERTIR_SENTIDO ? -1 : 1;
  for (long i = 0; i < n; i++) {
    fase = (fase + dir + 8) % 8;
    escribirFase(fase);
    uint32_t t = US_PASO_RAPIDO;
    if (i < PASOS_RAMPA) {
      t = US_PASO_LENTO - (US_PASO_LENTO - US_PASO_RAPIDO) * i / PASOS_RAMPA;
    }
    delayMicroseconds(t);
    if ((i & 0xFF) == 0) yield();
  }
  apagarBobinas();  // la caja reductora mantiene la posición sin corriente
}

// Avanza exactamente una cavidad. El objetivo se calcula desde el total
// acumulado para que los decimales no acumulen error.
void avanzarUnaCavidad() {
  cavidadActual++;
  long objetivo = lroundf(cavidadActual * PASOS_POR_VUELTA / CAVIDADES);
  long n = objetivo - pasosAcumulados;
  darPasos(n);
  pasosAcumulados = objetivo;
}

// Ajuste fino de alineación: mueve el disco sin cambiar la referencia,
// así la posición donde quede pasa a ser la "alineada".
void ajusteFino(float grados) {
  long n = lroundf(grados * PASOS_POR_VUELTA / 360.0f);
  darPasos(n);
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
  Serial.printf("[ENTREGA] %s -> avanzando cavidad %ld\n", motivo, cavidadActual + 1);
  avanzarUnaCavidad();
  pitido(3, 150);  // aviso al paciente: la pastilla está en la bandeja
}

void cebar() {
  Serial.println("[CEBADO] avanzando 1 cavidad");
  avanzarUnaCavidad();
  pitido(1, 400);
}

// ---------------- Hora y horarios ----------------

bool obtenerHora(struct tm& t) {
  time_t ahora = time(nullptr);
  localtime_r(&ahora, &t);
  return t.tm_year + 1900 >= 2024;  // antes de sincronizar NTP la fecha es 1970
}

// Revisa si toca una entrega programada. Guarda en memoria flash el día
// de la última entrega de cada horario para no repetirla si el ESP32 se
// reinicia dentro del mismo minuto. Las tomas perdidas por estar apagado
// NO se entregan tarde (más seguro que dar dosis fuera de hora).
void revisarHorarios() {
  struct tm t;
  if (!obtenerHora(t)) return;
  if (!horaValida) {
    horaValida = true;
    Serial.printf("[HORA] sincronizada: %02d:%02d:%02d\n", t.tm_hour, t.tm_min, t.tm_sec);
  }
  int32_t claveDia = (t.tm_year + 1900) * 10000 + (t.tm_mon + 1) * 100 + t.tm_mday;
  for (int i = 0; i < NUM_HORARIOS; i++) {
    if (t.tm_hour != HORARIOS[i].hora || t.tm_min != HORARIOS[i].minuto) continue;
    char clave[8];
    snprintf(clave, sizeof(clave), "h%d", i);
    if (prefs.getInt(clave, 0) == claveDia) continue;  // ya entregada hoy
    prefs.putInt(clave, claveDia);
    char motivo[32];
    snprintf(motivo, sizeof(motivo), "horario %02d:%02d", HORARIOS[i].hora, HORARIOS[i].minuto);
    entregarPastilla(motivo);
  }
}

void mostrarEstado() {
  struct tm t;
  if (obtenerHora(t)) {
    Serial.printf("Hora: %04d-%02d-%02d %02d:%02d:%02d\n", t.tm_year + 1900, t.tm_mon + 1,
                  t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec);
  } else {
    Serial.println("Hora: sin sincronizar (revisa WiFi)");
  }
  Serial.printf("WiFi: %s\n", WiFi.isConnected() ? WiFi.localIP().toString().c_str() : "desconectado");
  Serial.print("Horarios:");
  for (int i = 0; i < NUM_HORARIOS; i++) Serial.printf(" %02d:%02d", HORARIOS[i].hora, HORARIOS[i].minuto);
  Serial.printf("\nCavidades avanzadas desde el arranque: %ld\n", cavidadActual);
}

// ---------------- Botón ----------------

void revisarBoton() {
  static bool estadoEstable = HIGH, ultimaLectura = HIGH;
  static uint32_t cambioMs = 0, pulsadoDesdeMs = 0;
  static bool largaHecha = false;

  bool lectura = digitalRead(PIN_BOTON);
  if (lectura != ultimaLectura) { cambioMs = millis(); ultimaLectura = lectura; }
  if (millis() - cambioMs < MS_ANTIREBOTE) return;

  if (lectura != estadoEstable) {
    estadoEstable = lectura;
    if (estadoEstable == LOW) {               // se pulsó
      pulsadoDesdeMs = millis();
      largaHecha = false;
    } else if (!largaHecha) {                 // se soltó antes de 3 s
      if (millis() - ultimaEntregaManualMs >= MS_ANTIREPETICION || ultimaEntregaManualMs == 0) {
        ultimaEntregaManualMs = millis();
        entregarPastilla("boton");
      } else {
        Serial.println("[BOTON] ignorado (anti-repeticion)");
        pitido(1, 60);
      }
    }
  }
  if (estadoEstable == LOW && !largaHecha && millis() - pulsadoDesdeMs >= MS_PULSACION_LARGA) {
    largaHecha = true;
    cebar();
  }
}

// ---------------- Serie ----------------

void revisarSerie() {
  if (!Serial.available()) return;
  char c = Serial.read();
  switch (c) {
    case 'd': entregarPastilla("serie"); break;
    case 'c': cebar(); break;
    case 'j': ajusteFino(1.0f);  Serial.println("Ajuste +1°"); break;
    case 'J': ajusteFino(5.0f);  Serial.println("Ajuste +5°"); break;
    case 'h': mostrarEstado(); break;
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
  Serial.println("\n=== Pastillero V3 - ESP32 ===");

  for (int i = 0; i < 4; i++) pinMode(PINES_MOTOR[i], OUTPUT);
  apagarBobinas();
  pinMode(PIN_BOTON, INPUT_PULLUP);
  pinMode(PIN_LED, OUTPUT);
  if (PIN_BUZZER >= 0) pinMode(PIN_BUZZER, OUTPUT);

  prefs.begin("pastillero", false);

  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(true);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  configTzTime(ZONA_HORARIA, "pool.ntp.org", "time.google.com");

  Serial.println("Se asume que el disco arranca ALINEADO (cavidad sobre la salida).");
  Serial.println("Comandos: d=entregar c=cebar j/J=ajuste h=estado v=prueba vuelta");
  pitido(2, 80);
}

void loop() {
  revisarBoton();
  revisarSerie();

  static uint32_t ultimaRevisionMs = 0;
  if (millis() - ultimaRevisionMs >= 1000) {
    ultimaRevisionMs = millis();
    revisarHorarios();
  }
}
