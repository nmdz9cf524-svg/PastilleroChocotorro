"""Renderiza piezas STEP a PNG (matplotlib). Uso:
 python renderizar_vista.py salida.png elev azim "titulo" recorte|none pieza.step:RRGGBB ...
recorte = x0,x1,y0,y1,z0,z1 en mm."""
import cadquery as cq,sys,numpy as np,matplotlib
matplotlib.use('Agg');import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
# render2.py out.png elev azim title clip(x0,x1,y0,y1,z0,z1|none) file:color ...
out,elev,azim,title,clip=sys.argv[1],float(sys.argv[2]),float(sys.argv[3]),sys.argv[4],sys.argv[5]
fig=plt.figure(figsize=(8,8));ax=fig.add_subplot(111,projection='3d');allv=[]
for a in sys.argv[6:]:
    f,col=a.rsplit(':',1);s=cq.importers.importStep(f).val()
    if clip!='none':
        x0,x1,y0,y1,z0,z1=map(float,clip.split(','));s=s.intersect(cq.Solid.makeBox(x1-x0,y1-y0,z1-z0,cq.Vector(x0,y0,z0)))
        if not s.Solids():continue
    v,t=s.tessellate(0.2,0.3);v=np.array([[p.x,p.y,p.z] for p in v]);t=np.array(t)
    tri=v[t];n=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]+1e-9
    L=np.array([0.4,-0.6,0.7]);L/=np.linalg.norm(L);sh=0.4+0.6*np.abs(n@L)
    base=np.array(matplotlib.colors.to_rgb('#'+col))
    ax.add_collection3d(Poly3DCollection(tri,facecolors=np.clip(base[None]*sh[:,None],0,1),edgecolors='none'));allv.append(v)
V=np.vstack(allv);mn,mx=V.min(0),V.max(0);c=(mn+mx)/2;r=(mx-mn).max()/2*0.85
ax.set_xlim(c[0]-r,c[0]+r);ax.set_ylim(c[1]-r,c[1]+r);ax.set_zlim(c[2]-r,c[2]+r);ax.view_init(elev,azim);ax.set_box_aspect((1,1,1));ax.set_axis_off()
ax.set_title(title,fontsize=14)
plt.savefig(out,dpi=90,bbox_inches='tight')
