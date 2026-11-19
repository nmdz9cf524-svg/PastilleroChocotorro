"""Pastillero V4. Unidades mm. Parte de los STEP de V3 y aplica los cambios de V4.

Cambios respecto a V3:
  01  Carcasa con patas integradas (base nervada), pedestal de celda integrado y
      reforzado, tope de sobrecarga bajo el extremo móvil, plataforma electrónica
      integrada y paso de cable trasero. Sustituye a 01, 12, 18 y 19.
  02  Placa inferior con el canal de descarga integrado. Sustituye a 02 y 17.
  04  Aro con techo y los cuatro separadores integrados. Sustituye a 04 y 05.
  16  Bandeja de pesaje de una pieza con manguito para la celda y un prisionero.
      Sustituye a 14, 15 y 16.
  21  Embellecedor nuevo entre la carcasa y la reserva (versión corta y alta).

Uso: python generar_pastillero_v4.py [directorio_salida]
Requiere Python 3.12, CadQuery 2.7 y la carpeta Pastillero_V3 junto a Pastillero_V4.
"""
import cadquery as cq, pathlib, json, sys

ROOT = pathlib.Path(__file__).resolve().parent
V3 = ROOT.parents[1] / 'Pastillero_V3' / 'STEP_piezas'
OUT = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT.parent
OUT.mkdir(parents=True, exist_ok=True)
V = cq.Vector
C = 39.244  # posición de columnas / tornillos M3x30


def v3(name):
    return cq.importers.importStep(str(V3 / (name + '.step'))).val()


def box(x0, x1, y0, y1, z0, z1):
    return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def cyl(r, h, x=0, y=0, z=0):
    return cq.Solid.makeCylinder(r, h, V(x, y, z))


def rrect(w, r, z0, h, inset=0.0):
    """Rectángulo redondeado centrado (lado w, radio r) reducido 'inset' por lado."""
    w2 = w - 2 * inset
    r2 = max(r - inset, 0.3)
    return (cq.Workplane('XY', origin=(0, 0, z0)).rect(w2, w2)
            .extrude(h).edges('|Z').fillet(r2).val())


def hexprism(x, y, z, h, d=6.7):
    return cq.Workplane('XY', origin=(x, y, z)).polygon(6, d).extrude(h).val()


parts, notes = {}, {}


def add(n, s, note):
    s = s.clean()
    assert s.isValid() and len(s.Solids()) == 1, (n, len(s.Solids()))
    parts[n] = s
    notes[n] = note


# ---------------------------------------------------------------- 01 carcasa
W, RC, WALL = 125.0, 8.0, 3.0          # carcasa V3: 125x125, radio 8, pared 3
FEET_H = 3.0                           # misma altura que las patas 19 de V3
car = v3('01_carcasa_con_columnas')

# Patas integradas: base nervada bajo el piso (z -3..0). Las celdas de 27.6 mm
# se imprimen como puentes cortos, sin soportes, y alojan las cabezas de los
# cuatro tornillos de la bancada del motor.
base = rrect(W, RC, -FEET_H, FEET_H).cut(rrect(W, RC, -FEET_H - 1, FEET_H + 2, inset=WALL))
RIB = 2.4
for p in (-32.0, 0.0, 32.0):
    base = base.fuse(box(p - RIB / 2, p + RIB / 2, -60, 60, -FEET_H, 0))
    base = base.fuse(box(-60, 60, p - RIB / 2, p + RIB / 2, -FEET_H, 0))
for sx in (-1, 1):                     # zapatas macizas en las esquinas
    for sy in (-1, 1):
        x0, y0 = sx * 46.0, sy * 46.0
        base = base.fuse(box(min(x0, sx * 61), max(x0, sx * 61),
                             min(y0, sy * 61), max(y0, sy * 61), -FEET_H, 0))
base = base.intersect(rrect(W, RC, -FEET_H, FEET_H))
car = car.fuse(base)

