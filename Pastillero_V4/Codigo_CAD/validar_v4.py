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
VARIANTS = []  # piezas alternativas que ocupan el mismo sitio (ninguna en esta versión)
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
        n = f'motor_base_{x}_{y}'; bolt(n, x, y, 0, 12, True); nut(n, x, y, 8.7)
# Motor 28BYJ-48 por sus orejas: M3x8 desde arriba, tuerca bajo la placa de la bancada.
for x in [-params['motor_ear_x'], params['motor_ear_x']]:
    n = f'motor_oreja_{x}'; bolt(n, x, params['motor_body_offset_y'], params['motor_top_z'], 8)
    nut(n, x, params['motor_body_offset_y'], 71.6)
for k, (x, y) in enumerate(params['cone_bolts_xy']):
    bolt(f'cono_{k}', x, y, 95.4, 12, True); nut(f'cono_{k}', x, y, 104.1)
    nuts[f'cono_{k}'] = nuts[f'cono_{k}'].rotate((x, y, 0), (x, y, 1), 15)
radial = {}
# Un prisionero M3x8 en el cubo, apretando contra el plano del eje (x = +1.5).
pts = [(3.175 * math.cos(math.radians(30 + i * 60)), 3.175 * math.sin(math.radians(30 + i * 60))) for i in range(6)]
radial['tuerca_rotor_X'] = (cq.Workplane('YZ', origin=(5.9, 0, 84)).polyline(pts).close().extrude(2.4).val()
                            .cut(cq.Solid.makeCylinder(1.7, 3, V(5.7, 0, 84), V(1, 0, 0))))
radial['prisionero_rotor_X'] = cq.Solid.makeCylinder(1.5, 8, V(1.5, 0, 84), V(1, 0, 0))   # punta contra el plano del eje
bolt_schedule.append('prisionero M3x8')

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

# Holguras que importan.
gaps = {}
ramp = parts['16_rampa_salida']
for n in ['10_bancada_28BYJ48', '02_placa_inferior_con_canal', 'REF_ESP32_DevKit', 'REF_driver_ULN2003']:
    gaps['rampa_vs_' + n] = round(ramp.distance(allshapes[n]), 3)
# El pulsador va en la tapa de servicio: no debe tocar la reserva ni la tapa de llenado.
for n in ['07_reserva_con_barredor', '09_tapa_llenado']:
    gaps['pulsador_vs_' + n] = round(refs['REF_pulsador_6x6'].distance(allshapes[n]), 3)
cap = parts['21_tapa_cuadrada']
for n in ['02_placa_inferior_con_canal', '07_reserva_con_barredor',
          'TORNILLO_placas_39.244_39.244', '01_carcasa_v4']:
    gaps['tapa_vs_' + n] = round(cap.distance(allshapes[n]), 3)
# Barredor y techo: la parte de la reserva que queda sobre el disco (z 100..105.7, r<51).
sweeper = parts['07_reserva_con_barredor'].intersect(cq.Solid.makeCylinder(51, 5.7, V(0, 0, 100.0)))  # sin el pin (r=56)
for n in ['03_rotor_15x8_eje_D5', '06_cono_repartidor_punta_arriba']:
    gaps['barredor_vs_' + n] = round(sweeper.distance(allshapes[n]), 3)
print('GAPS', gaps, flush=True)
assert all(g >= 0.4 for k, g in gaps.items() if k.startswith(('rampa', 'barredor', 'pulsador'))), gaps
assert all(g >= 0.25 for k, g in gaps.items() if k.startswith('tapa') and not k.endswith('01_carcasa_v4')), gaps  # la tapa apoya en la carcasa

# Barrido continuo del grupo giratorio.
rp = params['rotor']
env = (cq.Solid.makeCylinder(rp['r'], rp['z1'] - rp['z0'], V(0, 0, rp['z0']))                 # disco
       .fuse(cq.Solid.makeCylinder(rp['cone_seat_r'], 101.4 - rp['z0'], V(0, 0, rp['z0'])))   # asiento del cono
       .fuse(cq.Solid.makeCylinder(10, rp['z0'] - 80, V(0, 0, 80)))                            # cubo
       .fuse(cq.Solid.makeCone(31, 1.5, 35, V(0, 0, 101.4))).cut(cq.Solid.makeCylinder(3.2, 25.5, V(0, 0, 79))))
moving = {'03_rotor_15x8_eje_D5', '06_cono_repartidor_punta_arriba'} | set(radial) | \
    {n for n in allshapes if n.startswith(('TORNILLO_cono_', 'TUERCA_cono_'))}
