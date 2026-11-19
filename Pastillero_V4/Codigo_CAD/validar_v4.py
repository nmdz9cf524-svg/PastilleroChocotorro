"""Validación geométrica de Pastillero V4: choques estáticos con tornillería,
barrido continuo del rotor, mallas STL y trayectoria de una pastilla acostada.
Uso: python validar_v4.py [directorio_V4]
"""
import cadquery as cq, pathlib, json, math, itertools, struct, collections, sys
import numpy as np

R = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else pathlib.Path(__file__).resolve().parents[1]
params = json.load(open(R / 'Parametros_V4.json'))
V = cq.Vector
parts = {p.stem: cq.importers.importStep(str(p)).val() for p in sorted((R / 'STEP_piezas').glob('*.step'))}
refs = {p.stem: cq.importers.importStep(str(p)).val() for p in sorted((R / 'Referencias_NO_imprimir').glob('REF*.step'))}
C = 39.244
# Las dos variantes del embellecedor ocupan el mismo sitio: se comprueba cada una por separado.
VARIANTS = ['21a_embellecedor_corto', '21b_embellecedor_alto']
assembly = {n: s for n, s in parts.items() if n not in VARIANTS}

fast, nuts, bolt_schedule = {}, {}, []


def bolt(n, x, y, z, length, up=False):
    d = V(0, 0, 1 if up else -1)
    shaft = cq.Solid.makeCylinder(1.5, length, V(x, y, z), d)
    head = cq.Solid.makeCylinder(2.85, 1.65, V(x, y, z), V(0, 0, -1 if up else 1))
    fast[n] = shaft.fuse(head)
    bolt_schedule.append(f'M3x{length}')


def grub(n, x, y, z, length, up=True):
    fast[n] = cq.Solid.makeCylinder(1.5, length, V(x, y, z), V(0, 0, 1 if up else -1))
    bolt_schedule.append(f'prisionero M3x{length}')


def nut(n, x, y, z):
    nuts[n] = (cq.Workplane('XY', origin=(x, y, z)).polygon(6, 6.35).extrude(2.4).val()
               .cut(cq.Solid.makeCylinder(1.7, 3, V(x, y, z - .2))))


for x in [-C, C]:
    for y in [-C, C]:
        n = f'placas_{x}_{y}'; bolt(n, x, y, 109.8, 30); nut(n, x, y, 85.0)
for x in [-18.5, 18.5]:
    for y in [-16, 16]:
        n = f'motor_base_{x}_{y}'; bolt(n, x, y, 0, 12, True); nut(n, x, y, 6.1)
for x in [-21, 21]:
    n = f'puente_motor_{x}'; bolt(n, x, 0, 73, 12); nut(n, x, 0, 63.1)
for y in [-51, -27]:
    bolt(f'mordaza_fija_{y}', -18.5, y, 4.0, 30, True); nut(f'mordaza_fija_{y}', -18.5, y, 32.0)
gx, gy = params['tray_grub_xy']
grub('bandeja_prisionero', gx, gy, 31.0, 6); nut('bandeja_prisionero', gx, gy, 32.1)
for k, (x, y) in enumerate(params['cone_bolts_xy']):
    bolt(f'cono_{k}', x, y, 95.4, 12, True); nut(f'cono_{k}', x, y, 104.1)
    nuts[f'cono_{k}'] = nuts[f'cono_{k}'].rotate((x, y, 0), (x, y, 1), 15)
for k, (x, y) in enumerate(params['wiper_bolts_xy']):
    bolt(f'peine_{k}', x, y, 109.8, 8); nut(f'peine_{k}', x, y, 101.9)
