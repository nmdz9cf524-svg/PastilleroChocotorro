"""Pastillero V3. Unidades mm. Pastilla nominal 15x8x6.
Genera prototipo CAD para ensayo; no certifica alimentación física ni pesaje.
Uso: python generar_pastillero_v3.py [directorio_salida]
"""
import cadquery as cq,pathlib,math,json,sys,shutil
ROOT=pathlib.Path(__file__).resolve().parent;SRC=ROOT/'fuentes'
OUT=pathlib.Path(sys.argv[1]).resolve() if len(sys.argv)>1 else ROOT.parent/'Reconstruido_V3'
OUT.mkdir(parents=True,exist_ok=True)
V=cq.Vector;C=39.244;parts={};notes={};refs={}
def box(x,y,h,cx=0,cy=0,z=0):return cq.Workplane('XY').box(x,y,h,centered=(True,True,False)).translate((cx,cy,z)).val()
def cyl(r,h,x=0,y=0,z=0):return cq.Solid.makeCylinder(r,h,V(x,y,z))
def hole(s,x,y,z,h,r=1.7):return s.cut(cyl(r,h,x,y,z))
def capsule(L,W,z,x=0,y=0,h=None):
 a=cq.Workplane('XY',origin=(x,y,z)).slot2D(L,W,angle=90)
 return a.extrude(h).val() if h is not None else a.val()
def hexhole(x,y,z,h):return cq.Workplane('XY',origin=(x,y,z)).polygon(6,6.7).extrude(h).val()
def add(n,s,note=''):
 s=s.clean();assert s.isValid() and len(s.Solids())==1,(n,len(s.Solids()));parts[n]=s;notes[n]=note
UNCHANGED=['01_carcasa_con_columnas','05_separador_placas_x4','10_bancada_motor_32x25','11_puente_motor','12_pedestal_extremo_fijo_celda','13_mordaza_fija_celda','14_mordaza_inferior_extremo_movil','15_apoyo_bandeja_extremo_movil','16_bandeja_pesaje','17_canal_descarga','18_plataforma_electronica','19_pata_inferior_x4']
for n in UNCHANGED:add(n,cq.importers.importStep(str(SRC/(n+'.step'))).val(),'Geometría conservada de V2.')
# Lower plate: narrower release window for the 15x8x6 trial pill.
lower=cyl(60,4,z=89).cut(capsule(16.8,9.6,88,0,-40,6));lower=hole(lower,0,0,88,6,10.5)
for x in [-C,C]:
 for y in [-C,C]:lower=hole(lower,x,y,88,6)
for x in [-14,14]:
 lower=hole(lower,x,-40,88,6);lower=lower.cut(hexhole(x,-40,90.4,3))
add('02_placa_inferior',lower,'Ventana de descarga 16.8x9.6, centrada en (0,-40).')
# New rotor: twelve radial capsule pockets, 16.2 x9 x8.
rot=cyl(52.5,8,z=93.4).fuse(cyl(10,13.4,z=80));rot=hole(rot,0,0,79,24,3.2)
for k in range(12):rot=rot.cut(capsule(16.2,9,93,0,40,9).rotate((0,0,0),(0,0,1),30*k))
for direction in [V(1,0,0),V(0,1,0)]:rot=rot.cut(cq.Solid.makeCylinder(1.7,12,V(0,0,84),direction))
rot=rot.cut(box(2.6,6,7.35,7.1,0,80)).cut(box(6,2.6,7.35,0,7.1,80))
cone_bolts=[]
for deg in [15,135,255]:
 a=math.radians(deg);x,y=16*math.cos(a),16*math.sin(a);cone_bolts.append([x,y])
 rot=hole(rot,x,y,93,10);rot=hole(rot,x,y,93.3,2.1,3.2)
add('03_rotor_15x8_con_cubo',rot,'12 ranuras de16.2x9; cubo Ø20; dos prisionerosM3x6; cono con tres M3x12 desde abajo.')
# Fixed ring and a 70-degree roof over the output prevent free-flow from hopper.
upper=cyl(60,4,z=101.8).cut(cyl(51.8,6,z=101))
a,b=map(math.radians,[235,305]);wedge=cq.Workplane('XY').polyline([(0,0),(100*math.cos(a),100*math.sin(a)),(100*math.cos(b),100*math.sin(b))]).close().extrude(4).translate((0,0,101.8)).val()
sector=cyl(51.8,4,z=101.8).cut(cyl(31.2,6,z=101)).intersect(wedge);upper=upper.fuse(sector)
for x in [-C,C]:
 for y in [-C,C]:upper=hole(upper,x,y,101,6)
# Local U axis points radially along leading edge theta235; V is CCW tangent.
theta=235
def xy(u,v):
 a=math.radians(theta);return u*math.cos(a)-v*math.sin(a),u*math.sin(a)+v*math.cos(a)
wiper_bolts=[]
for u in [35,45]:
 x,y=xy(u,2.8);wiper_bolts.append([x,y]);upper=hole(upper,x,y,101,6);upper=upper.cut(hexhole(x,y,101.8,2.6))
