import cadquery as cq,pathlib,json,sys,struct,collections
R=pathlib.Path(sys.argv[1]).resolve() if len(sys.argv)>1 else pathlib.Path(__file__).resolve().parents[1]
if (R/'Reconstruido_V3').is_dir():R=R/'Reconstruido_V3'
D=R/'Prueba_opcional';D.mkdir(exist_ok=True)
ps={p.stem:cq.importers.importStep(str(p)).val() for p in (R/'STEP_piezas').glob('*.step')}
def pill(w=8,h=6):return cq.Workplane('XY').slot2D(15,w,angle=90).extrude(h).edges('>Z or <Z').fillet(.8).val()
p=pill();cq.exporters.export(p,str(D/'Pastilla_ficticia_15x8x6.stl'),tolerance=.025,angularTolerance=.08);cq.exporters.export(p,str(D/'Pastilla_ficticia_15x8x6.step'))
rot=ps['03_rotor_15x8_con_cubo'];roof=ps['04_aro_con_techo_descarga'];flat=p.translate((0,-40,93))
stand=p.rotate((0,0,0),(1,0,0),90);b=stand.BoundingBox();stand=stand.translate((0,-40-(b.ymin+b.ymax)/2,93-b.zmin))
side=p.rotate((0,0,0),(0,0,1),90).translate((0,-40,93));double=pill(7.5,5.5).translate((0,-40,98.5))
# Shadow of lower release window, at the fixed roof: entirely blocked from above.
window=cq.Workplane('XY',origin=(0,-40,101.8)).slot2D(16.8,9.6,angle=90).extrude(4).val()
checks={'flat_pill_vs_rotor_mm3':flat.intersect(rot).Volume(),'flat_pill_vs_roof_mm3':flat.intersect(roof).Volume(),'upright_pill_vs_roof_mm3':stand.intersect(roof).Volume(),'crosswise_pill_vs_rotor_mm3':side.intersect(rot).Volume(),'second_layer_min_thickness_pill_vs_roof_mm3':double.intersect(roof).Volume(),'uncovered_release_shadow_mm3':window.cut(roof).Volume()}
assert checks['flat_pill_vs_rotor_mm3']<.001 and checks['flat_pill_vs_roof_mm3']<.001 and checks['uncovered_release_shadow_mm3']<.001
assert all(checks[k]>1 for k in ['upright_pill_vs_roof_mm3','crosswise_pill_vs_rotor_mm3','second_layer_min_thickness_pill_vs_roof_mm3'])
trajectory=[]
for z in [93,92,89,80,60,50,47,40,37]:
 s=p.translate((0,-40,z));bad=[]
 for n,other in ps.items():
  v=s.intersect(other).Volume()
  if v>.001:bad.append([n,v])
 trajectory.append({'pill_bottom_z':z,'intersections':bad});assert not bad,(z,bad)
# Verify optional dummy STL closure too.
raw=(D/'Pastilla_ficticia_15x8x6.stl').read_bytes();count=struct.unpack_from('<I',raw,80)[0];edges=collections.Counter()
for k in range(count):
 r=struct.unpack_from('<12fH',raw,84+50*k);vv=[tuple(round(x,5) for x in r[j:j+3]) for j in [3,6,9]]
 for j in range(3):edges[tuple(sorted([vv[j],vv[(j+1)%3]]))]+=1
assert all(x==2 for x in edges.values())
result={'pill_nominal_mm':[15,8,6],'geometric_tests':checks,'flat_release_path_samples':trajectory,'dummy_mesh_closed':True,'bulk_feed_simulation':False,'physical_feed_test':False}
a=math.degrees(math.atan(4.5/31.9));b=math.degrees(math.atan(4.8/31.6));bound=2*a+b
assert bound<35
result['roof_continuous_coverage_bound']={'required_half_roof_angle_bound_deg':bound,'provided_half_roof_angle_deg':35,'inner_radius_check_mm':[31.9,31.2],'outer_radius_check_mm':[48.1,51.8]}
json.dump(result,open(D/'Comprobacion_pastilla_V3.json','w'),indent=2);print('PILL TESTS',checks,'; all9 release positions clear',flush=True)
