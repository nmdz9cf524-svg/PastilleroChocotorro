import cadquery as cq,pathlib,json,math,itertools,struct,collections,numpy as np
import sys
R=pathlib.Path(sys.argv[1]).resolve() if len(sys.argv)>1 else pathlib.Path(__file__).resolve().parents[1]
if (R/'Reconstruido_V3').is_dir():R=R/'Reconstruido_V3'
params=json.load(open(R/'Parametros_V3.json'))
V=cq.Vector
parts={p.stem:cq.importers.importStep(str(p)).val() for p in sorted((R/'STEP_piezas').glob('*.step'))}
refs={p.stem:cq.importers.importStep(str(p)).val() for p in sorted((R/'Referencias_NO_imprimir').glob('REF*.step'))}
C=39.244
assembly=dict(parts)
s=parts['05_separador_placas_x4']
for i,(x,y) in enumerate([(-C,-C),(-C,C),(C,-C)],1):assembly[f'separador_extra_{i}']=s.translate((x-C,y-C,0))
s=parts['19_pata_inferior_x4']
for i,(x,y) in enumerate([(-54,54),(54,-54),(54,54)],1):assembly[f'pata_extra_{i}']=s.translate((x+54,y+54,0))
# Real fastener envelopes: M3 button heads <= Ø5.7 x1.65, shaft Ø3, nut 5.5 AF x2.4.
fast={};nuts={};bolt_schedule=[]
def bolt(n,x,y,z,length,up=False):
 d=V(0,0,1 if up else -1);shaft=cq.Solid.makeCylinder(1.5,length,V(x,y,z),d)
 head=cq.Solid.makeCylinder(2.85,1.65,V(x,y,z),V(0,0,-1 if up else 1))
 fast[n]=shaft.fuse(head);bolt_schedule.append((n,length))
def nut(n,x,y,z):
 nuts[n]=cq.Workplane('XY',origin=(x,y,z)).polygon(6,6.35).extrude(2.4).val().cut(cq.Solid.makeCylinder(1.7,3,V(x,y,z-.2)))
for x in [-C,C]:
 for y in [-C,C]:
  n=f'placas_{x}_{y}';bolt(n,x,y,109.8,30);nut(n,x,y,85.0)
for x in [-18.5,18.5]:
 for y in [-16,16]:
  n=f'motor_base_{x}_{y}';bolt(n,x,y,0,12,True);nut(n,x,y,6.1)
for x in [-21,21]:
 n=f'puente_motor_{x}';bolt(n,x,0,73,12);nut(n,x,0,63.1)
for y in [-51,-27]:
 bolt(f'pedestal_{y}',-18.5,y,0,12,True);nut(f'pedestal_{y}',-18.5,y,6.1)
 bolt(f'mordaza_fija_{y}',-18.5,y,32.5,16);nut(f'mordaza_fija_{y}',-18.5,y,20.1)
 bolt(f'bandeja_{y}',17.0,y,37,20);nut(f'bandeja_{y}',17.0,y,19.3)
for x in [27.5,55.5]:
 for y in [-29.5,29.5]:
  n=f'electronica_{x}_{y}';bolt(n,x,y,0,12,True);nut(n,x,y,8.1)
for x in [-14,14]:
 bolt(f'canal_{x}',x,-40,85,8,True);nut(f'canal_{x}',x,-40,90.5)
for k,(x,y) in enumerate(params['cone_bolts_xy']):
 bolt(f'cono_{k}',x,y,95.4,12,True);nut(f'cono_{k}',x,y,104.1)
 nuts[f'cono_{k}']=nuts[f'cono_{k}'].rotate((x,y,0),(x,y,1),15)
for k,(x,y) in enumerate(params['wiper_bolts_xy']):
 bolt(f'peine_{k}',x,y,109.8,8);nut(f'peine_{k}',x,y,101.9)
# Two rotor nuts and set screws are a rotating group.
radial={}
for suffix,plane,origin,axis in [('X','YZ',(5.9,0,84),(1,0,0)),('Y','XZ',(0,5.9,84),(0,1,0))]:
 # Generate X nut explicitly then rotate for the Y nut.
 pts=[(3.175*math.cos(math.radians(30+i*60)),3.175*math.sin(math.radians(30+i*60))) for i in range(6)]
 n=cq.Workplane('YZ',origin=(5.9,0,84)).polyline(pts).close().extrude(2.4).val().cut(cq.Solid.makeCylinder(1.7,3,V(5.7,0,84),V(1,0,0)))
 ss=cq.Solid.makeCylinder(1.5,6,V(3,0,84),V(1,0,0))
 if suffix=='Y':n=n.rotate((0,0,0),(0,0,1),90);ss=ss.rotate((0,0,0),(0,0,1),90)
 radial['tuerca_rotor_'+suffix]=n;radial['prisionero_'+suffix]=ss
