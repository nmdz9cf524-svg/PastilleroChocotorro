// Prueba de la lógica del firmware sin hardware: compila el sketch con un
// sustituto mínimo de Arduino (Arduino.h de esta carpeta) que simula el reloj
// y el botón con rebote, y comprueba que cada pulsación real entregue una sola
// pastilla (30°), que no haya repeticiones ni deriva.
//   g++ -std=c++17 -I. prueba_boton.cpp -o prueba_boton && ./prueba_boton
#include "Arduino.h"
#include "../pastillero_esp32/pastillero_esp32.ino"

// ---- pruebas de comportamiento ----
struct Press { double t0, dur; };          // segundos
static std::vector<Press> presses;
static double base_s = 0;                  // inicio del escenario actual
static int bounceLevel(uint64_t us) {
  double t = us / 1e6 - base_s;
  for (auto& p : presses) {
    if (t >= p.t0 && t < p.t0 + p.dur) {
      double k = t - p.t0;                            // rebote de 5 ms al pulsar y al soltar
      if (k < 0.005) return ((int)(k * 2000)) % 2 ? HIGH : LOW;
      if (p.dur - k < 0.005) return ((int)(k * 2000)) % 2 ? LOW : HIGH;
      return LOW;
    }
  }
  return HIGH;
}
long runScenario(const char* name, std::vector<Press> ps, double totalSec) {
  presses = ps; buttonLevel = bounceLevel;
  long e0 = entregas; long s0 = totalSteps;
  base_s = now_us / 1e6;
  while (now_us / 1e6 - base_s < totalSec) { loop(); now_us += 1000; }   // loop cada 1 ms
  long got = entregas - e0;
  printf("%-55s -> %ld entrega(s), %ld medios pasos\n", name, got, totalSteps - s0);
  return got;
}
int main() {
  setup();
  int fails = 0;
  auto expect = [&](const char* n, std::vector<Press> ps, double T, long want) {
    // reiniciar reloj y estado de entrega entre escenarios
    long got = runScenario(n, ps, T);       // el reloj sigue corriendo, como en el ESP32
    if (got != want) { printf("   FALLO: se esperaban %ld\n", want); fails++; }
  };
  expect("1 pulsacion corta con rebote", {{0.5, 0.15}}, 4, 1);
  expect("pulsacion mantenida 3 s (no repite)", {{0.5, 3.0}}, 6, 1);
  expect("doble toque rapido (0.3 s entre ambos)", {{0.5, 0.1}, {0.9, 0.1}}, 5, 1);
  expect("2 pulsaciones separadas 2.5 s", {{0.5, 0.1}, {3.0, 0.1}}, 7, 2);
  expect("pulsacion durante el giro (se ignora)", {{0.5, 0.1}, {0.8, 0.1}}, 5, 1);
  expect("2 pulsaciones separadas 1.7 s", {{0.5, 0.1}, {2.2, 0.1}}, 5, 2);
  expect("2a pulsacion 0.3 s despues de parar el rotor (bloqueada)", {{0.5, 0.1}, {1.6, 0.1}}, 4, 1);
  expect("pulsaciones de 40 ms (toque muy corto)", {{0.5, 0.04}, {2.5, 0.04}}, 5, 2);
  expect("ruido de 10 ms (no es pulsacion)", {{0.5, 0.01}}, 2, 0);
  expect("12 pulsaciones separadas 2.5 s", [](){ std::vector<Press> v; for (int i=0;i<12;i++) v.push_back({0.5+2.5*i,0.1}); return v; }(), 32, 12);
  printf("Entregas totales %ld, cavidad %d (debe ser %ld)\n", entregas, cavidad, entregas % 12);
  if (cavidad != entregas % 12) fails++;
  // Sin deriva: 1000 vueltas más.
  long s0 = totalSteps; for (int i = 0; i < 12 * 1000; i++) avanzarUnaCavidad();
  double err = (totalSteps - s0 - 1000 * PASOS_POR_VUELTA) * 360.0 / PASOS_POR_VUELTA;
  printf("1000 vueltas: error %.3f grados\n", err);
  if (fabs(err) > 0.05) fails++;
  printf(fails ? "HAY FALLOS\n" : "TODO OK\n");
  return fails;
}