# Tapar agujeros del piso que ya no llevan tornillo (pedestal y electrónica).
for x, y in [(-18.5, -51), (-18.5, -27), (27.5, -29.5), (55.5, -29.5),
             (27.5, 29.5), (55.5, 29.5)]:
    car = car.fuse(cyl(1.8, 4.0, x, y, 0))

# Pedestal fijo de la celda integrado: más ancho, unido al piso y a la pared
# frontal, con contrafuerte. Mantiene la cara de apoyo de V3 (z=24).
# Los dos M3x30 de la mordaza 13 entran DESDE ABAJO de la carcasa (cabeza
# alojada en el piso) y roscan en tuercas atrapadas en la mordaza 13. Así la
# celda, la mordaza y la bandeja se arman fuera y se bajan como un bloque.
ped = box(-25, -12, -60.0, -23, 4, 24)
ped = ped.fuse(cq.Workplane('XZ', origin=(0, -23, 0))
               .polyline([(-25, 4), (-33, 4), (-25, 14)]).close()
               .extrude(37.0).val())          # XZ extruye hacia -Y
car = car.fuse(ped)
for y in (-51, -27):
    car = car.cut(cyl(1.7, 30, -18.5, y, -1))                     # paso M3
    car = car.cut(cyl(3.2, 7.1, -18.5, y, -3.1))                  # cabeza

# Segundo apoyo = tope de sobrecarga bajo el extremo móvil. La bandeja queda
# libre 0.45 mm por encima; solo toca si la celda se sobrecarga o se golpea.
STOP_TOP = 21.35
car = car.fuse(box(12, 23, -46, -32, 4, STOP_TOP))

# Plataforma electrónica integrada (geometría de la pieza 18 sin tornillos).
plat = box(24, 59, -32.5, 32.5, 8, 11)
for x, y in [(32, -18), (51, -18), (32, 18), (51, 18)]:
    plat = plat.cut(box(x - 4, x + 4, y - 1, y + 1, 7, 12))        # bridas
for x in (27.5, 55.5):
    for y in (-29.5, 29.5):
        plat = plat.fuse(box(x - 3, x + 3, y - 3, y + 3, 4, 8))     # patas
car = car.fuse(plat)

# Paso de cable en la pared derecha (+X), sobre la plataforma.
car = car.cut(cq.Workplane('YZ', origin=(56, 0, 17)).slot2D(14, 8)
              .extrude(10).val())

add('01_carcasa_v4_patas_pedestal_integrados', car,
    'Carcasa V3 + patas nervadas, pedestal de celda reforzado, tope de '
    'sobrecarga, plataforma electrónica y paso de cable. Sustituye 01, 12, 18, 19.')

# --------------------------------------------------- 02 placa + canal integrado
plate = cyl(60, 4, z=89)
plate = plate.cut(cq.Workplane('XY', origin=(0, -40, 88)).slot2D(16.8, 9.6, angle=90)
                  .extrude(6).val())
plate = plate.cut(cyl(10.5, 6, z=88))
for x in (-C, C):
    for y in (-C, C):
        plate = plate.cut(cyl(1.7, 6, x, y, 88))
canal = v3('17_canal_descarga')
# Ceja superior del canal: localizar su cara inferior para rellenar los pasos
# y avellanados de los dos M3x8 que ya no hacen falta.
zf = 89.0
for i in range(400):
    z = 89.0 - 0.05 * (i + 1)
    a = sum(f.Area() for f in canal.intersect(box(-30, 30, -70, 0, z, z + 0.01)).Faces()
            if f.normalAt().z > 0.9)
    if a < 500:
        break
    zf = z
for x in (-14, 14):
    canal = canal.fuse(cyl(3.2, 89 - zf, x, -40, zf))
add('02_placa_inferior_con_canal', plate.fuse(canal),
    'Placa inferior V3 con el canal 17 integrado (sin M3x8 ni tuercas). '
    'Imprimir con la cara superior de la placa sobre la cama.')

