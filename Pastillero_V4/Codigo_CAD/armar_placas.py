"""Agrupa los STL de V4 en placas de impresión de 255x255 mm.

Para cada placa genera, en ../Impresion_255x255/:
  * .3mf  con cada pieza como objeto independiente, ya colocada en la cama
  * .stl  con todas las piezas en un solo archivo (posiciones relativas)
  * .png  vista superior con la distribución
Comprueba con la silueta real de cada pieza (incluidos huecos) que nada se
solapa, que hay >= 4 mm entre piezas y >= 2 mm al borde de la cama.
Uso: python armar_placas.py
Requiere: trimesh, shapely, networkx, lxml, matplotlib.
"""
import pathlib, json, math
import numpy as np, trimesh
from shapely.geometry import Polygon, box as sbox
from shapely.ops import unary_union
from shapely import affinity
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).resolve().parents[1]
STL = ROOT / 'STL'
OUT = ROOT / 'Impresion_255x255'
OUT.mkdir(exist_ok=True)
BED, MARGIN, GAP = 255.0, 2.0, 4.0

# (archivo STL sin extensión, centro X, centro Y, giro en grados alrededor de Z)
PLACAS = {
    'Placa_1_estructura_PLA_capa_0.28': {
        'capa': 0.28, 'material': 'PLA o PETG',
        'nota': 'Carcasa y piezas sin holguras finas. Capa gruesa = impresión más rápida.',
        'piezas': [
            ('01_carcasa_v4_patas_pedestal_integrados', 65.0, 65.0, 0),
            ('06_cono_repartidor_punta_arriba', 192.5, 62.5, 0),
            ('10_bancada_motor_32x25', 32.0, 156.0, 0),
            ('16_bandeja_pesaje_inclinada', 95.0, 165.0, 0),
            ('11_puente_motor', 35.0, 200.0, 0),
            ('13_mordaza_fija_celda_tuercas', 35.0, 225.0, 90),
        ]},
    'Placa_2_mecanismo_y_tapa_PLA_capa_0.20': {
        'capa': 0.20, 'material': 'PLA o PETG',
        'nota': 'Reserva (con techo y separadores), disco y placa: holguras finas. Y la tapa cuadrada.',
        'piezas': [
            ('21_tapa_cuadrada', 65.0, 65.0, 0),
            ('07_reserva_con_barredor', 192.5, 62.5, 0),
            ('02_placa_inferior_con_canal', 65.0, 192.5, 0),
            ('03_rotor_15x8_con_cubo', 192.5, 192.5, 0),
        ]},
}


def footprint(mesh):
    """Silueta exacta vista desde arriba (unión de triángulos proyectados)."""
    tris = mesh.vertices[mesh.faces][:, :, :2]
    a, b = tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0]
    area = np.abs(a[:, 0] * b[:, 1] - a[:, 1] * b[:, 0])
    polys = [Polygon(t) for t in tris[area > 1e-9]]
    return unary_union(polys).buffer(0.01).buffer(-0.01)


def placed(name, x, y, rot):
    m = trimesh.load(STL / (name + '.stl'))
    m.apply_transform(trimesh.transformations.rotation_matrix(math.radians(rot), [0, 0, 1]))
    b = m.bounds
    m.apply_translation([x - (b[0][0] + b[1][0]) / 2, y - (b[0][1] + b[1][1]) / 2, -b[0][2]])
    return m


resumen = {}
for placa, cfg in PLACAS.items():
    meshes, fps = [], []
    for name, x, y, rot in cfg['piezas']:
        m = placed(name, x, y, rot)
        meshes.append((name, m)); fps.append((name, footprint(m)))
    # Comprobaciones de cama y separación.
    bed_ok = sbox(MARGIN, MARGIN, BED - MARGIN, BED - MARGIN)
    for name, fp in fps:
        assert bed_ok.contains(fp), (placa, name, 'se sale de la cama', fp.bounds)
    gaps = {}
    for i in range(len(fps)):
        for j in range(i + 1, len(fps)):
            d = fps[i][1].distance(fps[j][1])
            gaps[f'{fps[i][0]} / {fps[j][0]}'] = round(d, 1)
            assert d >= GAP, (placa, fps[i][0], fps[j][0], d)
    # 3MF con objetos separados y STL combinado.
    scene = trimesh.Scene()
    for name, m in meshes:
        scene.add_geometry(m, node_name=name, geom_name=name)
    (OUT / (placa + '.3mf')).write_bytes(trimesh.exchange.threemf.export_3MF(scene))
    trimesh.util.concatenate([m for _, m in meshes]).export(OUT / (placa + '.stl'))
    # Vista superior.
    fig, ax = plt.subplots(figsize=(6, 6.6))
    ax.add_patch(plt.Rectangle((0, 0), BED, BED, fill=False, lw=2, ec='#333'))
    colors = ['#5b9bd5', '#d8a657', '#8a97a8', '#6a8fa8', '#c96f4a', '#7a9a6a', '#a6c', '#3b5b73']
    for k, (name, fp) in enumerate(fps):
        geoms = getattr(fp, 'geoms', [fp])
        for g in geoms:
            ax.fill(*g.exterior.xy, color=colors[k % len(colors)], alpha=.85, lw=0)
            for hole in g.interiors:
                ax.fill(*hole.xy, color='white', lw=0)
        c = fp.representative_point() if name.startswith('21') else fp.centroid
        if name.startswith('21'):
            c = type(c)(fp.bounds[0] + 14, fp.bounds[1] + 8)
        ax.text(c.x, c.y, name.split('_')[0], ha='center', va='center', fontsize=11, weight='bold', color='white')
    ax.set_xlim(-5, BED + 5); ax.set_ylim(-5, BED + 5); ax.set_aspect('equal')
    ax.set_title(f"{placa}\n{cfg['material']} · capa {cfg['capa']} mm · cama {BED:.0f}x{BED:.0f}", fontsize=10)
    ax.set_xticks([0, 64, 128, 192, 255]); ax.set_yticks([0, 64, 128, 192, 255])
    fig.savefig(OUT / (placa + '.png'), dpi=110, bbox_inches='tight'); plt.close(fig)
    resumen[placa] = {
        'material': cfg['material'], 'altura_capa_mm': cfg['capa'], 'nota': cfg['nota'],
        'piezas': [n for n, *_ in cfg['piezas']],
        'altura_max_mm': round(max(m.bounds[1][2] for _, m in meshes), 1),
        'volumen_solido_cm3': round(sum(m.volume for _, m in meshes) / 1000, 1),
        'separacion_minima_mm': min(gaps.values()) if gaps else None}
    print(placa, 'OK', resumen[placa]['piezas'], 'sep. mín.', resumen[placa]['separacion_minima_mm'], flush=True)
json.dump(resumen, open(OUT / 'Resumen_placas.json', 'w'), indent=2, ensure_ascii=False)
