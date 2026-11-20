# Pastillero V4: dispensador con botón

Cada pulsación del botón gira el rotor 30° y deja **una pastilla** en el bolsillo de salida, fuera de la caja. V4 usa el motor **28BYJ-48 con driver ULN2003** y un **ESP32**, ya no tiene sistema de pesaje y se arma con **9 piezas impresas**. Del diseño V3 conserva el cono y la forma del techo.

> **Para imprimir, ve directo a [`Impresion_255x255/`](Impresion_255x255/LEEME_IMPRESION.md).** Son 2 placas para una cama de 255 × 255.
> **Para armar, abre la guía animada** `Guia_visual/Ensamble_Pastillero_V4.html`. **Para ver cómo funciona**, abre `Guia_visual/Simulacion_boton_V4.html`.

## Carpetas

| Carpeta | Qué contiene |
|---|---|
| `Impresion_255x255/` | **Placas listas para imprimir** (.3mf, .stl y vista previa) y la guía de impresión |
| `Guia_visual/` | **Guía animada de ensamble** (`Ensamble_Pastillero_V4.html`) y **simulación del botón** (`Simulacion_boton_V4.html`). Se abren con doble clic; necesitan internet para cargar three.js |
| `STL/` | Cada pieza suelta, ya orientada, por si hay que reimprimir una |
| `STEP_piezas/` | Piezas en coordenadas de ensamble, para editar en CAD |
| `Pastillero_V4_ensamble.step` | Ensamble completo, con tornillería y referencias |
| `Referencias_NO_imprimir/` | Motor 28BYJ-48, pulsador 6×6, ULN2003, ESP32 y tornillería. **No se imprimen.** |
| `Codigo_CAD/` | Scripts que generan, validan y arman las placas, más `fuentes_V3/` con las piezas de V3 que se reutilizan |

![Vista V4](Vista_pastillero_V4.png)

## Piezas

| N.º | Pieza | Qué hace |
|---|---|---|
| 01 | **Carcasa** | Las patas vienen impresas como una base nervada bajo el piso. Lleva la plataforma del ESP32, el paso de cable de la pared derecha, y dos ranuras en el piso para la rampa. El frente queda limpio: el botón va arriba, en la tapa de servicio. |
| 02 | **Placa inferior con canal** | El canal va integrado y baja hasta 10 mm sobre la rampa, con la boca cortada en diagonal, para guiar la caída. El agujero pequeño de arriba recibe el poste de la reserva. |
| 03 | **Rotor** | 12 cavidades, una cada 30°. Disco de Ø103.6 × 7.6 mm (con asiento para el cono), con holgura de giro amplia. El cubo tiene agujero en doble D para el eje Ø5 del 28BYJ-48 y un prisionero M3×8. |
| 06 | **Cono** | Igual que en V3. |
| 07 | **Reserva** | Una sola pieza con el techo sobre la salida (así no caen pastillas de golpe), los cuatro separadores del disco y un barredor rígido justo antes del techo. Un poste entra en la placa 02, así que solo se monta en la posición correcta. |
| 09 | **Tapa de llenado** | Disco redondo que encaja a ras en la tapa de servicio. Se levanta por la muesca del frente y se echan las pastillas por la boca de Ø91, directo a la reserva. |
| 10 | **Bancada del 28BYJ-48** | Deja el eje del motor justo bajo el centro del rotor. El motor se atornilla por sus orejas. |
| 16 | **Rampa de salida** | Fondo a 25°. El bolsillo mide 30 mm y sale **29.5 mm** de la caja: caben varias pastillas y se toman con los dedos. No tiene tornillos: apoya en el borde inferior de la ventana y en dos nervios encajados en el piso. |
| 21 | **Tapa de servicio** | Caja cuadrada a ras de la carcasa. Cubre placa, disco y reserva y se levanta entera para mantenimiento. Su ceja circular entra en la reserva y sus pestañas en la carcasa. En su esquina frontal derecha lleva el **pulsador de entrega**: un táctil de 6×6 alojado por debajo, con el vástago asomando 2 mm por un agujero con rebaje para el dedo. |

**La caja se abre en dos secciones:** la tapa redonda 09 para llenar y la cuadrada 21 para mantenimiento.

## Qué cambió respecto a V3

