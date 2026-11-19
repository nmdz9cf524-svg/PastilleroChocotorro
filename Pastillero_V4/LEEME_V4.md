# Pastillero V4: piezas simplificadas

V4 parte de V3. El mecanismo de dosificación no cambia: rotor, cono, peine, techo, reserva y tapa son los mismos. Lo que cambia es la carcasa, la zona de la celda de carga y el número de piezas sueltas. Además se agrega un embellecedor.

![Vista V4](Vista_pastillero_V4.png)

## Qué cambió y por qué

| V3 | V4 | Motivo |
|---|---|---|
| 01 carcasa + 19 patas ×4 (pegadas) | **01 carcasa** con patas integradas | Las patas forman ahora una base nervada de 3 mm bajo el piso. Las celdas son de unos 28 mm, así que el piso se imprime como puentes cortos, sin soportes. Las cabezas de los tornillos quedan dentro de las celdas. |
| 12 pedestal (2 M3 al piso, se caía) | Pedestal **integrado en 01** | Va unido al piso y a la pared frontal y lleva un contrafuerte, así que ya no se puede caer. |
| no existía | **Segundo apoyo = tope de sobrecarga** integrado en 01 | Está debajo del extremo móvil de la celda, con 0.45 mm de holgura. No toca en uso normal: solo frena la bandeja si se aprieta o se golpea, para que la celda no se doble ni se suelte. (La celda tiene que quedar en voladizo para medir, por eso el segundo apoyo no la sujeta.) |
| 18 plataforma electrónica (4 M3) | Plataforma **integrada en 01** | Se conservan las ranuras para bridas y se agrega un paso de cable de 14×8 mm en la pared +X. |
| 13 mordaza (M3×16 desde arriba) | **13 mordaza con tuercas** | Los dos M3×30 entran **desde debajo de la carcasa**, con la cabeza alojada en el piso, y roscan en tuercas atrapadas en la 13. |
| 14 + 15 + 16 (3 piezas, 2 M3×20) | **16 bandeja de una pieza** | Un manguito abraza el extremo móvil de la celda y se fija con 1 prisionero M3×6 que se aprieta desde dentro de la bandeja. |
| 02 placa + 17 canal (2 M3×8) | **02 placa con canal** | Se imprime con la cara superior de la placa sobre la cama, así queda lisa para el disco. |
| 04 aro + 05 separadores ×4 | **04 aro con separadores** | Se imprime boca abajo. Los separadores quedan alineados. |
| no existía | **21 embellecedor** (corto o alto) | Tapa la franja entre la carcasa y la reserva (placa, disco, aro y tornillos M3×30). Queda a ras de la carcasa, se centra con 4 pestañas en las esquinas y se coloca bajándolo por encima de la reserva, sin herramientas. Elige **una** versión: **21a corto** (hasta z=114) o **21b alto** (cubre también la reserva y queda a ras de su borde, con la tapa 09 accesible). |

Balance: de **25 piezas impresas → 13**, de **29 tornillos/prisioneros → 20** y de **29 tuercas → 20**.

## Piezas a imprimir (carpeta `STL/`)

Los STL ya están orientados para imprimir. Los STEP de `STEP_piezas/` mantienen las coordenadas de ensamble.

| N.º | Pieza | Cant. | Alto de impresión | Orientación / nota |
|---|---|---|---|---|
| 01 | Carcasa con patas, pedestal, tope y plataforma | 1 | 92 mm | Base nervada sobre la cama. Cama ≥ 140×140. |
| 02 | Placa inferior con canal | 1 | 43 mm | Placa abajo, canal hacia arriba. |
| 03 | Rotor 15×8 con cubo | 1 | 21.4 mm | Igual que V3. |
| 04 | Aro con techo y separadores | 1 | 12.8 mm | Boca abajo, separadores hacia arriba. |
| 06 | Cono repartidor | 1 | 35 mm | Igual que V3. |
| 07 | Reserva centrada | 1 | 61 mm | Igual que V3. |
| 09 | Tapa de reserva | 1 | 15 mm | Igual que V3. |
| 10 | Bancada del motor | 1 | 65 mm | Igual que V3 (ver nota del motor). |
| 11 | Puente del motor | 1 | 4 mm | Igual que V3. |
| 13 | Mordaza fija con tuercas | 1 | 3.5 mm | Alojamientos hexagonales hacia arriba. |
| 16 | Bandeja de pesaje de una pieza | 1 | 49.5 mm | De pie sobre la cara del manguito. Usa borde (brim). |
| 20 | Peine flexible **TPU 95A** | 1 | 8 mm | Igual que V3. |
| 21a **o** 21b | Embellecedor corto **o** alto | 1 | 31 / 84 mm | Boca abajo (la cubierta sobre la cama). |

