# Firmware ESP32: Pastillero V4 con botón

Sketch: `pastillero_esp32/pastillero_esp32.ino` (Arduino IDE, placa **ESP32 Dev Module**).
No necesita librerías externas.

## Cómo funciona

- Cada vez que pulsas el botón, el rotor gira **30°**, avanza **una cavidad** y cae **una pastilla** a la bandeja.
- La entrega empieza en cuanto pulsas; no hay que soltar. Mantener pulsado no repite: hay que soltar y volver a pulsar.
- Después de cada entrega, el botón queda ignorado **1.5 s** (`MS_BLOQUEO`), para que un doble toque no dé dos pastillas.
- El motor gira solo **antihorario visto desde arriba**, el sentido para el que está puesto el barredor de la reserva. Nunca da reversa.
- Al terminar de girar apaga las bobinas. La caja reductora mantiene la posición sin corriente.
- **Sin horarios, sin WiFi y sin hora:** esa parte se quitó.

### Por qué 339 o 340 pasos

El 28BYJ-48 da unos **4075.77 medios pasos por vuelta**: su reducción real es 63.684:1, no 64:1. 30° son 339.65 medios pasos, que no es un número entero. Por eso el firmware calcula cada objetivo desde el arranque y da 339 o 340 según toque. Comprobado: 12 pulsaciones dan una vuelta, y tras 1000 vueltas el error sigue por debajo de 0.03°.

## Conexiones

| ESP32 | Va a | Nota |
|---|---|---|
| GPIO16 | ULN2003 IN1 | |
| GPIO17 | ULN2003 IN2 | |
| GPIO18 | ULN2003 IN3 | |
| GPIO19 | ULN2003 IN4 | |
| GPIO23 | Botón de 12 mm → GND | pull-up interno |
| GPIO21 | Zumbador activo (+) | opcional (pon `PIN_BUZZER = -1` si no lo usas) |
| GPIO2 | LED integrado | se enciende mientras gira |
| GND | GND del ULN2003 y de la fuente de 5 V | **GND común obligatorio** |

Alimenta el ULN2003 y el motor con **5 V aparte** (≥ 1 A), no desde el pin 3V3 del ESP32. El motor consume unos 240 mA mientras gira.

## Montaje mecánico (ya está en el CAD V4)

- **Botón:** pulsador de panel de **12 mm**, normalmente abierto. Va en el agujero de la pared frontal de la carcasa 01, centrado bajo la ventana de la bandeja, y se aprieta con su tuerca por dentro. Detrás hay unos 28 mm libres para el cuerpo y los cables.
- **Motor:** el 28BYJ-48 entra por arriba en la bancada 10 nueva y se atornilla por sus dos orejas con **2 M3×8** y tuercas atrapadas debajo. Su eje queda justo bajo el centro del rotor. El puente 11 ya no hace falta.
- **Rotor:** el rotor 03 nuevo tiene el agujero en doble D para el eje Ø5 de doble plano y **un prisionero M3×8** que aprieta contra un plano. El rotor de V3 (agujero redondo Ø6.4) no sirve con este motor.
- **Electrónica:** la placa ULN2003 va en el piso, a la izquierda de la bancada; el cable del motor sale por detrás. El ESP32 va en la plataforma de la derecha, junto al paso de cable.

Las medidas del motor son las de la hoja de datos estándar: cuerpo Ø28 × 19 mm, orejas a 35 mm, eje Ø5 con planos de 3 mm, descentrado 8 mm. Compruébalas con tu motor antes de imprimir la bancada. Si alguna cambia, están al principio de la sección del motor en `Pastillero_V4/Codigo_CAD/generar_pastillero_v4.py`.

## Primera puesta en marcha

1. Prueba **sin pastillas**. Gira el disco con la mano (o con `j`/`J` en el Monitor Serie) hasta que una cavidad quede justo sobre la ventana de salida. El firmware toma esa posición como la de partida.
2. Envía `v`: el disco debe dar exactamente una vuelta y terminar en la misma marca.
   - Si gira en sentido horario, pon `INVERTIR_SENTIDO = true`.
   - Si se queda corto o se pasa siempre lo mismo, ajusta `PASOS_POR_VUELTA`.
   - Si se traba o vibra, sube `US_PASO_RAPIDO`. Más lento da más par.
3. Pulsa el botón varias veces: cada pulsación debe mover exactamente una cavidad.
4. Llena la reserva y prueba con pastillas ficticias: cada pulsación debe dejar una pastilla en el bolsillo de la bandeja. Anota simples, dobles, vacías y atascos.

## Limitaciones

- **Sin sensor de origen:** si el motor pierde pasos (un atasco), el disco queda desalineado y el firmware no lo nota. Para corregirlo, añade un sensor hall A3144 con un imán en el rotor.
- **Sin confirmación de entrega:** la celda de carga y el HX711 todavía no se usan.
- Prototipo sin validación física. No lo uses como único medio para administrar medicación.
