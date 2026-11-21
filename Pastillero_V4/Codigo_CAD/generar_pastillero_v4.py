"""Pastillero V4. Unidades mm. Parte de los STEP de V3 y aplica los cambios de V4.

Piezas que genera (9 a imprimir + referencias):
  01  Carcasa: patas nervadas, plataforma electrónica, paso de cable, ranuras
      de la rampa y realce con el botón de entrega. Sustituye a 01, 12, 18, 19.
  02  Placa inferior con el canal de descarga integrado y prolongado.
  03  Rotor V3 con cubo en doble D para el eje Ø5 del motor 28BYJ-48.
  06  Cono V3 sin cambios.
  07  Reserva con techo, separadores y barredor integrados (sustituye 04, 05, 20).
  09  Tapa de llenado redonda, encajada a ras en la tapa de servicio.
  10  Bancada para el motor 28BYJ-48 (sustituye 10 y 11).
  16  Rampa de salida fija con bolsillo exterior (sin celda de carga).
  21  Tapa de servicio cuadrada.
Sin sistema de pesaje: se eliminaron celda, mordaza 13, pedestal y tope.

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


# Geometría de la rampa de salida (16), compartida con el canal de la placa 02.
# Ya no hay celda de carga: la rampa es fija, apoya en el borde inferior de la
# ventana (z=25) y en dos nervios que encajan en ranuras del piso.
SLOPE = math.tan(math.radians(25))      # fondo a 25°: la pastilla resbala sola
FLOOR, TW, WALL_H, LIP_H = 2.0, 2.0, 12.0, 5.0
RX = 23.5                               # media anchura (ventana: x -27..27)
TY_BACK, TY_FRONT = -21.5, -92.0        # de -21.5 a -92: el bolsillo sale 29.5 mm de la caja
Y_KNEE = -60.0                          # fin de la rampa / inicio del bolsillo (cara interior de la pared)
Z_POCKET = 27.0                         # cara superior del bolsillo: su base (z=25) apoya en la ventana
Z_REF = Z_POCKET + (-55.0 - Y_KNEE) * SLOPE    # cara superior del fondo en y=-55
RIB_Y = (-50.0, -30.0)                  # nervios bajo la rampa
GROOVE = 1.5                            # profundidad de las ranuras del piso


def floor_top(y):
    return Z_REF + (y + 55.0) * SLOPE if y >= Y_KNEE else Z_REF + (Y_KNEE + 55.0) * SLOPE


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

# Sin sistema de pesaje: ya no hay pedestal, tope ni tornillos de mordaza.
# Ranuras en el piso donde encajan los dos nervios de la rampa de salida.
for yr in RIB_Y:
    car = car.cut(box(-RX - 0.3, RX + 0.3, yr - 1.8, yr + 1.8, 4 - GROOVE, 4.1))

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

add('01_carcasa_v4', car,
    'Carcasa V3 + patas nervadas, plataforma electrónica, paso de cable y '
    'ranuras de la rampa. Sustituye 01, 12, 18, 19.')

# --------------------------------------------------- 02 placa + canal integrado
plate = cyl(60, 4, z=89)
plate = plate.cut(cq.Workplane('XY', origin=(0, -40, 88)).slot2D(16.8, 9.6, angle=90)
                  .extrude(6).val())
plate = plate.cut(cyl(11.5, 6, z=88))      # paso del cubo del rotor: 1.5 mm de holgura por si el eje queda algo descentrado
# Agujero del poste de orientación de la reserva: solo entra en una posición,
# con el techo encima de la ventana de salida.
KEY_XY, KEY_R = (0.0, 56.0), 1.5
plate = plate.cut(cyl(KEY_R + 0.2, 2.3, KEY_XY[0], KEY_XY[1], 93.0 - 2.2))
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
# El canal se prolonga hacia abajo y su boca se corta en paralelo a la rampa,
# con 10 mm de paso: guía la caída y la pastilla sale por debajo de la pared.
ext = box(-9.5, 9.5, -55, -25, 20, 50.01).cut(box(-6.5, 6.5, -52, -28, 19, 52))
canal = canal.fuse(ext)
canal = canal.cut(extr_yz([(-70, 0), (-70, floor_top(-70) + CANAL_GAP),
                           (-15, floor_top(-15) + CANAL_GAP), (-15, 0)], -30, 30))
add('02_placa_inferior_con_canal', plate.fuse(canal),
    'Placa inferior V3 con el canal 17 integrado (sin M3x8 ni tuercas). '
    'Imprimir con la cara superior de la placa sobre la cama.')

# ------------------------------- aro con techo + separadores (van dentro de 07)
# Ya no se imprimen aparte: el aro con su techo y los separadores forman parte
# de la reserva 07. El techo sigue tapando la salida para que no caigan
# pastillas de golpe, y los separadores fijan el hueco del disco.
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
RES_IN_R = 49.0
res = res.cut(cyl(RES_IN_R, 63, z=104.8))
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
# Aro, techo y separadores integrados.
res = res.fuse(aro)
# Relleno a 45° sobre el techo, por dentro de la reserva: hace imprimible el
# techo boca abajo y la pastilla que cae encima resbala hacia el cono.
hood = (cq.Workplane('XZ').polyline([(31.2, 105.8 - 0.01), (49.0 + 0.5, 105.8 - 0.01), (49.0 + 0.5, 124.1),
                                     (49.0, 123.6), (31.2, 105.8 + 0.01)]).close()
        .revolve(360, (0, 0, 0), (0, 1, 0)).val())
roof_wedge_tall = cq.Workplane('XY').polyline([(0, 0), (100 * math.cos(a0), 100 * math.sin(a0)),
                                               (100 * math.cos(a1), 100 * math.sin(a1))]).close().extrude(30).translate((0, 0, 101.8)).val()
res = res.fuse(hood.intersect(roof_wedge_tall))
# Faldón exterior: une los cuatro separadores y el poste en un anillo de 2.5 mm
# (z 93-101.8). Impresa boca abajo, la cara de arriba queda plana en vez de
# acabar en postes sueltos; además los separadores dejan de ser tubos finos
# aislados. Va por fuera del disco (r=51.8) con 5.7 mm de holgura.
SKIRT_R_IN = 57.5
res = res.fuse(cyl(60, 101.8 - 93.0 + 0.01, z=93.0).cut(cyl(SKIRT_R_IN, 12, z=92.0)))
res = res.fuse(cyl(2.7, 101.8 - 93.0 + 0.01, KEY_XY[0], KEY_XY[1], 93.0))   # refuerzo del poste
for x in (-C, C):
    for y in (-C, C):
        res = res.cut(cyl(1.7, 30, x, y, 90))                        # paso M3x30 limpio
# Poste de orientación: baja hasta la placa 02 y entra en su agujero.
res = res.fuse(cyl(KEY_R, 93.0 - 91.0 + 0.01, KEY_XY[0], KEY_XY[1], 91.0))   # solo asoma 2 mm
# Holgura cono-techo: el borde interior del techo (y la punta del barredor)
# pasa de r=31.2 a r=31.55. La ventana de salida empieza en r=31.6, así que
# sigue tapada entera.
res = res.cut(cyl(31.55, 8, z=100.0))
# Línea de llenado máximo: ranura en V grabada por dentro de la pared. Con la
# reserva llena (~400 pastillas) el montón pide más par del que da el
# 28BYJ-48; hasta la línea caben ~60 pastillas de 15x8x6 y el par necesario
# queda en ~7 mN·m, con margen de sobra. No se graba donde la pared está tapada
# por el barredor y el relleno del techo (208°-312°), para no dejar huecos.
FILL_Z, FILL_DEPTH = 113.5, 0.8
fill_groove = (cq.Workplane('XZ').polyline([(RES_IN_R - 0.01, FILL_Z - FILL_DEPTH - 0.1),
                                            (RES_IN_R + FILL_DEPTH, FILL_Z),
                                            (RES_IN_R - 0.01, FILL_Z + FILL_DEPTH + 0.1)]).close()
               .revolve(360, (0, 0, 0), (0, 1, 0)).val())
FILL_A0, FILL_A1 = 312.0, 208.0 + 360.0          # arco grabado, en sentido antihorario
fill_wedge = (cq.Workplane('XY').polyline([(0, 0)] + [polar(80, FILL_A0 + (FILL_A1 - FILL_A0) * k / 24) for k in range(25)])
              .close().extrude(10).translate((0, 0, FILL_Z - 5)).val())
res = res.cut(fill_groove.intersect(fill_wedge))
add('07_reserva_con_barredor', res,
    'Reserva con barredor rígido, aro con techo y separadores integrados '
    '(sustituye a 04, 05 y al peine 20 de TPU). Poste de orientación hacia la '
    'placa 02. Imprimir boca abajo.')

# ------------------------------------------------- 16 rampa de salida fija
# Sin pesaje. El fondo baja a 25° hacia la ventana y termina en un bolsillo
# largo (30 mm) que sale 29.5 mm de la caja: caben varias pastillas y se toman
# con los dedos sin meter la mano. Apoya en el borde inferior de la ventana
# (z=25) y en dos nervios que encajan 1.5 mm en ranuras del piso: no flota y
# no se mueve. Se mete desde dentro antes que la bancada del motor.
outer = extr_yz([(TY_BACK, floor_top(TY_BACK) - FLOOR), (Y_KNEE, Z_POCKET - FLOOR),
                 (TY_FRONT, Z_POCKET - FLOOR), (TY_FRONT, Z_POCKET + WALL_H - 2),
                 (Y_KNEE, Z_POCKET + WALL_H), (TY_BACK, floor_top(TY_BACK) + WALL_H)], -RX, RX)
cavity = extr_yz([(TY_BACK + TW, floor_top(TY_BACK + TW)), (Y_KNEE, Z_POCKET),
                  (TY_FRONT + TW, Z_POCKET), (TY_FRONT + TW, 120), (TY_BACK + TW, 120)],
                 -RX + TW, RX - TW)
ramp = outer.cut(cavity)
# Labio frontal más bajo que las paredes para meter los dedos.
ramp = ramp.cut(box(-RX + TW, RX - TW, TY_FRONT - 1, TY_FRONT + TW + 0.01, Z_POCKET + LIP_H, 120))
for yr in RIB_Y:                                                       # nervios
    ramp = ramp.fuse(box(-RX, RX, yr - 1.5, yr + 1.5, 4 - GROOVE, floor_top(yr + 1.5) - FLOOR + 0.2))
add('16_rampa_salida', ramp,
    'Rampa fija a 25° con bolsillo largo que sale 29.5 mm por la ventana. Apoya '
    'en la ventana y en dos nervios encajados en el piso. Sustituye a la bandeja '
    'de pesaje 16, la mordaza 13 y la celda. Imprimir de pie sobre un costado.')

# ------------------------- 21 tapa de servicio corta + 09 tapa de llenado
# Se abre en dos secciones:
#   * 09 tapa de llenado: tapa redonda apoyada en la boca de la reserva, con una
#     ceja que entra en ella y una pestaña al frente para levantarla.
#   * 21 tapa de servicio: caja cuadrada corta (unos 32 mm) que solo cubre la
#     franja del disco, la pestaña de la reserva y sus tornillos. Su abertura
#     redonda rodea la reserva, que queda a la vista. Se levanta para llegar al
#     disco y los tornillos. Lleva el pulsador de entrega en la esquina.
RES_TOP, RES_IN, RES_OUT = 166.8, 49.0, 52.0
HOLE_R = RES_OUT + 0.5                  # abertura de la tapa de servicio alrededor de la reserva
CHAMFER_AT_HOLE = 109.8 + (60.0 - HOLE_R)   # altura del chaflán de la reserva en el borde de la abertura
DECK0 = CHAMFER_AT_HOLE + 1.0           # cara inferior de la cubierta, 1 mm sobre el chaflán
DECK_T = 2.5
TOP = DECK0 + DECK_T
cap = rrect(W, RC, 89, TOP - 89).cut(rrect(W, RC, 88, DECK0 - 88, inset=2.0))
cap = cap.cut(cyl(HOLE_R, 10, z=DECK0 - 1))                                         # abertura para la reserva
# Botón de entrega arriba: pulsador táctil 6x6 en la esquina frontal derecha.
# Alojamiento bajo la cubierta, con piso: el pulsador entra deslizándose desde
# el lado de la reserva (-X), sus patas pasan por dos ranuras del piso y, al
# pulsarlo, el cuerpo apoya en ese piso. El vástago asoma por un agujero Ø4.2.
BTN_XY, BTN_BODY, BTN_H, BTN_STEM = (46.0, -46.0), 6.0, 3.5, 6.0   # 6x6x9.5 mm
BTN_FLOOR = 1.5
bx, by = BTN_XY
cap = cap.fuse(box(bx - 5, bx + 5, by - 5, by + 5, DECK0 - BTN_H - BTN_FLOOR, DECK0 + 0.01))   # alojamiento
cap = cap.cut(box(bx - 6, bx + 3.05, by - 3.05, by + 3.05, DECK0 - BTN_H, DECK0))               # cuerpo (entra desde -X)
for sy in (-1, 1):                                                                            # ranuras de las patas
    cap = cap.cut(box(bx - 6, bx + 3.05, min(by + sy * 2.0, by + sy * 3.05), max(by + sy * 2.0, by + sy * 3.05),
                      DECK0 - BTN_H - BTN_FLOOR - 1, DECK0 - BTN_H + 0.01))
cap = cap.cut(cyl(2.1, 10, bx, by, DECK0 - 1))                                                # paso del vástago
tabs = rrect(W, RC, 83, 6.01, inset=WALL + 0.25).cut(rrect(W, RC, 82, 8, inset=WALL + 0.25 + 1.6))
ledge = rrect(W, RC, 89, 2.0).cut(rrect(W, RC, 88, 4, inset=WALL + 0.25 + 1.6))
keep = None
for sx in (-1, 1):
    for sy in (-1, 1):
        b = box(min(sx * 42, sx * 70), max(sx * 42, sx * 70), min(sy * 42, sy * 70), max(sy * 42, sy * 70), 82, 90)
        keep = b if keep is None else keep.fuse(b)
cap = cap.fuse(tabs.fuse(ledge).intersect(keep))
add('21_tapa_cuadrada', cap,
    'Tapa de servicio cuadrada corta: cubre solo la franja del disco y los '
    'tornillos, con abertura para la reserva. Lleva el pulsador de entrega 6x6 '
    'en la esquina. Imprimir boca abajo.')

# Tapa de llenado sobre la reserva: disco de 1.6 mm, ceja que entra 3 mm en la
# boca (holgura 0.3) y pestaña al frente para levantarla con el dedo.
LID_T = 1.6
lid = cyl(RES_OUT, LID_T, z=RES_TOP)
lid = lid.fuse(cyl(RES_IN - 0.3, 3.0 + 0.01, z=RES_TOP - 3.0).cut(cyl(RES_IN - 2.3, 4, z=RES_TOP - 3.5)))   # ceja
lid = lid.fuse(cq.Workplane('XY', origin=(0, -RES_OUT + 1, RES_TOP)).slot2D(18, 12).extrude(LID_T).val())  # pestaña
for x, y in [(12, 12), (-12, 12), (12, -12), (-12, -12)]:
    lid = lid.cut(cyl(1.0, 10, x, y, RES_TOP - 5))                                  # respiraderos
add('09_tapa_llenado', lid,
    'Tapa redonda de llenado apoyada en la boca de la reserva, con ceja y '
    'pestaña al frente para levantarla. Imprimir boca abajo.')

# ------------------------------------------------- motor 28BYJ-48 (referencia)
# Medidas de la hoja de datos estándar: cuerpo Ø28 x 19, orejas con agujeros
# Ø4.2 a 35 mm, eje Ø5 con dos planos (3 mm entre planos) descentrado 8 mm,
# saliente Ø9 x 1.5 y eje ~10 mm sobre la cara superior. Comprueba tu motor.
M_BODY_R, M_BODY_H, M_OFF = 14.0, 19.0, 8.0     # cuerpo en (0, +8): el eje queda en (0, 0)
M_EAR_X, M_EAR_W, M_EAR_T = 17.5, 7.0, 1.0
M_TOP = 77.5                            # cara superior del motor (orejas apoyadas en z=76.5)
SHAFT_R, SHAFT_FLAT, SHAFT_TOP = 2.5, 3.0, 87.5
motor = cyl(M_BODY_R, M_BODY_H, 0, M_OFF, M_TOP - M_BODY_H)
ears = (cq.Workplane('XY', origin=(0, M_OFF, M_TOP - M_EAR_T)).slot2D(2 * M_EAR_X + M_EAR_W, M_EAR_W)
        .extrude(M_EAR_T).val())
for sx in (-1, 1):
    ears = ears.cut(cyl(2.1, 3, sx * M_EAR_X, M_OFF, M_TOP - 2))
motor = motor.fuse(ears).fuse(cyl(4.5, 1.5, 0, 0, M_TOP))
motor = motor.fuse(box(-7.75, 7.75, M_OFF + 10, M_OFF + 17, M_TOP - 15, M_TOP - 1))   # caja de cables
shaft = cyl(SHAFT_R, SHAFT_TOP - M_TOP - 1.5, 0, 0, M_TOP + 1.5).intersect(
    box(-SHAFT_FLAT / 2, SHAFT_FLAT / 2, -5, 5, M_TOP, SHAFT_TOP + 1))
refs_new = {'REF_motor_28BYJ48': motor.fuse(shaft).clean()}

# ---------------------------------------------- 10 bancada para 28BYJ-48
# Marco en U: 4 patas sobre los mismos agujeros del piso (M3x12 desde abajo,
# tuerca en ranura lateral), dos paredes laterales y una placa superior. El
# motor entra por arriba en la placa y se atornilla por sus dos orejas con
# M3x8 y tuercas atrapadas debajo. Ya no hace falta el puente 11.
PLATE_Z0, PLATE_Z1 = 71.5, 76.5
ban = box(-25.5, 25.5, -21, 21, PLATE_Z0, PLATE_Z1)
for sx in (-1, 1):
    for sy in (-1, 1):
        x, y = sx * 18.5, sy * 16
        ban = ban.fuse(box(x - 5, x + 5, y - 5, y + 5, 4, PLATE_Z0))
    ban = ban.fuse(box(min(sx * 20.5, sx * 23.5), max(sx * 20.5, sx * 23.5), -21, 21, 4, PLATE_Z0))
ban = ban.cut(cyl(M_BODY_R + 0.5, 30, 0, M_OFF, PLATE_Z0 - 20))                 # cuerpo
ban = ban.cut(box(-8.5, 8.5, M_OFF + 9, 30, PLATE_Z0 - 20, PLATE_Z1 + 1))       # caja de cables
for sx in (-1, 1):
    ban = ban.cut(cyl(1.7, 10, sx * M_EAR_X, M_OFF, PLATE_Z0 - 1))              # paso M3
    ban = ban.cut(hexprism(sx * M_EAR_X, M_OFF, PLATE_Z0 - 0.01, 2.6))          # tuerca
    for sy in (-1, 1):
        x, y = sx * 18.5, sy * 16
        ban = ban.cut(cyl(1.7, 20, x, y, 3))                                    # paso M3x12
        ban = ban.cut(hexprism(x, y, 8.6, 2.6))                                 # tuerca
        ban = ban.cut(box(min(x, x - sx * 8), max(x, x - sx * 8), y - 2.95, y + 2.95, 8.6, 11.2))  # ranura hacia dentro
add('10_bancada_28BYJ48', ban,
    'Bancada para motor 28BYJ-48: el eje queda centrado bajo el rotor. Se '
    'atornilla al piso con 4 M3x12 y el motor por sus orejas con 2 M3x8. '
    'Sustituye 10 y 11.')

# Rotor V3 con cubo para eje Ø5 de doble plano: agujero en doble D (sin
# holgura de giro) y un solo prisionero M3x8 que aprieta contra un plano.
rot = v3('03_rotor_15x8_con_cubo')
hub = cyl(10, 13.4, z=80)
rot = rot.fuse(cyl(3.3, 13.4, z=80))                                             # tapar agujero Ø6.4
rot = rot.fuse(cq.Solid.makeCylinder(1.75, 10.5, V(0, 0, 84), V(0, 1, 0)).intersect(hub))
rot = rot.fuse(box(-3, 3, 5.8, 10.5, 80, 87.35).intersect(hub))                  # tapar ranura Y
rot = rot.cut(cyl(2.6, 24, z=79).intersect(box(-1.6, 1.6, -5, 5, 78, 104)))      # doble D 5.2 / 3.2
rot = rot.cut(cq.Solid.makeCylinder(1.7, 12, V(0, 0, 84), V(1, 0, 0)))          # paso del prisionero (+X)
# Holguras para impresión FDM (±0.2 mm por pieza):
#   * radio del disco 52.5 -> 51.8: 1.0 mm a los separadores de la reserva (antes 0.3).
#     El borde sigue bajo el anillo de la reserva (r=51.8), así que no escapan pastillas.
#   * disco 0.2 mm más fino por cada cara fuera del cono: 0.6 mm a la placa y al techo
#     (antes 0.4). La pastilla acostada (6 mm) sigue quedando bajo la cara superior.
ROTOR_R, ROTOR_Z0, ROTOR_Z1 = 51.8, 93.6, 101.2
rot = rot.cut(cyl(60, 20, z=90).cut(cyl(ROTOR_R, 22, z=89)))                       # borde exterior
rot = rot.cut(cyl(ROTOR_R + 1, ROTOR_Z0 - 93.0, z=93.0).cut(cyl(10.8, 2, z=92.9)))    # cara inferior (no toca el cubo)
CONE_SEAT_R = 30.8                      # base del cono: r=30.67
rot = rot.cut(cyl(ROTOR_R + 1, 1.0, z=ROTOR_Z1).cut(cyl(CONE_SEAT_R, 2, z=ROTOR_Z1 - 0.5)))  # cara superior (no toca el asiento del cono)
add('03_rotor_15x8_eje_D5', rot,
    'Rotor V3 con cubo para el eje Ø5 de doble plano del 28BYJ-48 y un '
    'prisionero M3x8. Imprimir boca abajo.')

# ------------------------------------------------ piezas V3 sin cambios
UNCHANGED = ['06_cono_repartidor_punta_arriba']
for n in UNCHANGED:
    add(n, v3(n), 'Sin cambios respecto a V3.')

# ------------------------------------------------------------- exportación
# Orientación de impresión de cada STL (los STEP quedan en coordenadas de ensamble).
FLIP_X = {'02_', '03_', '04_', '07_', '09_', '10_', '21_'}  # boca abajo (la bancada: placa del motor sobre la cama)
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
# Electrónica de referencia (no se imprime): pulsador táctil 6x6, ULN2003 y ESP32.
h = BTN_BODY / 2
puls = (box(bx - h, bx + h, by - h, by + h, DECK0 - BTN_H, DECK0)                           # cuerpo
        .fuse(cyl(1.75, BTN_STEM, bx, by, DECK0)))                                          # vástago
for sx in (-1, 1):
    for sy in (-1, 1):
        puls = puls.fuse(box(bx + sx * 2.25 - 0.35, bx + sx * 2.25 + 0.35, by + sy * 2.55 - 0.3,
                             by + sy * 2.55 + 0.3, DECK0 - BTN_H - 3.5, DECK0 - BTN_H))  # patas, por las ranuras del piso
uln = box(-58.0, -26.0, -12.0, 23.0, 4.0, 5.6)                                       # PCB 32x35
uln = uln.fuse(box(-45.5, -38.5, -6.0, 13.0, 5.6, 9.0))                             # ULN2003 DIP16
uln = uln.fuse(box(-55.0, -49.0, 4.0, 16.0, 5.6, 12.6))                             # conector del motor
esp = box(27.5, 55.5, -26.0, 26.0, 11.0, 12.6).fuse(box(32.0, 51.0, -26.0, -8.0, 12.6, 15.8))
refs_new.update({'REF_pulsador_6x6': puls, 'REF_driver_ULN2003': uln, 'REF_ESP32_DevKit': esp})
for n, sref in refs_new.items():
    cq.exporters.export(sref, str(OUT / 'Referencias_NO_imprimir' / (n + '.step')))
# ------------------ alternativa: reutilizar la bancada 10 de V3 ya impresa
# La bancada de V3 tiene la misma base que la V4: 4 patas de 10x10 en
# (±18.5, ±16), los mismos agujeros del piso y 51x42 mm de huella. Arriba acaba
# en dos postes a z=69 (en x=±21) para el puente 11 del motor de V3. Este puente
# sustituye a la bancada 10 V4: se atornilla a esos postes con los 2 M3x12 y las
# tuercas del puente 11 de V3, y deja la cara de apoyo del 28BYJ-48 a z=76.5,
# igual que la bancada V4, así que el eje llega a la misma altura del rotor.
ALT = OUT / 'Alternativa_bancada_V3'
ALT.mkdir(exist_ok=True)
AD_Z0, AD_Z1, V3_POST_X = 69.0, PLATE_Z1, 21.0
ad = box(-25.5, 25.5, -12.0, 21.0, AD_Z0, AD_Z1)
ad = ad.cut(cyl(M_BODY_R + 0.5, 20, 0, M_OFF, AD_Z0 - 5))                     # cuerpo del motor
ad = ad.cut(box(-8.5, 8.5, M_OFF + 9, 30, AD_Z0 - 5, AD_Z1 + 1))              # caja de cables
for sx in (-1, 1):
    ad = ad.cut(cyl(1.7, 20, sx * M_EAR_X, M_OFF, AD_Z0 - 5))                 # oreja: paso M3x8
    ad = ad.cut(hexprism(sx * M_EAR_X, M_OFF, AD_Z0 - 0.01, 3.6))             # tuerca de la oreja
    ad = ad.cut(cyl(1.7, 20, sx * V3_POST_X, 0, AD_Z0 - 5))                   # paso M3x12 al poste V3
    ad = ad.cut(cyl(3.0, AD_Z1 - 73.0 + 1, sx * V3_POST_X, 0, 73.0))          # cabeza a z=73, como el puente 11
assert ad.isValid() and len(ad.Solids()) == 1
cq.exporters.export(ad, str(ALT / '11_puente_28BYJ48_sobre_bancada_V3.step'))
q = ad.translate((0, 0, -AD_Z0))                                               # cara de los postes sobre la cama
cq.exporters.export(q, str(ALT / '11_puente_28BYJ48_sobre_bancada_V3.stl'), tolerance=.025, angularTolerance=.08)
print('ALTERNATIVA puente', round(ad.Volume() / 1000, 1), 'cm3 frente a', round(parts['10_bancada_28BYJ48'].Volume() / 1000, 1), flush=True)

meta = {n: {'size_mm': [round(s.BoundingBox().xlen, 3), round(s.BoundingBox().ylen, 3),
                        round(s.BoundingBox().zlen, 3)],
            'volume_mm3': round(s.Volume(), 1), 'note': notes[n]}
        for n, s in sorted(parts.items())}
json.dump(meta, open(OUT / 'Dimensiones_y_notas.json', 'w'), indent=2, ensure_ascii=False)
v3params = json.load(open(V3 / 'Parametros_V3.json'))
v3params.update({'version': 'V4', 'feet_height_mm': FEET_H, 'ramp_rib_y': list(RIB_Y),
                 'sweeper': {'z_bottom': SWEEP_Z, 'r_in': R_IN, 'deg_attack_in': A_IN,
                             'deg_attack_out': A_OUT, 'deg_end': A_END},
                 'reservoir_key_xy': list(KEY_XY), 'rotor': {'r': ROTOR_R, 'z0': ROTOR_Z0, 'z1': ROTOR_Z1, 'cone_seat_r': CONE_SEAT_R}, 'button': {'type': 'pulsador tactil 6x6x9.5', 'xy': list(BTN_XY), 'body_top_z': DECK0},
                 'motor': '28BYJ-48', 'motor_top_z': M_TOP, 'motor_ear_x': M_EAR_X, 'motor_body_offset_y': M_OFF, 'cap_top_z': TOP,
                 'fill_lid_top_z': RES_TOP + LID_T, 'fill_max_line': {'z': FILL_Z, 'depth': FILL_DEPTH, 'deg_from': FILL_A0, 'deg_to': FILL_A1 - 360.0},
                 'tray_slope_deg': 25, 'tray_floor': {'z_ref_at_y_-55': round(Z_REF, 4), 'y_knee': Y_KNEE,
                 'z_pocket': round(Z_POCKET, 3), 'y_back': TY_BACK, 'y_front': TY_FRONT,
                 'pocket_y_center': round((Y_KNEE + TY_FRONT + TW) / 2, 2)}})
json.dump(v3params, open(OUT / 'Parametros_V4.json', 'w'), indent=2)
print('BUILT', len(parts), 'valid unique solids', flush=True)