# Pairwise check; tiny tangent numerical noise ignored below 0.001 mm³.
allshapes={**assembly,**refs,**{'TORNILLO_'+n:s for n,s in fast.items()},**{'TUERCA_'+n:s for n,s in nuts.items()},**radial}
col=[]
for (na,a),(nb,b) in itertools.combinations(allshapes.items(),2):
 ba=a.BoundingBox();bb=b.BoundingBox()
 if any([ba.xmax<bb.xmin-1e-5,bb.xmax<ba.xmin-1e-5,ba.ymax<bb.ymin-1e-5,bb.ymax<ba.ymin-1e-5,ba.zmax<bb.zmin-1e-5,bb.zmax<ba.zmin-1e-5]):continue
 v=a.intersect(b).Volume()
 if v>.001:col.append([na,nb,round(v,5)])
print('PAIRWISE',col,flush=True)
# Continuous sweep bounding the whole rotating group, including solid cavity edges.
env=cq.Solid.makeCylinder(52.5,8,V(0,0,93.4)).fuse(cq.Solid.makeCylinder(10,13.4,V(0,0,80))).fuse(cq.Solid.makeCone(31,1.5,35,V(0,0,101.4))).cut(cq.Solid.makeCylinder(3.2,25.5,V(0,0,79)))
moving_names={'03_rotor_15x8_con_cubo','06_cono_repartidor_punta_arriba'}|set(radial)|{n for n in allshapes if n.startswith(('TORNILLO_cono_','TUERCA_cono_'))}
static={n:s for n,s in allshapes.items() if n not in moving_names}
sweepbad=[];clearances={}
for n,s in static.items():
 v=env.intersect(s).Volume()
 if v>.001:sweepbad.append([n,v])
 clearances[n]=env.distance(s)
print('FULL_SWEEP',sweepbad,'MIN_GAP',min(clearances.values()),flush=True)
# STL check with welded float32 coordinates and directed edge winding.
mesh=[]
for p in sorted((R/'STL').glob('*.stl')):
 data=p.read_bytes();count=struct.unpack_from('<I',data,80)[0];assert len(data)==84+count*50
 ed=collections.Counter();directions=collections.Counter();vv=[];vol=0
 for k in range(count):
  rec=struct.unpack_from('<12fH',data,84+50*k);v=[tuple(round(x,5) for x in rec[j:j+3]) for j in [3,6,9]];vv+=v
  a,b,c=map(np.array,v);vol+=float(np.dot(a,np.cross(b,c)))/6
  for j in range(3):
   e=(v[j],v[(j+1)%3]);key=tuple(sorted(e));ed[key]+=1;directions[key]+=1 if e==key else -1
 bad=sum(v!=2 for v in ed.values());winding=sum(v!=0 for v in directions.values())
 dim=[max(v[j] for v in vv)-min(v[j] for v in vv) for j in range(3)]
 s=parts[p.stem];expected=s
 if p.stem.startswith('20_'):expected=s.rotate((0,0,0),(0,0,1),-235).rotate((0,0,0),(1,0,0),90)
 b=expected.BoundingBox();err=max(abs(a-b) for a,b in zip(dim,[b.xlen,b.ylen,b.zlen]));verr=abs(vol-s.Volume())/s.Volume()
 mesh.append({'file':p.name,'triangles':count,'bad_edges':bad,'winding_errors':winding,'dimension_max_error_mm':err,'volume_relative_error':verr})
 assert bad==0 and winding==0 and err<.05 and verr<.002,(p.name,mesh[-1])
result={'static_collisions_mm3_above_0_001':col,'continuous_rotor_sweep_collisions':sweepbad,'minimum_nominal_rotor_clearance_mm':min(clearances.values()),'rotor_clearances_mm':clearances,'meshes':mesh,'fastener_count':len(fast)+2,'nut_count':len(nuts)+2,'bolts':dict(collections.Counter(l for n,l in bolt_schedule)),'unique_print_files':len(parts),'printed_parts_in_assembly':len(assembly),'real_component_references':len(refs),'physical_validation':False}
json.dump(result,open(R/'Verificacion_CAD_y_STL.json','w'),indent=2)
assert not col and not sweepbad
cq.exporters.export(cq.Compound.makeCompound(list(fast.values())+list(nuts.values())+list(radial.values())),str(R/'Referencias_NO_imprimir/Tornilleria_nominal.step'))
cq.exporters.export(cq.Compound.makeCompound(list(allshapes.values())),str(R/'Pastillero_V3_ensamble.step'))
print('OK',result['unique_print_files'],'meshes;',result['printed_parts_in_assembly'],'printed pieces;',result['fastener_count'],'fasteners;',result['nut_count'],'nuts',flush=True)