static = {n: s for n, s in {**allshapes, **{v: parts[v] for v in VARIANTS}}.items() if n not in moving}
sweepbad, clearances = [], {}
for n, s in static.items():
    v = env.intersect(s).Volume()
    if v > .001:
        sweepbad.append([n, v])
    clearances[n] = round(env.distance(s), 3)
print('FULL_SWEEP', sweepbad, 'MIN_GAP', min(clearances.values()), flush=True)
# Holguras de giro pensadas para impresión FDM (±0.2 mm por pieza): todas >= 0.6 mm.
res_ = assembly['07_reserva_con_barredor']; pl_ = assembly['02_placa_inferior_con_canal']
disk = cq.Solid.makeCylinder(rp['r'], rp['z1'] - rp['z0'], V(0, 0, rp['z0']))
spin_gaps = {
    'disco_vs_separadores': disk.distance(res_.intersect(cq.Solid.makeBox(200, 200, 8.7, V(-100, -100, 93.0)))),
    'disco_vs_placa': disk.distance(pl_.intersect(cq.Solid.makeBox(200, 200, 4, V(-100, -100, 89)))),
    'disco_vs_techo': disk.distance(res_.intersect(cq.Solid.makeBox(200, 200, 4.2, V(-100, -100, 101.75)))),
    'cubo_vs_agujero_placa': cq.Solid.makeCylinder(10, rp['z0'] - 80, V(0, 0, 80)).distance(pl_),
    'cono_vs_techo': cq.Solid.makeCone(31, 1.5, 35, V(0, 0, 101.4)).distance(res_),
}
spin_gaps = {k: round(v, 3) for k, v in spin_gaps.items()}
print('HOLGURAS_GIRO', spin_gaps, flush=True)
assert all(v >= 0.6 for v in spin_gaps.values()), spin_gaps

# Línea de llenado máximo: capacidad hasta la línea (volumen libre / volumen a
# granel de una pastilla 15x8x6, compacidad 0.58) y que la ranura no deje la
# reserva en varios sólidos ni con huecos internos.
fl = params['fill_max_line']
free = (cq.Solid.makeCylinder(49, fl['z'] - 101.2, V(0, 0, 101.2))
        .cut(parts['07_reserva_con_barredor']).cut(parts['06_cono_repartidor_punta_arriba']).cut(parts['03_rotor_15x8_eje_D5']))
pill_bulk = ((15 - 8) * 8 + math.pi * 16) * 6 / 0.58
fill_capacity = int(free.Volume() / pill_bulk)
print('LINEA_LLENADO', fl['z'], 'capacidad', fill_capacity, 'pastillas', flush=True)
assert 40 <= fill_capacity <= 80, fill_capacity
r07 = parts['07_reserva_con_barredor']
assert len(r07.Solids()) == 1 and len(r07.Shells()) == 1, 'reserva con huecos internos'

# Trayectoria de una pastilla acostada 15x8x6: cae por el canal, se apoya en la
# rampa de 25° y resbala hasta el bolsillo exterior. Nada debe estorbarla.
tf = params['tray_floor']; slope = math.tan(math.radians(params['tray_slope_deg']))
def floor_top(y):
    return tf['z_ref_at_y_-55'] + (max(y, tf['y_knee']) + 55.0) * slope
pill = cq.Workplane('XY').slot2D(15, 8, angle=90).extrude(6).edges('>Z or <Z').fillet(.8).val()
# Pastilla inclinada como la rampa (eje largo según Y, que es la dirección de bajada).
poses = [('cayendo', pill.translate((0, -40, z)), z) for z in [93, 89, 80, 70, 60, 55]]
tilted = pill.rotate((0, 0, 0), (1, 0, 0), params['tray_slope_deg'])  # cara inferior paralela a la rampa
for y in [-36, -40, -45, -50, -54]:          # apoyada en la rampa, bajando
    poses.append(('rampa', tilted.translate((0, y, floor_top(y) + 0.15)), y))
for y in [tf['pocket_y_center']]:              # en el bolsillo exterior
    poses.append(('bolsillo', pill.translate((0, y, floor_top(y) + 0.1)), y))
trajectory = []
for kind, s_, key in poses:
    bad = [[n, round(o.intersect(s_).Volume(), 3)] for n, o in {**assembly, **hardware}.items()
           if overlap(o, s_) and o.intersect(s_).Volume() > .001]
    trajectory.append({'pose': kind, 'pos': key, 'intersections': bad})
