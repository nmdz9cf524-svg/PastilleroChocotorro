# Firmware ESP32 – Pastillero V3

Sketch: `pastillero_esp32/pastillero_esp32.ino` (Arduino IDE, placa **ESP32 Dev Module**).
No necesita librerías externas: `WiFi`, `time` y `Preferences` vienen con el core ESP32.

## Cómo funciona

- El rotor tiene 12 cavidades a 30°. **Una pastilla = avanzar una cavidad.**
- El motor solo gira **antihorario visto desde arriba**, el sentido para el que se diseñó el peine. Nunca da reversa.
- La hora se toma de internet (NTP). A cada horario de `HORARIOS[]` entrega una pastilla, una sola vez por día. Si el ESP32 estaba apagado a esa hora, **no** la entrega tarde.
- Botón: **corto** entrega una pastilla. **Largo (3 s)** hace el *cebado*.
- Al terminar de girar, el firmware apaga las bobinas. La caja reductora mantiene la posición sin corriente.

## Conexiones

| ESP32 | Va a | Nota |
|---|---|---|
| GPIO16 | ULN2003 IN1 | |
| GPIO17 | ULN2003 IN2 | |
| GPIO18 | ULN2003 IN3 | |
| GPIO19 | ULN2003 IN4 | |
| GPIO23 | Pulsador → GND | pull-up interno |
| GPIO21 | Zumbador activo (+) | opcional |
| GPIO2 | LED integrado | |
| GND | GND del ULN2003 y de la fuente de 5 V | **GND común obligatorio** |

Alimenta el ULN2003 y el motor con **5 V aparte** (≥ 1 A). No los alimentes desde el pin 3V3 del ESP32.
Cuando el motor gira consume unos 240 mA.

## Primera puesta en marcha

1. Escribe tu WiFi y tu `ZONA_HORARIA` en el código. Por defecto está `CST6`, el centro de México.
2. Prueba **sin pastillas**. Gira el disco con la mano (o con `j`/`J` en el Monitor Serie) hasta que una cavidad quede justo sobre la ventana de salida. El firmware toma esa posición como la de partida.
3. Envía `v`: el disco debe dar exactamente una vuelta y terminar en la misma marca.
   - Si gira en sentido horario, pon `INVERTIR_SENTIDO = true`.
   - Si se queda corto o se pasa siempre lo mismo, ajusta `PASOS_POR_VUELTA`.
   - Si se traba o vibra, sube `US_PASO_RAPIDO`. Más lento da más par.
4. Llena la reserva y haz **cebado** (pulsación larga o `c`).
   Después de rellenar, la cavidad que espera bajo el techo puede estar vacía. El cebado la avanza; puede que caiga una pastilla o ninguna.
5. Haz el registro de 100 entregas de la guía (pág. 4): simples, dobles, vacías y atascos.

## Cambios mecánicos necesarios para el 28BYJ-48

El CAD usa un motor nominal de **Ø32×25 con eje Ø6 centrado**. El 28BYJ-48 es distinto:

| | CAD actual | 28BYJ-48 |
|---|---|---|
| Cuerpo | Ø32 × 25 | Ø28 × 19, orejas con agujeros a 35 mm |
| Eje | Ø6, centrado | Ø5 con dos planos (3 mm), **descentrado ~8 mm** |
| Largo de eje | ~15 mm por encima del motor | ~10 mm |
| Par | — | ~30 mN·m (bajo) |

- **Bancada 10 y puente 11:** rediseñarlos para que el **eje** quede en el centro del rotor (0,0), no el cuerpo.
- **Cubo del rotor 03:** su agujero es Ø6.4 con prisioneros M3. Usa un acople 5→6 mm o reimprime el cubo con agujero en "D" para el eje de 5 mm.
- **Par:** el 28BYJ-48 es justo para mover rotor, cono y pastillas que pasan bajo el peine de TPU. Si se atasca a velocidad lenta, considera la versión de 12 V o un NEMA 17 con A4988.

## Limitaciones (pendiente)

- **Sin sensor de origen:** si el motor pierde pasos (atasco), el disco queda desalineado y el firmware no lo nota. Para corregirlo, añade un sensor hall A3144 con un imán en el rotor.
- **Sin confirmación de entrega:** la celda de carga y el HX711 no se usan todavía.
- Prototipo sin validación física. No lo uses como único medio para administrar medicación.