| V3 | V4 |
|---|---|
| 19 patas pegadas | Integradas en la carcasa 01 |
| 12 pedestal, 13 y 14 mordazas, 15 apoyo, 16 bandeja de pesaje, celda de carga | **Eliminados.** El pesaje ya no tenía función; la bandeja es ahora la rampa fija 16 |
| 18 plataforma electrónica | Integrada en la carcasa 01 |
| 17 canal (2 M3×8) | Integrado y prolongado en la placa 02 |
| 04 aro, 05 separadores ×4, 20 peine TPU | Integrados en la reserva 07 (barredor rígido en lugar del peine) |
| 09 tapa redonda | 09 tapa de llenado, encajada en la tapa de servicio 21 |
| 10 bancada + 11 puente (motor Ø32) | 10 bancada para 28BYJ-48 |
| 03 rotor (eje Ø6) | 03 rotor para eje D5 |
| Firmware con horarios y WiFi | Firmware solo con botón |

Balance: de **25 piezas impresas → 9**, de **29 tornillos/prisioneros → 14** y de **29 tuercas → 15**. Sin filamento flexible.

## Tornillería y componentes

| Elemento | Cant. | Ubicación |
|---|---|---|
| M3×30 cabeza botón | 4 | Reserva, placa y columnas |
| M3×12 cabeza botón | 7 | 4 bancada al piso; 3 cono al rotor |
| M3×8 cabeza botón | 2 | Orejas del motor a la bancada |
| Prisionero M3×8 | 1 | Cubo del rotor, contra el plano del eje |
| Tuerca M3 (5.5 entre caras × 2.4) | 15 | |

Además: motor **28BYJ-48 + placa ULN2003**, **ESP32 DevKit**, **pulsador táctil de 6×6×9.5 mm** (el común de 4 patas) con un **conector de 2 pines**, fuente de **5 V ≥ 1 A** y zumbador activo opcional. Las conexiones y el firmware están en [`Firmware_ESP32/LEEME_FIRMWARE.md`](../Firmware_ESP32/LEEME_FIRMWARE.md).

## Armado

1. **Rampa (antes que la bancada):**
   1. Bájala por arriba unos 3.5 cm más atrás de su sitio, para que el bolsillo pase por dentro de la pared.
   2. Cerca del piso, empújala hacia el frente hasta que el bolsillo salga por la ventana.
   3. Bájala los últimos 2 mm: los nervios entran en las ranuras del piso y el bolsillo apoya en la ventana.
2. **Bancada y motor:**
   1. Fija la bancada 10 al piso con 4 M3×12 desde abajo.
   2. Mete dos tuercas en los hexágonos de debajo de su placa.
   3. Baja el 28BYJ-48 con el eje arriba y la caja de cables hacia atrás.
   4. Atorníllalo por sus orejas con 2 M3×8.
3. **Electrónica:**
   1. Pon la placa ULN2003 en el piso, a la izquierda de la bancada.
   2. Pon el ESP32 en la plataforma de la derecha.
   3. Cablea según el LEEME del firmware. Deja un cable de 2 hilos con conector para el pulsador (GPIO23 y GND).
4. **Placa y rotor:**
   1. Asienta la placa 02 sobre las columnas.
   2. Une cono y rotor con 3 M3×12 y bájalos sobre el eje. El agujero en doble D solo entra alineado con los planos del eje.
   3. Pon debajo del disco un calce de 0.6 mm (6 hojas de papel de impresora o una tarjeta de plástico), apóyalo y aprieta el prisionero M3×8. Quita el calce: el disco queda centrado en altura, con 0.6 mm a la placa y 0.6 mm al techo.
5. **Reserva:**
   1. Bájala girándola hasta que su poste entre en la placa.
   2. Cierra con los 4 M3×30.
   3. Gira el disco a mano: debe pasar libre bajo el barredor y el techo.
6. **Tapas y pulsador:**
   1. Mete el pulsador 6×6 por debajo de la tapa de servicio 21, en su alojamiento de la esquina, y fíjalo con una gota de pegamento.
   2. Conéctalo al conector de 2 pines.
   3. Baja la tapa de servicio.
   4. Pon la tapa de llenado 09 en su asiento.

## Revisión de coherencia con lo pedido

