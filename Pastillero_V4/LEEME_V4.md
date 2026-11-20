# Pastillero V4: piezas simplificadas

V4 parte de V3 y usa el motor **28BYJ-48 con driver ULN2003** y un **botón de entrega**: cada pulsación gira el rotor 30° y deja una pastilla. El cono y la forma del techo son los mismos. Lo que cambia es la carcasa, la zona de la celda de carga y el número de piezas sueltas. La reserva ahora lleva integrados el techo, los separadores y un barredor rígido (ya no hay aro ni peine sueltos), la tapa pasa a ser una pieza cuadrada que cubre todo, y una bandeja inclinada saca la pastilla por la ventana.

> **Para imprimir, ve directo a [`Impresion_255x255/`](Impresion_255x255/LEEME_IMPRESION.md).** Ahí están las 2 placas listas para una cama de 255 × 255.

## Carpetas

| Carpeta | Qué contiene |
|---|---|
| `Impresion_255x255/` | **Placas listas para imprimir** (.3mf, .stl y vista previa) y la guía de impresión |
| `Guia_visual/` | **Guía animada de ensamble** (`Ensamble_Pastillero_V4.html`) y **simulación del botón** (`Simulacion_boton_V4.html`). Se abren con doble clic; necesitan internet para cargar three.js |
| `STL/` | Cada pieza suelta, ya orientada, por si hay que reimprimir una |
| `STEP_piezas/` | Piezas en coordenadas de ensamble, para editar en CAD |
| `Pastillero_V4_ensamble.step` | Ensamble completo, con tornillería y referencias |
| `Referencias_NO_imprimir/` | Motor 28BYJ-48, botón, ULN2003, ESP32, celda y tornillería. **No se imprimen.** |
| `Codigo_CAD/` | Scripts que generan, validan y arman las placas, más `fuentes_V3/` con las piezas de V3 que se reutilizan |

![Vista V4](Vista_pastillero_V4.png)

## Qué cambió y por qué

| V3 | V4 | Motivo |
|---|---|---|
| 01 carcasa + 19 patas ×4 (pegadas) | **01 carcasa** con patas integradas | Las patas forman ahora una base nervada de 3 mm bajo el piso. Las celdas son de unos 28 mm, así que el piso se imprime como puentes cortos, sin soportes. Las cabezas de los tornillos quedan dentro de las celdas. |
| 12 pedestal (2 M3 al piso, se caía) | Pedestal **integrado en 01** | Va unido al piso y a la pared frontal y lleva un contrafuerte, así que ya no se puede caer. |
| no existía | **Segundo apoyo = tope de sobrecarga** integrado en 01 | Está debajo del extremo móvil de la celda, con 0.45 mm de holgura. No toca en uso normal: solo frena la bandeja si se aprieta o se golpea, para que la celda no se doble ni se suelte. (La celda tiene que quedar en voladizo para medir, por eso el segundo apoyo no la sujeta.) |
| 18 plataforma electrónica (4 M3) | Plataforma **integrada en 01** | Se conservan las ranuras para bridas y se agrega un paso de cable de 14×8 mm en la pared +X. Ahí va el ESP32. |
| no existía | **Botón de entrega en 01** | Agujero de 12 mm en la pared frontal, centrado bajo la ventana y justo debajo del bolsillo de la bandeja. Lleva un pulsador de panel de 12 mm con tuerca. Detrás hay unos 28 mm libres para el cuerpo y los cables. |
| 10 bancada + 11 puente (motor Ø32 centrado) | **10 bancada para 28BYJ-48** | El 28BYJ-48 tiene el eje descentrado 8 mm: la bancada lo coloca para que el eje quede justo bajo el centro del rotor. El motor entra por arriba en su placa y se atornilla por sus dos orejas con 2 M3×8 y tuercas atrapadas. Ya no hay puente. Se imprime boca abajo. |
| 03 rotor (agujero Ø6.4, 2 prisioneros) | **03 rotor para eje D5** | Agujero en doble D para el eje Ø5 de doble plano del 28BYJ-48 y un prisionero M3×8 contra un plano. El rotor de V3 no sirve con este motor. |
| 13 mordaza (M3×16 desde arriba) | **13 mordaza con tuercas** | Los dos M3×30 entran **desde debajo de la carcasa**, con la cabeza alojada en el piso, y roscan en tuercas atrapadas en la 13. |
| 14 + 15 + 16 (3 piezas, 2 M3×20) | **16 bandeja inclinada de una pieza** | El fondo baja a **25°** hacia la ventana frontal y termina en un **bolsillo que sale 17.5 mm por fuera de la caja**. La pastilla resbala sola y se toma desde fuera sin meter la mano, y como sigue sobre la bandeja, se sigue pesando. Un manguito abraza el extremo móvil de la celda y se fija con 1 prisionero M3×10 que se aprieta desde dentro de la bandeja. |
| 17 canal | Boca del canal cortada en diagonal | Sigue la rampa con 10 mm de paso, para que la pastilla caiga y salga por debajo. |
| 02 placa + 17 canal (2 M3×8) | **02 placa con canal** | Se imprime con la cara superior de la placa sobre la cama, así queda lisa para el disco. |
| 04 aro con techo + 05 separadores ×4 | **Integrados en la reserva 07** | El techo sigue tapando la salida, así no caen pastillas de golpe cuando una cavidad se alinea con la ventana. Los separadores siguen fijando el hueco del disco. Ya no son piezas sueltas. |
| 20 peine TPU (2 M3×8) | **Barredor integrado en la reserva 07** | Un bloque rígido baja de la pared de la reserva hasta 0.6 mm del disco, justo antes del techo. Las pastillas metidas en su cavidad pasan por debajo y las que van encima se empujan hacia el cono. Su cara de ataque está inclinada para empujarlas hacia dentro y no contra la pared. Ya no hace falta TPU. |
| 07 reserva | **07 reserva con techo, separadores y barredor** | Una sola pieza, impresa boca abajo. Sobre el techo, por dentro, lleva un relleno a 45°: así se imprime sin soportes y la pastilla que cae encima resbala hacia el cono. La pestaña lleva un chaflán de 45° con huecos para las cabezas de los M3×30. Un poste entra en un agujero de la placa 02, así que la reserva solo se monta en la posición correcta. |
| 09 tapa redonda | **21 tapa cuadrada de una pieza** | Sustituye a la tapa 09 y al embellecedor. Es una caja de 125 × 125 a ras de la carcasa que cubre placa, disco y reserva y cierra arriba. Una ceja circular por dentro entra en la boca de la reserva, y 4 pestañas en las esquinas entran en la carcasa. Para rellenar se levanta entera. |

