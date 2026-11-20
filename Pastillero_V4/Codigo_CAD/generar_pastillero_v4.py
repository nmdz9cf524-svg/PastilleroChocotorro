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
Requiere Python 3.12 y CadQuery 2.7. Las piezas que vienen de V3 están en fuentes_V3/.
"""
import cadquery as cq, pathlib, json, sys, math

ROOT = pathlib.Path(__file__).resolve().parent
V3 = ROOT / 'fuentes_V3'                # copia de los STEP de V3 que se reutilizan
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


def extr_yz(pts, x0, x1):
    """Perfil (y, z) extruido en X entre x0 y x1."""
    return cq.Workplane('YZ', origin=(x0, 0, 0)).polyline(pts).close().extrude(x1 - x0).val()


# Geometría de la bandeja inclinada (16), compartida con el canal de la placa 02.
SLOPE = math.tan(math.radians(25))      # fondo a 25°: la pastilla resbala sola
FLOOR, TW, WALL_H, LIP_H = 2.0, 2.0, 12.0, 6.0
TY_BACK, TY_FRONT = -21.5, -80.0        # bandeja de -21.5 a -80 (sale 17.5 mm)
Y_KNEE = -62.0                          # fin de la rampa / inicio del bolsillo
Z_REF = 37.0                            # cara superior del fondo en y=-55


def floor_top(y):
    return Z_REF + (y + 55.0) * SLOPE if y >= Y_KNEE else Z_REF + (Y_KNEE + 55.0) * SLOPE


Z_POCKET = floor_top(Y_KNEE)
CANAL_GAP = 10.0                        # hueco canal-rampa para que pase la pastilla

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
# Boca del canal recortada en paralelo a la rampa de la bandeja, con 10 mm de
# paso: la pastilla cae, resbala y sale por debajo de la pared frontal.
canal = canal.cut(extr_yz([(-70, 0), (-70, floor_top(-70) + CANAL_GAP),
                           (-15, floor_top(-15) + CANAL_GAP), (-15, 0)], -30, 30))
add('02_placa_inferior_con_canal', plate.fuse(canal),
    'Placa inferior V3 con el canal 17 integrado (sin M3x8 ni tuercas). '
    'Imprimir con la cara superior de la placa sobre la cama.')

# ------------------------------------------------------ 04 aro + separadores
aro = v3('04_aro_con_techo_descarga')
sep = v3('05_separador_placas_x4')      # en (C, C)
for x in (-C, C):
    for y in (-C, C):
        aro = aro.fuse(sep.translate((x - C, y - C, 0)))
# El peine de TPU ya no existe (barredor integrado en la reserva 07): se
# rellenan sus dos pasos y alojamientos de tuerca, solo dentro del techo.
V3P = json.load(open(V3 / 'Parametros_V3.json'))
a0, a1 = map(math.radians, V3P['roof_sector_degrees'])
roof_wedge = cq.Workplane('XY').polyline([(0, 0), (100 * math.cos(a0), 100 * math.sin(a0)),
                                          (100 * math.cos(a1), 100 * math.sin(a1))]).close().extrude(4).translate((0, 0, 101.8)).val()
roof_zone = cyl(51.8, 4, z=101.8).cut(cyl(31.2, 6, z=101)).intersect(roof_wedge)
for x, y in V3P['wiper_bolts_xy']:
    aro = aro.fuse(cyl(3.6, 4, x, y, 101.8).intersect(roof_zone))
# Agujero para el pin de la reserva: solo entra en una orientación.
PIN_XY, PIN_R = (0.0, 56.0), 1.5
aro = aro.cut(cyl(PIN_R + 0.2, 2.5, PIN_XY[0], PIN_XY[1], 105.8 - 2.4))
add('04_aro_con_techo_y_separadores', aro,
    'Aro con techo V3 con los cuatro separadores integrados y agujero del pin '
    'de orientación de la reserva. Imprimir boca abajo.')

# ---------------------------------------- 07 reserva con barredor integrado
# Reserva V3 (Ø98 interior, pestaña Ø120) + barredor rígido que sustituye al
# peine de TPU. Va justo antes del techo en el giro antihorario, a 0.6 mm del
# disco: las pastillas metidas en su cavidad pasan por debajo y las que van
# encima o tumbadas sobre el disco se empujan hacia el cono. Su cara de ataque
# está inclinada (como una cuchilla quitanieves) para empujarlas hacia dentro
# y no contra la pared.
res = cyl(52, 61, z=105.8).fuse(cyl(60, 4, z=105.8))
# Chaflán de 45° sobre la pestaña: la reserva se imprime boca abajo.
res = res.fuse(cq.Solid.makeCone(60, 52, 8, V(0, 0, 109.8)))
res = res.cut(cyl(49, 63, z=104.8))
for x in (-C, C):
    for y in (-C, C):
        res = res.cut(cyl(1.7, 8, x, y, 104)).cut(cyl(3.3, 12, x, y, 109.8))  # paso + cabeza
SWEEP_Z = 101.4 + 0.6                   # cara inferior del barredor (disco a 101.4)
R_IN, R_OUT = 31.5, 50.5
A_IN, A_OUT, A_END = 226.0, 214.0, 233.5   # cara de ataque inclinada; el techo empieza en 235°
def polar(r, a):
    return (r * math.cos(math.radians(a)), r * math.sin(math.radians(a)))
plan = ([polar(R_IN, A_IN)] + [polar(R_OUT, A_OUT + (A_END - A_OUT) * k / 12) for k in range(13)]
        + [polar(R_IN, A_END - (A_END - A_IN) * k / 6) for k in range(7)])
blade = cq.Workplane('XY', origin=(0, 0, SWEEP_Z)).polyline(plan).close().extrude(30).val()
# Perfil radial: dorso a 45° hacia la pared, imprimible sin soportes boca abajo.
env = (cq.Workplane('XZ').polyline([(R_IN, SWEEP_Z), (R_OUT, SWEEP_Z), (R_OUT, 126),
                                    (49.0 + 0.01, 124.5), (R_IN, SWEEP_Z + 4.0 + 0.01)]).close()
       .revolve(360, (0, 0, 0), (0, 1, 0)).val())
res = res.fuse(blade.intersect(env))
res = res.fuse(cyl(PIN_R, 2.0, PIN_XY[0], PIN_XY[1], 105.8 - 2.0))   # pin de orientación
add('07_reserva_con_barredor', res,
    'Reserva V3 con barredor rígido integrado (sustituye al peine 20 de TPU), '
    'chaflán bajo la pestaña y pin de orientación. Imprimir boca abajo.')

# ------------------------------------------ 16 bandeja inclinada, una pieza
# Celda (referencia) 50x15x7: x -25..25, y -46.5..-31.5, z 24..31. Extremo
# móvil en +X. La bandeja abraza el extremo con un manguito y se fija con un
# prisionero M3x10 que se aprieta desde dentro de la bandeja.
# El fondo baja a 25° hacia la ventana frontal y termina en un bolsillo que
# sale por la ventana: la pastilla resbala sola y se toma desde fuera, sin
# dejar de estar sobre la celda (se sigue pesando).
CL = 0.2
TX0, TX1 = -22.5, 25.0                  # ventana de la carcasa: x -27..27
SZ0 = 24 - CL - 2.0                     # fondo del manguito (21.8)
sleeve = box(10, TX1, -46.5 - CL - 3, -31.5 + CL + 3, SZ0, 70)
sleeve = sleeve.cut(box(9, TX1 + 1, -46.5 - CL, -31.5 + CL, 24 - CL, 31 + CL))
tray = sleeve.intersect(extr_yz([(-90, 0), (-90, Z_POCKET), (Y_KNEE, Z_POCKET),
                                 (TY_BACK, floor_top(TY_BACK)), (TY_BACK, 0)], TX0, TX1))
outer = extr_yz([(TY_BACK, floor_top(TY_BACK) - FLOOR), (Y_KNEE, Z_POCKET - FLOOR),
                 (TY_FRONT, Z_POCKET - FLOOR), (TY_FRONT, Z_POCKET + WALL_H),
                 (Y_KNEE, Z_POCKET + WALL_H), (TY_BACK, floor_top(TY_BACK) + WALL_H)], TX0, TX1)
cavity = extr_yz([(TY_BACK + TW, floor_top(TY_BACK + TW)), (Y_KNEE, Z_POCKET),
                  (TY_FRONT + TW, Z_POCKET), (TY_FRONT + TW, 120), (TY_BACK + TW, 120)],
                 TX0 + TW, TX1 - TW)
tray = tray.fuse(outer).cut(cavity)
# Labio frontal más bajo que las paredes para meter los dedos.
tray = tray.cut(box(TX0 + TW, TX1 - TW, TY_FRONT - 1, TY_FRONT + TW + 0.01, Z_POCKET + LIP_H, 120))
GX, GY = 18.0, -39.0
tray = tray.cut(cyl(1.7, 30, GX, GY, 30))                         # prisionero
tray = tray.cut(hexprism(GX, GY, 32.0, 2.6))                       # tuerca
tray = tray.cut(box(GX, TX1 + 1, GY - 2.95, GY + 2.95, 32.0, 34.6))  # ranura
add('16_bandeja_pesaje_inclinada', tray,
    'Sustituye 14, 15 y 16. Fondo a 25° hacia un bolsillo que sale por la '
    'ventana frontal. Manguito para el extremo móvil de la celda y prisionero '
    'M3x10 con tuerca. Imprimir de pie sobre la cara +X.')

# ------------------------------------------- 13 mordaza fija con tuercas
# Misma envolvente que V3 (13x32x3.5). Tuercas M3 en alojamientos hexagonales
# por arriba: quedan atrapadas bajo la bandeja y no se caen al montar.
mor = box(-25, -12, -55, -23, 31, 34.5)
for y in (-51, -27):
    mor = mor.cut(cyl(1.7, 6, -18.5, y, 30)).cut(hexprism(-18.5, y, 31.9, 3))
add('13_mordaza_fija_celda_tuercas', mor,
    'Mordaza superior del extremo fijo. Dos tuercas M3 en su cara superior; '
    'los M3x30 entran desde debajo de la carcasa.')

# --------------------------------------------- 21 tapa cuadrada de una pieza
# Sustituye al embellecedor (21a/21b) y a la tapa redonda 09. Caja cuadrada a
# ras de la carcasa que cubre placa, disco, aro y reserva y cierra arriba. Una
# ceja circular por dentro entra en la boca de la reserva y la centra; cuatro
# pestañas de esquina entran en la carcasa. Para rellenar se levanta entera.
RES_TOP, RES_IN = 166.8, 49.0
DECK0 = RES_TOP + 0.3                   # 0.3 mm sobre el borde de la reserva
DECK_T = 2.5
TOP = DECK0 + DECK_T
cap = rrect(W, RC, 89, TOP - 89).cut(rrect(W, RC, 88, DECK0 - 88, inset=2.0))
cap = cap.fuse(cyl(RES_IN - 0.3, DECK0 - 163.8 + 0.01, z=163.8).cut(cyl(RES_IN - 3.3, 10, z=163)))   # ceja
for x, y in [(12, 12), (-12, 12), (12, -12), (-12, -12)]:
    cap = cap.cut(cyl(1.0, 10, x, y, DECK0 - 1))                     # respiraderos
tabs = rrect(W, RC, 83, 6.01, inset=WALL + 0.25).cut(rrect(W, RC, 82, 8, inset=WALL + 0.25 + 1.6))
ledge = rrect(W, RC, 89, 2.0).cut(rrect(W, RC, 88, 4, inset=WALL + 0.25 + 1.6))
keep = None
for sx in (-1, 1):
    for sy in (-1, 1):
        b = box(min(sx * 42, sx * 70), max(sx * 42, sx * 70), min(sy * 42, sy * 70), max(sy * 42, sy * 70), 82, 90)
        keep = b if keep is None else keep.fuse(b)
cap = cap.fuse(tabs.fuse(ledge).intersect(keep))
add('21_tapa_cuadrada', cap,
    'Tapa y embellecedor en una sola pieza (sustituye 21a, 21b y 09). Ceja '
    'circular que entra en la boca de la reserva. Imprimir boca abajo.')

# ------------------------------------------------ piezas V3 sin cambios
UNCHANGED = ['03_rotor_15x8_con_cubo', '06_cono_repartidor_punta_arriba',
             '10_bancada_motor_32x25', '11_puente_motor']
for n in UNCHANGED:
    add(n, v3(n), 'Sin cambios respecto a V3.')

# ------------------------------------------------------------- exportación
# Orientación de impresión de cada STL (los STEP quedan en coordenadas de ensamble).
FLIP_X = {'02_', '03_', '04_', '07_', '21_'}
for d in ['STL', 'STEP_piezas', 'Referencias_NO_imprimir']:
    (OUT / d).mkdir(exist_ok=True)
for n, s in sorted(parts.items()):
    q = s
    if n[:3] in FLIP_X:
        q = s.rotate((0, 0, 0), (1, 0, 0), 180)
    elif n.startswith('16_'):
        q = s.rotate((0, 0, 0), (0, 1, 0), 90)          # cara +X sobre la cama
    b = q.BoundingBox()
    q = q.translate((-(b.xmin + b.xmax) / 2, -(b.ymin + b.ymax) / 2, -b.zmin))
    cq.exporters.export(q, str(OUT / 'STL' / (n + '.stl')), tolerance=.025, angularTolerance=.08)
    cq.exporters.export(s, str(OUT / 'STEP_piezas' / (n + '.step')))
REFS = V3
for n in ['REF_motor_32x25', 'REF_eje_6x35', 'REF_celda_50x15x7']:
    cq.exporters.export(cq.importers.importStep(str(REFS / (n + '.step'))).val(),
                        str(OUT / 'Referencias_NO_imprimir' / (n + '.step')))
meta = {n: {'size_mm': [round(s.BoundingBox().xlen, 3), round(s.BoundingBox().ylen, 3),
                        round(s.BoundingBox().zlen, 3)],
            'volume_mm3': round(s.Volume(), 1), 'note': notes[n]}
        for n, s in sorted(parts.items())}
json.dump(meta, open(OUT / 'Dimensiones_y_notas.json', 'w'), indent=2, ensure_ascii=False)
v3params = json.load(open(V3 / 'Parametros_V3.json'))
v3params.update({'version': 'V4', 'tray_grub_xy': [GX, GY], 'overload_stop_gap_mm':
                 round(SZ0 - STOP_TOP, 2), 'feet_height_mm': FEET_H,
                 'sweeper': {'z_bottom': SWEEP_Z, 'r_in': R_IN, 'deg_attack_in': A_IN,
                             'deg_attack_out': A_OUT, 'deg_end': A_END},
                 'reservoir_pin_xy': list(PIN_XY), 'cap_top_z': TOP,
                 'tray_slope_deg': 25, 'tray_floor': {'z_ref_at_y_-55': Z_REF, 'y_knee': Y_KNEE,
                 'z_pocket': round(Z_POCKET, 3), 'y_back': TY_BACK, 'y_front': TY_FRONT}})
json.dump(v3params, open(OUT / 'Parametros_V4.json', 'w'), indent=2)
print('BUILT', len(parts), 'valid unique solids', flush=True)