| Pedido | Cómo se cumple | Comprobado con |
|---|---|---|
| Botón que entregue una pastilla al momento | Pulsador en GPIO23; el firmware gira al detectar la pulsación, sin esperar a soltar. Un doble toque, pulsar mientras gira o mantener pulsado no dan pastillas de más | `Firmware_ESP32/prueba_logica`: 10 casos con rebote simulado, TODO OK |
| 30° por pulsación, una sola pastilla | 12 cavidades a 30°. Cada pulsación da 339 o 340 medios pasos y el objetivo se calcula desde el arranque, así que no hay deriva. El techo tapa toda la ventana de salida, así que no cae una segunda pastilla desde la reserva | 12 pulsaciones = 1 vuelta y error de 0.02° tras 1000 vueltas; ventana descubierta 0 mm³ |
| Motor 28BYJ-48 | Bancada con el eje descentrado bajo el centro del rotor; rotor con agujero en doble D | Sin choques; motor a 0.7 mm del rotor |
| Sin sistema de peso | Se eliminaron celda, mordaza, pedestal, tope y manguito | Ninguna pieza ni tornillo los menciona |
| Rampa más larga, pastilla fácil de sacar | El bolsillo sale 29.5 mm de la caja y mide 30 mm; la pastilla queda entera fuera | Trayectoria de la pastilla sin choques hasta el bolsillo |
| Tapa en dos secciones | Tapa de llenado 09 a ras sobre la tapa de servicio 21 | Encaje a ras: 0.0 mm de desnivel y contacto 0.0 mm |
| Botón arriba y pequeño | Pulsador táctil 6×6 en la esquina frontal derecha de la tapa de servicio; asoma 2 mm sobre un rebaje para el dedo | Apoya en la tapa (contacto 0.0 mm), sin choques; queda a más de 8 mm de la reserva y de la tapa de llenado |
| Ninguna pieza flotando | Cada pieza apoya en otra y todas llegan hasta la carcasa. La rampa apoya en la ventana y en el piso, la tapa de llenado y el pulsador en la tapa de servicio, el motor en la bancada y el rotor en el eje por su prisionero | Comprobación de contactos en `validar_v4.py` (`supports` en el JSON) |

## Verificación (solo geometría)

`Codigo_CAD/validar_v4.py` comprobó lo siguiente (resultado en `Verificacion_CAD_y_STL.json`):

- No hay choques entre piezas, referencias (motor, pulsador, ULN2003, ESP32) y tornillería con volumen mayor de 0.001 mm³.
- El barrido completo del rotor y el cono no choca con nada. **Todas las holguras de giro son de al menos 0.6 mm**, pensadas para impresión FDM (±0.2 mm por pieza):

  | Entre | Holgura |
  |---|---|
  | Borde del disco y separadores de la reserva | 1.0 mm |
  | Disco y placa (abajo) | 0.6 mm |
  | Disco y techo (arriba) | 0.6 mm |
  | Cubo y agujero de la placa | 1.5 mm |
  | Cono y borde del techo | 0.68 mm |
  | Motor y rotor | 0.7 mm |
- El techo de la reserva tapa entera la ventana de salida. El barredor queda a 0.8 mm del disco.
- Una pastilla acostada de 15×8×6 cae por el canal, se apoya en la rampa y queda entera en el bolsillo exterior.
- La rampa entra por arriba y por la ventana sin chocar, y después la bancada baja sin tocarla (0.5 mm).
- **Ninguna pieza flota:** todas apoyan en otra y llegan hasta la carcasa.
- Los 9 STL son mallas cerradas, con orientación coherente y el mismo volumen y envolvente que el CAD.

**Sin probar:**
- **Comportamiento real:** la alimentación con carga y la fricción.
- **Barredor:** es rígido. Si una pastilla medio metida en su cavidad se atasca contra él, sube `SWEEP_Z` en el generador para darle más holgura.
- **Rampa:** los 25° son una estimación para PLA contra un comprimido recubierto. Si la pastilla no resbala, sube `SLOPE`.
- **Motor:** las medidas del 28BYJ-48 son las de su hoja de datos estándar. Confirma las de tu motor antes de imprimir la bancada.

## Regenerar

```
cd Codigo_CAD
pip install -r requirements.txt
python generar_pastillero_v4.py   # crea STL/, STEP_piezas/ y los json
python validar_v4.py              # choques, rotor, pastilla, montaje, piezas flotantes y mallas
python armar_placas.py            # placas de 255x255 en ../Impresion_255x255
python generar_guia_ensamble.py   # guía animada y simulación del botón en ../Guia_visual
```

Todo lo que necesitan los scripts está dentro de `Pastillero_V4/`; las piezas de V3 que se reutilizan están en `Codigo_CAD/fuentes_V3/`.