radial = {}
for suffix in ['X', 'Y']:
    pts = [(3.175 * math.cos(math.radians(30 + i * 60)), 3.175 * math.sin(math.radians(30 + i * 60))) for i in range(6)]
    n = (cq.Workplane('YZ', origin=(5.9, 0, 84)).polyline(pts).close().extrude(2.4).val()
         .cut(cq.Solid.makeCylinder(1.7, 3, V(5.7, 0, 84), V(1, 0, 0))))
    ss = cq.Solid.makeCylinder(1.5, 6, V(3, 0, 84), V(1, 0, 0))
    if suffix == 'Y':
        n = n.rotate((0, 0, 0), (0, 0, 1), 90); ss = ss.rotate((0, 0, 0), (0, 0, 1), 90)
    radial['tuerca_rotor_' + suffix] = n; radial['prisionero_rotor_' + suffix] = ss
    bolt_schedule.append('prisionero M3x6')

hardware = {**{'TORNILLO_' + n: s for n, s in fast.items()}, **{'TUERCA_' + n: s for n, s in nuts.items()}, **radial}


def overlap(a, b):
    ba, bb = a.BoundingBox(), b.BoundingBox()
    return not any([ba.xmax < bb.xmin - 1e-5, bb.xmax < ba.xmin - 1e-5, ba.ymax < bb.ymin - 1e-5,
                    bb.ymax < ba.ymin - 1e-5, ba.zmax < bb.zmin - 1e-5, bb.zmax < ba.zmin - 1e-5])


allshapes = {**assembly, **refs, **hardware}
col = []
for (na, a), (nb, b) in itertools.combinations(allshapes.items(), 2):
    if overlap(a, b):
        v = a.intersect(b).Volume()
        if v > .001:
            col.append([na, nb, round(v, 5)])
for nv in VARIANTS:
    for nb, b in allshapes.items():
        if overlap(parts[nv], b):
            v = parts[nv].intersect(b).Volume()
            if v > .001:
                col.append([nv, nb, round(v, 5)])
print('PAIRWISE', col, flush=True)

# Holguras de piezas nuevas que no deben tocarse (la bandeja cuelga solo de la celda).
gaps = {}
tray = parts['16_bandeja_pesaje_una_pieza']
for n in ['01_carcasa_v4_patas_pedestal_integrados', '13_mordaza_fija_celda_tuercas', '10_bancada_motor_32x25',
          '02_placa_inferior_con_canal', 'TORNILLO_mordaza_fija_-51', 'TORNILLO_mordaza_fija_-27']:
    gaps['bandeja_vs_' + n] = round(tray.distance(allshapes[n]), 3)
for nv in VARIANTS:
    for n in ['02_placa_inferior_con_canal', '04_aro_con_techo_y_separadores', '07_reserva_centrada',
              '09_tapa_reserva_centrada', '20_peine_flexible_TPU', 'TORNILLO_placas_39.244_39.244']:
        gaps[nv + '_vs_' + n] = round(parts[nv].distance(allshapes[n]), 3)
print('GAPS', gaps, flush=True)
assert all(g >= 0.4 for k, g in gaps.items() if k.startswith('bandeja')), gaps

# Barrido continuo del grupo giratorio.
env = (cq.Solid.makeCylinder(52.5, 8, V(0, 0, 93.4)).fuse(cq.Solid.makeCylinder(10, 13.4, V(0, 0, 80)))
       .fuse(cq.Solid.makeCone(31, 1.5, 35, V(0, 0, 101.4))).cut(cq.Solid.makeCylinder(3.2, 25.5, V(0, 0, 79))))
moving = {'03_rotor_15x8_con_cubo', '06_cono_repartidor_punta_arriba'} | set(radial) | \
    {n for n in allshapes if n.startswith(('TORNILLO_cono_', 'TUERCA_cono_'))}
static = {n: s for n, s in {**allshapes, **{v: parts[v] for v in VARIANTS}}.items() if n not in moving}
sweepbad, clearances = [], {}
for n, s in static.items():
    v = env.intersect(s).Volume()
    if v > .001:
        sweepbad.append([n, v])
    clearances[n] = round(env.distance(s), 3)
print('FULL_SWEEP', sweepbad, 'MIN_GAP', min(clearances.values()), flush=True)

