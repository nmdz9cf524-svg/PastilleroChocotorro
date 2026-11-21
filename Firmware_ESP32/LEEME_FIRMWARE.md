# Firmware ESP32: Pastillero V4 con botón

Sketch: `pastillero_esp32/pastillero_esp32.ino` (Arduino IDE, placa **ESP32 Dev Module**).
No necesita librerías externas.

## Cómo funciona

- Cada vez que pulsas el botón, el rotor gira **30°** (unos 0.77 s), avanza **una cavidad** y cae **una pastilla** al bolsillo de la rampa.
- La entrega empieza en cuanto pulsas; no hay que soltar. Mantener pulsado no repite: hay que soltar y volver a pulsar.
- Mientras el rotor gira no se leen pulsaciones, y al pararse el botón queda ignorado **0.8 s** más (`MS_BLOQUEO`). Así un doble toque no da dos pastillas, y se puede pedir otra a los ~1.6 s. Si pulsas durante el bloqueo, el LED parpadea.
- El filtro de rebote es de **15 ms** (`MS_ANTIREBOTE`): un toque corto de 40 ms cuenta y el ruido de 10 ms no.
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
| GPIO23 | Pulsador táctil 6×6 → GND | pull-up interno |
| GPIO21 | Zumbador activo (+) | opcional (pon `PIN_BUZZER = -1` si no lo usas) |
| GPIO2 | LED integrado | se enciende mientras gira |
| GND | GND del ULN2003 y de la fuente de 5 V | **GND común obligatorio** |

Alimenta el ULN2003 y el motor con **5 V aparte** (≥ 1 A), no desde el pin 3V3 del ESP32. El motor consume unos 240 mA mientras gira.

## Montaje mecánico (ya está en el CAD V4)

- **Botón:** pulsador táctil de **6×6** (el común de 4 patas; vale de 9.5 mm o de 8 mm de alto), **arriba, en la esquina frontal derecha de la tapa de servicio 21**. Entra deslizándose por debajo de la tapa, desde el lado de la reserva, en un alojamiento con piso: sus patas pasan por dos ranuras y, al pulsarlo, el cuerpo apoya en ese piso. El vástago asoma por un agujero de Ø4.2.
  - Suelda dos cables a dos patas **opuestas en diagonal**, que siempre forman el contacto, y termínalos en un **conector de 2 pines** (tipo Dupont). Así puedes desconectar el botón al levantar la tapa de servicio para mantenimiento. Los cables bajan por la esquina interior de la tapa hasta el ESP32.
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
3. Pulsa el botón varias veces, dejando 2 s entre pulsaciones: cada una debe mover exactamente una cavidad.
4. Llena la reserva y prueba con pastillas ficticias: cada pulsación debe dejar una pastilla en el bolsillo de la rampa. Anota simples, dobles, vacías y atascos.

## Prueba de la lógica sin hardware

`prueba_logica/` compila el sketch con un sustituto mínimo de Arduino que simula el reloj y el botón con rebote:

```
cd prueba_logica
g++ -std=c++17 -I. prueba_boton.cpp -o prueba_boton && ./prueba_boton
```

Comprueba 10 casos: pulsación con rebote, pulsación mantenida, doble toque, pulsación durante el giro, pulsaciones a 1.7 s y a 2.5 s, toque de 40 ms, ruido de 10 ms y 12 pulsaciones. Debe responder **TODO OK**, con 12 pulsaciones = 1 vuelta y un error menor de 0.03° tras 1000 vueltas. No sustituye compilar con el núcleo del ESP32 en el Arduino IDE.

## Limitaciones

- **Sin sensor de origen:** si el motor pierde pasos (un atasco), el disco queda desalineado y el firmware no lo nota. Para corregirlo, añade un sensor hall A3144 con un imán en el rotor.
- **Sin confirmación de entrega:** se quitó el sistema de pesaje, así que el firmware no sabe si de verdad cayó una pastilla. Revisa el bolsillo.
- Prototipo sin validación física. No lo uses como único medio para administrar medicación.
