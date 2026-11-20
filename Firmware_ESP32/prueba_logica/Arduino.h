#pragma once
// Sustituto mínimo de Arduino con reloj simulado y botón programable.
#include <cstdio>
#include <cstdint>
#include <cmath>
#include <algorithm>
#include <functional>
#include <vector>
using std::min;
#define HIGH 1
#define LOW 0
#define OUTPUT 1
#define INPUT_PULLUP 2
static uint64_t now_us = 0;                      // reloj simulado
static long totalSteps = 0;                      // medios pasos dados (escrituras de fase)
static std::function<int(uint64_t)> buttonLevel = [](uint64_t){ return HIGH; };
inline void digitalWrite(int, int) {}
inline int digitalRead(int p) { return p == 23 ? buttonLevel(now_us) : HIGH; }
inline void pinMode(int, int) {}
inline void delay(unsigned long ms) { now_us += ms * 1000ULL; }
inline void delayMicroseconds(unsigned long us) { now_us += us; totalSteps++; }
inline void yield() {}
inline unsigned long millis() { return (unsigned long)(now_us / 1000ULL); }
struct SerialC { void begin(int) {} template<class... A> void printf(const char* f, A... a) { ::printf(f, a...); }
  void println(const char* s) { ::puts(s); } int available() { return 0; } char read() { return 0; } };
static SerialC Serial;