# ------------------------------------------------------ 04 aro + separadores
aro = v3('04_aro_con_techo_descarga')
sep = v3('05_separador_placas_x4')      # en (C, C)
for x in (-C, C):
    for y in (-C, C):
        aro = aro.fuse(sep.translate((x - C, y - C, 0)))
add('04_aro_con_techo_y_separadores', aro,
    'Aro con techo V3 con los cuatro separadores integrados. Imprimir boca abajo.')

# ------------------------------------------------- 16 bandeja de una pieza
# Celda (referencia) 50x15x7: x -25..25, y -46.5..-31.5, z 24..31. Extremo
# móvil en +X. La bandeja abraza el extremo con un manguito y se fija con un
# prisionero M3x6 que se aprieta desde dentro de la bandeja.
CL = 0.2
TX0, TX1 = -22.5, 27.0                  # bandeja
TY0, TY1 = -56.5, -21.5
TZ0, TZ1, FLOOR, TW = 35.0, 47.0, 2.0, 2.0
tray = box(TX0, TX1, TY0, TY1, TZ0, TZ1)
inner = (cq.Workplane('XY', origin=((TX0 + TX1) / 2, (TY0 + TY1) / 2, TZ0 + FLOOR))
         .rect(TX1 - TX0 - 2 * TW, TY1 - TY0 - 2 * TW).extrude(TZ1).edges('|Z').fillet(4).val())
tray = tray.cut(inner)
SZ0 = 24 - CL - 2.0                     # fondo del manguito (21.8)
sleeve = box(10, TX1, -46.5 - CL - 3, -31.5 + CL + 3, SZ0, TZ0 + 0.01)
sleeve = sleeve.cut(box(9, 25 + 0.3, -46.5 - CL, -31.5 + CL, 24 - CL, 31 + CL))
tray = tray.fuse(sleeve)
GX, GY = 18.0, -39.0
tray = tray.cut(cyl(1.7, 20, GX, GY, 30))                         # prisionero
tray = tray.cut(hexprism(GX, GY, 32.0, 2.6))                       # tuerca
tray = tray.cut(box(GX, TX1 + 1, GY - 2.95, GY + 2.95, 32.0, 34.6))  # ranura
add('16_bandeja_pesaje_una_pieza', tray,
    'Sustituye 14, 15 y 16. Manguito para el extremo móvil de la celda y un '
    'prisionero M3x6 con tuerca. Imprimir de pie sobre la cara +X.')

# ------------------------------------------- 13 mordaza fija con tuercas
# Misma envolvente que V3 (13x32x3.5). Tuercas M3 en alojamientos hexagonales
# por arriba: quedan atrapadas bajo la bandeja y no se caen al montar.
mor = box(-25, -12, -55, -23, 31, 34.5)
for y in (-51, -27):
    mor = mor.cut(cyl(1.7, 6, -18.5, y, 30)).cut(hexprism(-18.5, y, 31.9, 3))
add('13_mordaza_fija_celda_tuercas', mor,
    'Mordaza superior del extremo fijo. Dos tuercas M3 en su cara superior; '
    'los M3x30 entran desde debajo de la carcasa.')

# ------------------------------------------------------- 21 embellecedor
# Cubre la franja entre la carcasa (z=89) y la reserva: placa, rotor, aro,
# separadores y tornillos M3x30. Pared flush con la carcasa; cuatro pestañas
# de esquina entran 6 mm dentro de la carcasa para centrarlo. Se coloca
# bajándolo por encima de la reserva, sin herramientas.
R_RES = 52.0
def embellecedor(top):
    e = rrect(W, RC, 89, top - 89).cut(rrect(W, RC, 88, top - 89 + 2, inset=2.0))
    deck = rrect(W, RC, top - 2.0, 2.0).cut(cyl(R_RES + 0.5, 4, z=top - 3))
    e = e.fuse(deck)
    tabs = rrect(W, RC, 83, 6.01, inset=WALL + 0.25).cut(
        rrect(W, RC, 82, 8, inset=WALL + 0.25 + 1.6))
    keep = None
    for sx in (-1, 1):
        for sy in (-1, 1):
            b = box(min(sx * 42, sx * 70), max(sx * 42, sx * 70),
                    min(sy * 42, sy * 70), max(sy * 42, sy * 70), 82, 90)
            keep = b if keep is None else keep.fuse(b)
    # Ménsula que une cada pestaña con la pared (solo en las esquinas, fuera
    # del radio 60 de placa, aro y reserva).
    ledge = rrect(W, RC, 89, 2.0).cut(rrect(W, RC, 88, 4, inset=WALL + 0.25 + 1.6))
    return e.fuse(tabs.fuse(ledge).intersect(keep))