Balance: de **25 piezas impresas → 9**, de **29 tornillos/prisioneros → 17** y de **29 tuercas → 18**. Ya no hace falta filamento flexible.

## Piezas a imprimir

La forma más rápida es usar las **placas de [`Impresion_255x255/`](Impresion_255x255/LEEME_IMPRESION.md)**:

| Placa | Piezas | Capa |
|---|---|---|
| 1 · Estructura (PLA) | 01, 06, 10, 13, 16 | 0.28 mm |
| 2 · Mecanismo y tapa (PLA) | 21, 07, 02, 03 | 0.20 mm |

Estas piezas sueltas en `STL/` necesitan una orientación concreta:

| N.º | Pieza | Orientación |
|---|---|---|
| 01 | Carcasa con patas, pedestal, tope y plataforma | Base nervada sobre la cama. Sin soportes. |
| 02 | Placa inferior con canal | Placa abajo, canal hacia arriba. |
| 16 | Bandeja inclinada | De pie sobre la cara del manguito, con borde (*brim*). |
| 10 | Bancada del 28BYJ-48 | Boca abajo (placa del motor sobre la cama). |
| 07 | Reserva con techo, separadores y barredor | Boca abajo (borde superior sobre la cama), separadores hacia arriba. |
| 21 | Tapa cuadrada | Boca abajo (la cara de arriba sobre la cama). |

## Tornillería

| Elemento | Cant. | Ubicación |
|---|---|---|
| M3×30 cabeza botón | 6 | 4 reserva/placa/columnas; 2 mordaza 13 desde abajo de la carcasa |
| M3×12 cabeza botón | 7 | 4 bancada al piso; 3 cono al rotor |
| M3×8 cabeza botón | 2 | Orejas del motor 28BYJ-48 a la bancada |
| Prisionero M3×8 | 1 | Cubo del rotor, contra el plano del eje |
| Prisionero M3×10 | 1 | Bandeja 16 |
| Tuerca M3 (5.5 entre caras × 2.4) | 18 | |

Además: motor **28BYJ-48 + placa ULN2003**, **ESP32 DevKit**, **pulsador de panel de 12 mm** normalmente abierto, fuente de **5 V ≥ 1 A** y zumbador activo opcional. Conexiones y firmware en [`Firmware_ESP32/LEEME_FIRMWARE.md`](../Firmware_ESP32/LEEME_FIRMWARE.md).

## Armado

**El orden cambió:** el bloque de pesaje se monta **antes** que la bancada del motor, porque el bolsillo de la bandeja tiene que pasar por la ventana.