add('04_aro_con_techo_descarga',upper,'Techo fijo235°..305°; giro de trabajo antihorario visto desde arriba.')
# Up-pointing rotating cone; hollow, three nut bosses, 12 shallow radial tracks.
cone=cq.Solid.makeCone(31,1.5,35,V(0,0,101.4)).cut(cq.Solid.makeCone(25,.6,27.6,V(0,0,104.4)))
try:cone=cq.Workplane(obj=cone).edges('>Z').fillet(.7).val()
except Exception:pass
for x,y in cone_bolts:cone=cone.fuse(cyl(5,9,x,y,101.4))
cone=hole(cone,0,0,100,7,3.4)
for deg,(x,y) in zip([15,135,255],cone_bolts):
 cone=hole(cone,x,y,100,12)
 slot=hexhole(16,0,104,2.6).fuse(box(18,5.8,2.6,25,0,104)).rotate((0,0,0),(0,0,1),deg)
 cone=cone.cut(slot)
# Tracks are 9 mm wide and 0.8 mm below nominal conical surface.
slope=35/29.5
za=101.4+(31-21)*slope;zb=101.4+(31-31.3)*slope
track=cq.Workplane('XZ').polyline([(21,za-.8),(31.3,zb-.8),(31.3,zb+3),(21,za+3)]).close().extrude(4.5,both=True).val()
for deg in range(0,360,30):cone=cone.cut(track.rotate((0,0,0),(0,0,1),deg))
add('06_cono_repartidor_punta_arriba',cone,'Ø62 base, alto35; 12 canales radiales; hueco para reducir masa. Gira solidario al rotor.')
# Wide concentric reservoir; external rim bolts remain accessible.
hopper=cyl(52,61,z=105.8).fuse(cyl(60,4,z=105.8)).cut(cyl(49,63,z=104.8))
for x in [-C,C]:
 for y in [-C,C]:hopper=hole(hopper,x,y,105,6)
add('07_reserva_centrada',hopper,'Ø98 interior; flangeØ120; cuatro M3x30 fijan reserva, aro, separadores y base.')
# Lid with clearance0.3 per side and vent holes.
cap=cyl(52,4,z=166.8).fuse(cyl(48.7,3,z=163.8).cut(cyl(45.7,4,z=163.3))).fuse(cyl(8,8,z=170.8))
for x,y in [(12,12),(-12,12),(12,-12),(-12,-12)]:cap=hole(cap,x,y,166,6,1)
add('09_tapa_reserva_centrada',cap,'PestañaØ97.4 para bocaØ98; cuatro respiraderosØ2.')
# TPU comb, fixed just before roof entrance. Flexible tips clear rotor by0.2mm.
wiper=box(17.3,8,4,39.85,1.5,105.8)
u=31.5
while u<48.3:
 width=min(1.0,48.3-u);wiper=wiper.fuse(box(width,.8,4.2,u+width/2,-2,101.6));u+=1.6
for u in [35,45]:wiper=hole(wiper,u,2.8,105,6)
wiper=wiper.rotate((0,0,0),(0,0,1),theta)
add('20_peine_flexible_TPU',wiper,'TPU95A obligatorio para ensayo de barrido; dos M3x8. No sustituir por PLA rígido en prueba con pastillas.')
# Component reference dimensions retained; they still need actual-part confirmation.
for n in ['REF_motor_32x25','REF_eje_6x35','REF_celda_50x15x7']:refs[n]=cq.importers.importStep(str(SRC/(n+'.step'))).val()
for d in ['STL','STEP_piezas','Referencias_NO_imprimir']:(OUT/d).mkdir(exist_ok=True)
for n,s in sorted(parts.items()):
 # The disk is printed upside down; the TPU comb flat on a side, teeth horizontal.
 q=s.rotate((0,0,0),(1,0,0),180) if n.startswith('03_') else s
 if n.startswith('20_'):
  q=s.rotate((0,0,0),(0,0,1),-theta).rotate((0,0,0),(1,0,0),90)
 b=q.BoundingBox();q=q.translate((-(b.xmin+b.xmax)/2,-(b.ymin+b.ymax)/2,-b.zmin))
 cq.exporters.export(q,str(OUT/'STL'/(n+'.stl')),tolerance=.025,angularTolerance=.08)
 cq.exporters.export(s,str(OUT/'STEP_piezas'/(n+'.step')))
for n,s in refs.items():cq.exporters.export(s,str(OUT/'Referencias_NO_imprimir'/(n+'.step')))
meta={n:{'size_mm':[s.BoundingBox().xlen,s.BoundingBox().ylen,s.BoundingBox().zlen],'volume_mm3':s.Volume(),'note':notes[n]} for n,s in sorted(parts.items())}
json.dump(meta,open(OUT/'Dimensiones_y_notas.json','w'),indent=2)
json.dump({'pill_nominal_mm':[15,8,6],'cavity_length_width_mm':[16.2,9],'pocket_count':12,'pocket_pitch_degrees':30,'cone_bolts_xy':cone_bolts,'wiper_bolts_xy':wiper_bolts,'working_rotation':'CCW viewed from top','roof_sector_degrees':[235,305]},open(OUT/'Parametros_V3.json','w'),indent=2)
print('BUILT',len(parts),'valid unique solids',flush=True)