assert all(not t['intersections'] for t in trajectory), trajectory
# La pastilla del bolsillo queda fuera de la carcasa (se toma desde fuera).
assert pill.translate((0, tf['pocket_y_center'], 0)).BoundingBox().ymax < -62.5  # la pastilla entera queda fuera de la caja

# Una pastilla por giro: vista desde arriba, la ventana de salida de la placa
# (16.8 x 9.6 en y=-40) debe quedar tapada entera por el techo de la reserva,
# así no caen pastillas de la reserva directamente cuando una cavidad se alinea.
window = cq.Workplane('XY', origin=(0, -40, 101.8)).slot2D(16.8, 9.6, angle=90).extrude(4).val()
uncovered = window.cut(assembly['07_reserva_con_barredor']).Volume()
print('VENTANA_DESCUBIERTA_mm3', round(uncovered, 4), flush=True)
assert uncovered < 0.001

# Montaje de la rampa: entra por arriba 35 mm más atrás (el bolsillo pasa por
# dentro de la pared), baja hasta 2 mm sobre el piso, avanza por la ventana y
# baja 2 mm para que los nervios entren en sus ranuras. Va ANTES que la bancada.
path = [(0, 35, dz) for dz in [80, 60, 40, 20, 10, 4, 2]] + \
       [(0, dy, 2.0) for dy in [30, 25, 20, 15, 10, 5, 2, 0]] + [(0, 0, 1.0), (0, 0, 0)]
insert_bad = []
for dx, dy, dz in path:
    t = ramp.translate((dx, dy, dz))
    for n in ['01_carcasa_v4', 'REF_driver_ULN2003', 'REF_ESP32_DevKit']:
        v = t.intersect(allshapes[n]).Volume()
        if v > .001:
            insert_bad.append([n, dy, dz, round(v, 3)])
# Después, la bancada baja en vertical sin tocar la rampa.
for dz in [80, 40, 10, 2, 0.5]:
    v = assembly['10_bancada_28BYJ48'].translate((0, 0, dz)).intersect(ramp).Volume()
    if v > .001:
        insert_bad.append(['10_bancada_28BYJ48', dz, round(v, 3)])
print('MONTAJE', insert_bad, flush=True)
assert not insert_bad

# Ninguna pieza flotando: cada pieza y componente debe apoyar en otro (contacto
# a menos de 0.02 mm) y, siguiendo esos apoyos, todo debe llegar a la carcasa.
# El rotor cuelga del eje del motor por su prisionero: ese apoyo se cuenta con
# el prisionero, que toca el plano del eje.
bodies = {**assembly, **refs, 'prisionero_rotor_X': radial['prisionero_rotor_X']}
contacts = {n: set() for n in bodies}
names = list(bodies)
for i, a in enumerate(names):
    for b in names[i + 1:]:
        if overlap(bodies[a], bodies[b]) and bodies[a].distance(bodies[b]) < 0.02:
            contacts[a].add(b); contacts[b].add(a)
# Uniones roscadas (no hay contacto geométrico porque el agujero tiene holgura):
# el prisionero rosca en la tuerca atrapada en el cubo del rotor.
for a_, b_ in [('prisionero_rotor_X', '03_rotor_15x8_eje_D5')]:
    contacts[a_].add(b_); contacts[b_].add(a_)
seen, todo = {'01_carcasa_v4'}, ['01_carcasa_v4']
while todo:
    for nb in contacts[todo.pop()]:
        if nb not in seen:
            seen.add(nb); todo.append(nb)
floating = sorted(set(bodies) - seen)
supports = {n: sorted(contacts[n]) for n in bodies}
print('FLOTANDO', floating, flush=True)
assert not floating, floating

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

# Alternativa: bancada 10 de V3 (ya impresa) + puente 11 para el 28BYJ-48 en
# lugar de la bancada 10 V4. Mismas comprobaciones de choque contra todo lo demás.
ALT = R / 'Alternativa_bancada_V3'
alt = {'10_bancada_motor_32x25_V3': cq.importers.importStep(str(R.parent / 'Pastillero_V3/STEP_piezas/10_bancada_motor_32x25.step')).val(),
       '11_puente_28BYJ48_sobre_bancada_V3': cq.importers.importStep(str(ALT / '11_puente_28BYJ48_sobre_bancada_V3.step')).val()}
alt_hw = {}
for x in (-21.0, 21.0):
    bolt(f'puente_V3_{x}', x, 0, 73.0, 12); alt_hw['TORNILLO_puente_V3_' + str(x)] = fast.pop(f'puente_V3_{x}')
    nut(f'puente_V3_{x}', x, 0, 63.1); alt_hw['TUERCA_puente_V3_' + str(x)] = nuts.pop(f'puente_V3_{x}')