## Tornillería

| Elemento | Cant. | Ubicación |
|---|---|---|
| M3×30 cabeza botón | 6 | 4 reserva/aro/placa/columnas; 2 mordaza 13 desde abajo de la carcasa |
| M3×12 cabeza botón | 9 | 4 bancada al piso; 2 puente motor; 3 cono al rotor |
| M3×8 cabeza botón | 2 | Peine flexible |
| Prisionero M3×6 | 3 | 2 cubo del rotor; 1 bandeja |
| Tuerca M3 (5.5 entre caras × 2.4) | 20 | |

## Armado

1. **Motor:** fija la bancada 10 al piso con 4 M3×12 desde abajo; las cabezas quedan dentro de las celdas de la base. Coloca el motor y el puente 11.
2. **Bloque de pesaje, fuera de la caja:**
   1. Mete una tuerca en la ranura lateral del manguito de la bandeja 16.
   2. Desliza el extremo móvil de la celda dentro del manguito hasta el tope y aprieta el prisionero M3×6 desde dentro de la bandeja (llave Allen de 1.5 mm).
   3. Pon dos tuercas en los hexágonos de la mordaza 13 y desliza la mordaza entre la celda y el fondo de la bandeja, sobre el extremo fijo. Las tuercas quedan atrapadas y no se caen.
3. Baja el bloque celda + mordaza + bandeja dentro de la carcasa hasta apoyar el extremo fijo en el pedestal. Voltea la caja y aprieta los 2 M3×30 desde abajo. Comprueba que la bandeja no toque nada: el tope, la mordaza y la bancada deben tener holgura visible.
4. Pon la placa 02 (con su canal) y el conjunto rotor + cono, igual que en V3: cono y rotor con 3 M3×12, prisioneros al eje.
5. Monta el peine 20 sobre el aro 04 (2 M3×8). Coloca el aro, cuyos separadores ya vienen integrados, la reserva 07 y los 4 M3×30.
6. Baja el embellecedor 21 por encima de la reserva hasta que las pestañas entren en la carcasa. Pon la tapa 09.

## Verificación (solo geometría)

`Codigo_CAD/validar_v4.py` comprobó lo siguiente (resultado en `Verificacion_CAD_y_STL.json`):

- No hay choques entre piezas, referencias (motor, eje, celda) y tornillería con volumen mayor de 0.001 mm³, incluidas las dos variantes del embellecedor.
- El barrido completo del rotor y el cono no choca con nada. La holgura mínima es 0.20 mm, igual que en V3.
- Las holguras de la bandeja: 0.45 mm al tope de sobrecarga, 0.5 mm a la mordaza y a la bancada.
- El embellecedor queda a 0.5 mm de la placa, el aro y la reserva, y a 0.55 mm de las cabezas M3×30.
- Una pastilla acostada de 15×8×6 baja libre desde la cavidad hasta el fondo de la bandeja.
- Los 14 STL son mallas cerradas, con orientación coherente y el mismo volumen y envolvente que el CAD.
- El bloque celda + mordaza + bandeja se puede bajar en vertical con el motor ya montado.

**Sin probar:** alimentación con carga, fricción, comportamiento del peine y calibración de la celda real. La celda 50×15×7 y el motor Ø32×25 siguen siendo referencias nominales. Confirma tu celda real antes de imprimir la bandeja y la mordaza.

## Pendiente conocido

La bancada 10 y el puente 11 siguen pensados para el motor nominal Ø32×25 con eje centrado. Si usas el **28BYJ-48**, hay que rediseñarlos (eje descentrado unos 8 mm), como indica `Firmware_ESP32/LEEME_FIRMWARE.md`.

## Regenerar

```
pip install -r ../Pastillero_V3/Codigo_CAD/requirements.txt
cd Codigo_CAD
python generar_pastillero_v4.py   # lee ../../Pastillero_V3/STEP_piezas
python validar_v4.py
```