add('21a_embellecedor_corto', embellecedor(114.0),
    'Tapa la franja del mecanismo hasta z=114, sobre las cabezas M3x30. '
    'Imprimir boca abajo.')
add('21b_embellecedor_alto', embellecedor(166.8),
    'Versión alta: cubre también la reserva y queda a ras de su borde '
    '(la tapa 09 sigue accesible). Imprimir boca abajo.')

# ------------------------------------------------ piezas V3 sin cambios
UNCHANGED = ['03_rotor_15x8_con_cubo', '06_cono_repartidor_punta_arriba',
             '07_reserva_centrada', '09_tapa_reserva_centrada',
             '10_bancada_motor_32x25', '11_puente_motor',
             '20_peine_flexible_TPU']
for n in UNCHANGED:
    add(n, v3(n), 'Sin cambios respecto a V3.')

# ------------------------------------------------------------- exportación
# Orientación de impresión de cada STL (los STEP quedan en coordenadas de ensamble).
FLIP_X = {'02_', '03_', '04_', '21a', '21b'}
for d in ['STL', 'STEP_piezas', 'Referencias_NO_imprimir']:
    (OUT / d).mkdir(exist_ok=True)
for n, s in sorted(parts.items()):
    q = s
    if n[:3] in FLIP_X:
        q = s.rotate((0, 0, 0), (1, 0, 0), 180)
    elif n.startswith('16_'):
        q = s.rotate((0, 0, 0), (0, 1, 0), 90)          # cara +X sobre la cama
    elif n.startswith('20_'):
        q = s.rotate((0, 0, 0), (0, 0, 1), -235).rotate((0, 0, 0), (1, 0, 0), 90)
    b = q.BoundingBox()
    q = q.translate((-(b.xmin + b.xmax) / 2, -(b.ymin + b.ymax) / 2, -b.zmin))
    cq.exporters.export(q, str(OUT / 'STL' / (n + '.stl')), tolerance=.025, angularTolerance=.08)
    cq.exporters.export(s, str(OUT / 'STEP_piezas' / (n + '.step')))
REFS = pathlib.Path(V3).parent / 'Referencias_NO_imprimir'
for n in ['REF_motor_32x25', 'REF_eje_6x35', 'REF_celda_50x15x7']:
    cq.exporters.export(cq.importers.importStep(str(REFS / (n + '.step'))).val(),
                        str(OUT / 'Referencias_NO_imprimir' / (n + '.step')))
meta = {n: {'size_mm': [round(s.BoundingBox().xlen, 3), round(s.BoundingBox().ylen, 3),
                        round(s.BoundingBox().zlen, 3)],
            'volume_mm3': round(s.Volume(), 1), 'note': notes[n]}
        for n, s in sorted(parts.items())}
json.dump(meta, open(OUT / 'Dimensiones_y_notas.json', 'w'), indent=2, ensure_ascii=False)
v3params = json.load(open(pathlib.Path(V3).parent / 'Parametros_V3.json'))
v3params.update({'version': 'V4', 'tray_grub_xy': [GX, GY], 'overload_stop_gap_mm':
                 round(SZ0 - STOP_TOP, 2), 'feet_height_mm': FEET_H})
json.dump(v3params, open(OUT / 'Parametros_V4.json', 'w'), indent=2)
print('BUILT', len(parts), 'valid unique solids', flush=True)