# Trayectoria de una pastilla acostada 15x8x6 desde la cavidad hasta la bandeja.
pill = cq.Workplane('XY').slot2D(15, 8, angle=90).extrude(6).edges('>Z or <Z').fillet(.8).val()
trajectory = []
for z in [93, 92, 89, 80, 60, 50, 47, 40, 37]:
    s = pill.translate((0, -40, z))
    bad = [[n, round(o.intersect(s).Volume(), 3)] for n, o in assembly.items()
           if overlap(o, s) and o.intersect(s).Volume() > .001]
    trajectory.append({'pill_bottom_z': z, 'intersections': bad})
assert all(not t['intersections'] for t in trajectory), trajectory

# Mallas STL: cerradas, orientación coherente, misma envolvente y volumen que el CAD.
mesh = []
for p in sorted((R / 'STL').glob('*.stl')):
    data = p.read_bytes(); count = struct.unpack_from('<I', data, 80)[0]; assert len(data) == 84 + count * 50
    ed = collections.Counter(); directions = collections.Counter(); vv = []; vol = 0
    for k in range(count):
        rec = struct.unpack_from('<12fH', data, 84 + 50 * k); v = [tuple(round(x, 5) for x in rec[j:j + 3]) for j in [3, 6, 9]]; vv += v
        a, b, c = map(np.array, v); vol += float(np.dot(a, np.cross(b, c))) / 6
        for j in range(3):
            e = (v[j], v[(j + 1) % 3]); key = tuple(sorted(e)); ed[key] += 1; directions[key] += 1 if e == key else -1
    bad = sum(v != 2 for v in ed.values()); winding = sum(v != 0 for v in directions.values())
    dim = sorted(max(v[j] for v in vv) - min(v[j] for v in vv) for j in range(3))
    s = parts[p.stem]; b = s.BoundingBox()
    if p.stem.startswith('20_'):
        b = s.rotate((0, 0, 0), (0, 0, 1), -235).rotate((0, 0, 0), (1, 0, 0), 90).BoundingBox()
    err = max(abs(x - y) for x, y in zip(dim, sorted([b.xlen, b.ylen, b.zlen]))); verr = abs(vol - s.Volume()) / s.Volume()
    mesh.append({'file': p.name, 'triangles': count, 'bad_edges': bad, 'winding_errors': winding,
                 'dimension_max_error_mm': round(err, 4), 'volume_relative_error': round(verr, 6),
                 'print_height_mm': round(max(v[2] for v in vv), 2)})
    assert bad == 0 and winding == 0 and err < .05 and verr < .002, (p.name, mesh[-1])

result = {'static_collisions_mm3_above_0_001': col, 'continuous_rotor_sweep_collisions': sweepbad,
          'minimum_nominal_rotor_clearance_mm': min(clearances.values()), 'rotor_clearances_mm': clearances,
          'new_part_gaps_mm': gaps, 'pill_release_path': trajectory, 'meshes': mesh,
          'fasteners': dict(collections.Counter(bolt_schedule)), 'fastener_count': len(bolt_schedule),
          'nut_count': len(nuts) + 2, 'unique_print_files': len(parts),
          'printed_parts_in_assembly': len(assembly) + 1, 'physical_validation': False}
json.dump(result, open(R / 'Verificacion_CAD_y_STL.json', 'w'), indent=2, ensure_ascii=False)
assert not col and not sweepbad
cq.exporters.export(cq.Compound.makeCompound(list(hardware.values())), str(R / 'Referencias_NO_imprimir/Tornilleria_nominal.step'))
cq.exporters.export(cq.Compound.makeCompound(list(assembly.values()) + [parts['21a_embellecedor_corto']] +
                                             list(refs.values()) + list(hardware.values())),
                    str(R / 'Pastillero_V4_ensamble.step'))
print('OK', len(parts), 'STL;', result['printed_parts_in_assembly'], 'piezas a imprimir;',
      result['fastener_count'], 'tornillos/prisioneros;', result['nut_count'], 'tuercas', flush=True)