bolt_schedule = bolt_schedule[:-2]
for x in (-18.5, 18.5):                                   # la bancada V3 atrapa las tuercas de la base a z=6.1
    for y in (-16, 16):
        alt_hw[f'TUERCA_base_V3_{x}_{y}'] = nuts[f'motor_base_{x}_{y}'].translate((0, 0, 6.1 - 8.7))
alt_hw['TUERCA_oreja_alt_-'] = nuts['motor_oreja_' + str(-params['motor_ear_x'])].translate((0, 0, 70.0 - 71.6))
alt_hw['TUERCA_oreja_alt_+'] = nuts['motor_oreja_' + str(params['motor_ear_x'])].translate((0, 0, 70.0 - 71.6))
others = {n: s for n, s in {**assembly, **refs, **hardware}.items()
          if n != '10_bancada_28BYJ48' and not n.startswith(('TUERCA_motor_oreja', 'TUERCA_motor_base'))}
alt_col = []
for na, a in {**alt, **alt_hw}.items():
    for nb, b in {**others, **{k: v for k, v in {**alt, **alt_hw}.items() if k > na}}.items():
        if overlap(a, b):
            v = a.intersect(b).Volume()
            if v > .001:
                alt_col.append([na, nb, round(v, 4)])
alt_contact = {
    'puente_sobre_postes_V3': round(alt['11_puente_28BYJ48_sobre_bancada_V3'].distance(alt['10_bancada_motor_32x25_V3']), 3),
    'motor_sobre_puente': round(refs['REF_motor_28BYJ48'].distance(alt['11_puente_28BYJ48_sobre_bancada_V3']), 3),
    'bancada_V3_sobre_carcasa': round(alt['10_bancada_motor_32x25_V3'].distance(parts['01_carcasa_v4']), 3),
    'bancada_V3_vs_rampa': round(alt['10_bancada_motor_32x25_V3'].distance(parts['16_rampa_salida']), 3),
    'puente_vs_rotor': round(alt['11_puente_28BYJ48_sobre_bancada_V3'].distance(parts['03_rotor_15x8_eje_D5']), 3),
}
print('ALTERNATIVA_BANCADA_V3', alt_col, alt_contact, flush=True)
assert not alt_col, alt_col
assert alt_contact['puente_sobre_postes_V3'] < 0.02 and alt_contact['motor_sobre_puente'] < 0.02 and alt_contact['bancada_V3_sobre_carcasa'] < 0.02
assert alt_contact['bancada_V3_vs_rampa'] >= 0.4 and alt_contact['puente_vs_rotor'] >= 0.6

result = {'static_collisions_mm3_above_0_001': col, 'continuous_rotor_sweep_collisions': sweepbad,
          'minimum_nominal_rotor_clearance_mm': min(clearances.values()), 'rotor_spin_gaps_mm': spin_gaps, 'fill_max_line': {'z': fl['z'], 'capacity_pills_15x8x6': fill_capacity}, 'rotor_clearances_mm': clearances,
          'new_part_gaps_mm': gaps, 'pill_release_path': trajectory, 'assembly_path_collisions': insert_bad, 'floating_parts': floating, 'alternative_V3_motor_mount': {'collisions': alt_col, 'contacts_and_gaps_mm': alt_contact}, 'exit_window_uncovered_mm3': uncovered, 'supports': supports, 'meshes': mesh,
          'fasteners': dict(collections.Counter(bolt_schedule)), 'fastener_count': len(bolt_schedule),
          'nut_count': len(nuts) + 2, 'unique_print_files': len(parts),
          'printed_parts_in_assembly': len(assembly), 'physical_validation': False}
json.dump(result, open(R / 'Verificacion_CAD_y_STL.json', 'w'), indent=2, ensure_ascii=False)
assert not col and not sweepbad
cq.exporters.export(cq.Compound.makeCompound(list(hardware.values())), str(R / 'Referencias_NO_imprimir/Tornilleria_nominal.step'))
json.dump(list(hardware.keys()), open(R / 'Referencias_NO_imprimir/Tornilleria_nominal_nombres.json', 'w'), indent=0)
cq.exporters.export(cq.Compound.makeCompound(list(assembly.values()) +
                                             list(refs.values()) + list(hardware.values())),
                    str(R / 'Pastillero_V4_ensamble.step'))
print('OK', len(parts), 'STL;', result['printed_parts_in_assembly'], 'piezas a imprimir;',
      result['fastener_count'], 'tornillos/prisioneros;', result['nut_count'], 'tuercas', flush=True)