1. **Bloque de pesaje, fuera de la caja:**
   1. Mete una tuerca M3 en la ranura del manguito de la bandeja 16.
   2. Desliza el extremo móvil de la celda dentro del manguito hasta que quede a ras del extremo y aprieta el prisionero M3×10 desde dentro de la bandeja (llave Allen de 1.5 mm).
   3. Pon dos tuercas en los hexágonos de la mordaza 13 y desliza la mordaza entre la celda y el fondo de la bandeja, sobre el extremo fijo. Las tuercas quedan atrapadas.
2. **Meter el bloque en la carcasa:**
   1. Bájalo por arriba unos 2 cm más atrás de su sitio, para que el bolsillo pase por dentro de la pared.
   2. A la altura de la ventana, empújalo hacia el frente hasta que el bolsillo salga por la ventana y la celda apoye en el pedestal.
   3. Voltea la caja y aprieta los 2 M3×30 desde abajo.
3. **Motor:** baja la bancada 10 y fíjala al piso con 4 M3×12 desde abajo. Mete dos tuercas en los hexágonos de debajo de su placa, baja el 28BYJ-48 por el agujero (eje arriba, caja de cables hacia atrás) y atorníllalo por sus orejas con 2 M3×8.
4. **Botón y electrónica:** mete el botón de 12 mm en el agujero frontal y apriétalo con su tuerca por dentro. Pon la placa ULN2003 en el piso, a la izquierda de la bancada, y el ESP32 en la plataforma de la derecha. Cablea según el LEEME del firmware.
5. **Comprueba que la bandeja cuelga libre:** debe tener holgura visible con el tope, la mordaza, la bancada y los bordes de la ventana.
6. Pon la placa 02 (con su canal) y el conjunto rotor + cono: cono y rotor con 3 M3×12. El agujero en doble D solo entra con los planos del eje alineados; aprieta el prisionero M3×8 contra un plano.
7. Baja la reserva 07 sobre la placa girándola hasta que su poste entre en el agujero de la placa (solo entra en una posición). Así el techo queda encima de la salida y el barredor justo antes. Ciérralo todo con los 4 M3×30 y gira el disco a mano: las cavidades deben pasar bajo el barredor y el techo sin rozar.
8. Baja la tapa cuadrada 21 por encima de la reserva hasta que la ceja entre en la boca y las pestañas en la carcasa.

## Verificación (solo geometría)

`Codigo_CAD/validar_v4.py` comprobó lo siguiente (resultado en `Verificacion_CAD_y_STL.json`):

- No hay choques entre piezas, referencias (motor 28BYJ-48, botón, ULN2003, ESP32, celda) y tornillería con volumen mayor de 0.001 mm³.
- El motor queda a 0.7 mm del rotor en todo el giro; el cubo con agujero en doble D no toca el eje.
- El barrido completo del rotor y el cono no choca con nada. La holgura mínima es 0.20 mm, igual que en V3.
- Las holguras de la bandeja: 0.45 mm al tope de sobrecarga y a la mordaza, más de 2 mm a la bancada y a los bordes de la ventana.
- El canal queda 10 mm por encima de la rampa.
- El techo de la reserva queda a 0.4 mm del disco (igual que el aro de V3) y el barredor a 0.6 mm.
- La tapa cuadrada queda a 0.5 mm de la placa y a 0.3 mm de la reserva.
- Una pastilla acostada de 15×8×6 cae por el canal, se apoya en la rampa y baja libre hasta el bolsillo exterior.
- Los 9 STL son mallas cerradas, con orientación coherente y el mismo volumen y envolvente que el CAD.
- El bloque celda + mordaza + bandeja entra por arriba y por la ventana sin chocar, y después la bancada baja sin tocar la bandeja.

**Sin probar:** alimentación con carga, fricción y calibración de la celda real. El barredor es rígido: si una pastilla medio metida en su cavidad se atasca contra él, sube `SWEEP_Z` en el generador (más holgura) o vuelve al peine de TPU de la versión anterior (está en el historial de git). Los 25° de la rampa son una estimación para PLA contra un comprimido recubierto: si la pastilla no resbala, sube `SLOPE` en el generador. La celda 50×15×7 sigue siendo una referencia nominal. Las medidas del 28BYJ-48 son las de su hoja de datos estándar. Confirma tu celda y tu motor antes de imprimir la bandeja, la mordaza y la bancada.

## Regenerar

```
cd Codigo_CAD
pip install -r requirements.txt
python generar_pastillero_v4.py   # crea STL/, STEP_piezas/ y los json
python validar_v4.py              # choques, rotor, pastilla, montaje y mallas
python armar_placas.py            # placas de 255x255 en ../Impresion_255x255
python generar_guia_ensamble.py   # guía animada y simulación del botón en ../Guia_visual
```

Todo lo que necesitan los scripts está dentro de `Pastillero_V4/`; las piezas de V3 que se reutilizan están en `Codigo_CAD/fuentes_V3/`.
