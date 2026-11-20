# Impresión por placas: cama de 255 × 255 mm

Aquí están todas las piezas del Pastillero V4 agrupadas en placas listas para imprimir. Las piezas ya están giradas en su orientación de impresión y colocadas en la cama. Entre piezas hay al menos 5 mm y al borde 2.5 mm; se comprobó con la silueta real de cada una.

Con **2 placas** se imprime todo el pastillero, y todo en PLA o PETG: ya no hay piezas de TPU.

| Placa | Piezas | Material | Capa | Alto máx. |
|---|---|---|---|---|
| ![](Placa_1_estructura_PLA_capa_0.28.png) **1 · Estructura** | 01 carcasa, 07 reserva con barredor, 06 cono, 10 bancada, 16 bandeja inclinada, 11 puente, 13 mordaza | PLA / PETG | **0.28 mm** | 92 mm |
| ![](Placa_2_mecanismo_y_tapa_PLA_capa_0.20.png) **2 · Mecanismo y tapa** | 21 tapa cuadrada, 02 placa con canal, 04 aro, 03 rotor | PLA / PETG | **0.20 mm** | 87 mm |

## Archivos de cada placa

- **`.3mf`** (recomendado): cada pieza es un objeto independiente y ya está colocado. Ábrelo en Bambu Studio, OrcaSlicer, PrusaSlicer o Cura. Si el programa pregunta, elige cargar solo la geometría.
- **`.stl`**: la placa entera en un solo archivo. Si tu programa lo carga como un solo objeto, usa "Dividir en objetos" (*Split to objects*) para ajustar cada pieza.
- **`.png`**: vista superior de la distribución.
- **`Resumen_placas.json`**: lista de piezas, alto máximo y volumen sólido de cada placa.

Las piezas sueltas también están en `../STL/`, por si hay que reimprimir solo una.

## Cómo se ahorró tiempo

1. **Menos placas.** Con 2 impresiones se cubren las 11 piezas.
2. **Capa según la función.** La placa 1 lleva piezas de estructura sin holguras críticas, así que va a 0.28 mm: unas 30 % menos capas que a 0.20. El barredor de la reserva tiene 0.6 mm de holgura, suficiente para esa capa. La placa 2 lleva las piezas con holguras finas (disco, aro y placa) y la tapa, que se ve mejor a 0.20 mm.
3. **Sin cambio de material.** El barredor rígido de la reserva sustituye al peine de TPU.
4. **Sin soportes.** Todas las piezas están orientadas para imprimirse sin soportes: la carcasa sobre su base nervada; la placa 02, el aro 04, la reserva 07 y la tapa 21 boca abajo; y la bandeja 16 de pie.

## Ajustes sugeridos

- **Rígidas:** boquilla 0.4, 3 perímetros, relleno 15–20 % en gyroid o rejilla y **sin soportes**. Para la carcasa y la reserva basta con 2 perímetros si quieres ir aún más rápido.
- **Bandeja 16 (placa 1):** ponle un borde (*brim*) de 5 mm porque se imprime de pie. Las líneas de capa quedan a lo largo de la rampa y ayudan a que la pastilla resbale.
- **Antes de imprimir:** revisa en el laminador que ninguna pieza haya quedado flotando o girada. Los STL ya vienen apoyados en z = 0.

## Para regenerar las placas

```
cd ../Codigo_CAD
python armar_placas.py
```

Las posiciones están en el diccionario `PLACAS` al inicio de `armar_placas.py`. Si cambias una pieza, el script vuelve a comprobar que nada se encima y que todo cabe en 255 × 255.
