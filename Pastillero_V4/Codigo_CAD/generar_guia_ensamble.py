"""Genera la guía animada de ensamble de Pastillero V4.

Salidas:
  ../Guia_visual/Ensamble_Pastillero_V4.html   guía de ensamble autocontenida (abre con doble clic)
  ../Guia_visual/Simulacion_boton_V4.html      simulación del botón: 30° y una pastilla por pulsación
  [--artefacto-boton DIR]  la simulación para publicar (DIR/index.html + DIR/ensamble_v4.txt)
  [--artefacto DIR]  DIR/index.html + DIR/ensamble_v4.txt (base64)  (versión para publicar,
                     con la geometría en un archivo aparte)

Lee los STEP de ../STEP_piezas, ../Referencias_NO_imprimir (con los nombres de la
tornillería que deja validar_v4.py) y Parametros_V4.json. Ejecuta antes
generar_pastillero_v4.py y validar_v4.py.
Uso: python generar_guia_ensamble.py [--artefacto DIR]
"""
import cadquery as cq, pathlib, json, struct, base64, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
HERE = pathlib.Path(__file__).resolve().parent
TOL, ANG = 0.12, 0.3
V3_CSS = ROOT.parent / 'Guia_visual' / 'Ensamble_Pastillero_V3.html'


def load(p):
    return cq.importers.importStep(str(p)).val()


meshes = []  # (nombre, forma)
for p in sorted((ROOT / 'STEP_piezas').glob('*.step')):
    if p.stem == '21b_embellecedor_alto':
        continue  # la guía muestra el embellecedor corto; el alto se monta igual
    meshes.append((p.stem, load(p)))
for n in ['REF_celda_50x15x7', 'REF_motor_28BYJ48', 'REF_pulsador_12mm', 'REF_driver_ULN2003', 'REF_ESP32_DevKit']:
    meshes.append((n, load(ROOT / 'Referencias_NO_imprimir' / (n + '.step'))))
hw_names = json.load(open(ROOT / 'Referencias_NO_imprimir' / 'Tornilleria_nominal_nombres.json'))
hw = load(ROOT / 'Referencias_NO_imprimir' / 'Tornilleria_nominal.step').Solids()
assert len(hw) == len(hw_names), (len(hw), len(hw_names))
c0 = hw[0].BoundingBox().center
assert hw_names[0].startswith('TORNILLO_placas_') and abs(c0.x + 39.244) < 0.1, 'orden de tornillería inesperado'
meshes += list(zip(hw_names, hw))
# Pastilla ficticia 15x8x6, origen en el centro de su cara inferior.
pill = cq.Workplane('XY').slot2D(15, 8, angle=90).extrude(6).edges('>Z or <Z').fillet(.8).val()
meshes.append(('PASTILLA', pill))

# Formato binario (little endian): uint32 n; por malla: uint32 nv, uint32 ni,
# int16 xyz*100 (nv*3), relleno a 4 bytes, uint32 índices (ni).
blob = bytearray(struct.pack('<I', len(meshes)))
tris_total = 0
for name, shape in meshes:
    v, t = shape.tessellate(TOL, ANG)
    pos = np.round(np.array([[q.x, q.y, q.z] for q in v]) * 100).astype('<i2')
    idx = np.array(t, dtype='<u4').ravel()
    blob += struct.pack('<II', len(pos), len(idx)) + pos.tobytes()
    blob += b'\0' * ((4 - (len(pos) * 6) % 4) % 4)
    blob += idx.tobytes()
    tris_total += len(t)
print(len(meshes), 'mallas,', tris_total, 'triángulos,', round(len(blob) / 1e6, 2), 'MB', flush=True)

prm = json.load(open(ROOT / 'Parametros_V4.json'))
ramp = {'slope_deg': prm['tray_slope_deg'], 'z_ref': prm['tray_floor']['z_ref_at_y_-55'],
        'y_knee': prm['tray_floor']['y_knee']}
src = V3_CSS.read_text()
i = src.index('<style>\n/* Layout'); j = src.index('</style>', i) + len('</style>')
page = ((HERE / 'plantilla_guia_ensamble.html').read_text()
        .replace('__CSS__', src[i:j]).replace('__RAMP__', json.dumps(ramp)))
names_js = '<script>window.PASTILLERO_NAMES=' + json.dumps([n for n, _ in meshes]) + ';</script>'

out = ROOT / 'Guia_visual'
out.mkdir(exist_ok=True)
b64 = base64.b64encode(bytes(blob)).decode()
standalone = ('<!doctype html>\n<html lang="es"><head><meta charset="utf-8">'
              '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">'
              '<style>body{margin:0}</style></head><body>\n'
              + page.replace('__DATA__', names_js + '\n<script>window.PASTILLERO_B64="' + b64 + '";</script>')
              + '\n</body></html>\n')
(out / 'Ensamble_Pastillero_V4.html').write_text(standalone)
print('guía:', out / 'Ensamble_Pastillero_V4.html', round(len(standalone) / 1e6, 2), 'MB')

sim_src = (HERE / 'plantilla_simulacion_boton.html').read_text().replace('__CSS__', src[i:j]).replace('__RAMP__', json.dumps(ramp))
sim = ('<!doctype html>\n<html lang="es"><head><meta charset="utf-8">'
                         '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">'
                         '<style>body{margin:0}</style></head><body>\n'
                         + sim_src.replace('__DATA__', names_js + '\n<script>window.PASTILLERO_B64="' + b64 + '";</script>')
                         + '\n</body></html>\n')
(out / 'Simulacion_boton_V4.html').write_text(sim)
print('simulación:', out / 'Simulacion_boton_V4.html', round(len(sim) / 1e6, 2), 'MB')
if '--artefacto-boton' in sys.argv:
    d = pathlib.Path(sys.argv[sys.argv.index('--artefacto-boton') + 1]).resolve()
    d.mkdir(parents=True, exist_ok=True)
    (d / 'index.html').write_text(sim_src.replace('__DATA__', names_js))
    (d / 'ensamble_v4.txt').write_text(b64)
    print('artefacto simulación:', d)

if '--artefacto' in sys.argv:
    d = pathlib.Path(sys.argv[sys.argv.index('--artefacto') + 1]).resolve()
    d.mkdir(parents=True, exist_ok=True)
    (d / 'index.html').write_text(page.replace('__DATA__', names_js))
    (d / 'ensamble_v4.txt').write_text(b64)  # base64: los artefactos no sirven .bin
    print('artefacto:', d)
