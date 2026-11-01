import sys, os, math
src = open('/home/claude/scripts/make_items.py').read()
exec(src[:src.index("TEX = ")])
import numpy as np
from PIL import Image
def rbox_v(sx, sy, sz, z0, mat, rv, rtop=0.0, cx=0, cy=0, segs=8):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * sx + cx, v.co.y * sy + cy, v.co.z * sz + z0 + sz / 2))
    ve = [e for e in bm.edges if abs((e.verts[0].co - e.verts[1].co).normalized().z) > 0.9]
    bmesh.ops.bevel(bm, geom=ve, offset=rv, segments=segs, profile=0.5, affect='EDGES')
    if rtop > 0:
        te = [e for e in bm.edges if all(v.co.z > z0 + sz - 1e-3 for v in e.verts) or all(v.co.z < z0 + 1e-3 for v in e.verts)]
        bmesh.ops.bevel(bm, geom=te, offset=rtop, segments=3, profile=0.5, affect='EDGES')
    me = bpy.data.meshes.new('b'); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new('b', me); bpy.context.collection.objects.link(o); me.materials.append(M(mat))
    for p in me.polygons: p.use_smooth = True
    return o

# ============ Console dock + console (generic, no logos) ============
reset()
# dock 17.3 x 5.4 x 10.4, front = -Y
rbox_v(17.3, 5.4, 10.4, 0, 'noir_mat', 1.2, 0.6)
box(14.5, 0.2, 0.6, 0, -2.75, 9.0, 'gris_fonce')                 # front groove
# console standing in the dock (screen facing front), 23.9 x 1.4 x 10.2, bottom inside the dock
rbox_v(17.2, 1.4, 10.2, 5.6, 'noir_brillant', 0.6, 0.3, cy=-0.2)  # tablet body
box(15.6, 0.15, 8.6, 0, -0.98, 6.4, 'ecran')                       # screen glass
for sx, mat in ((-1, 'joycon_bleu'), (1, 'joycon_rouge')):          # controllers on both sides
    rbox_v(3.4, 1.4, 10.2, 5.6, mat, 1.5, 0.3, cx=sx * (8.6 + 1.7), cy=-0.2)
    cyl(0.7, 0.4, sx * (8.6 + 1.7), -1.05, 13.0 if sx < 0 else 10.2, 'gris_fonce', 20, axis='Y')   # sticks
    for (dx, dz) in ((-0.6, 0), (0.6, 0), (0, 0.6), (0, -0.6)):
        cyl(0.28, 0.3, sx * (8.6 + 1.7) + dx, -1.0, (10.2 if sx < 0 else 13.0) + dz, 'gris_fonce', 12, axis='Y')
export('switch_dock', {'noir_mat': ((0.06, 0.06, 0.065), 0.15, 15, ''), 'noir_brillant': ((0.05, 0.05, 0.055), 0.5, 80, ''),
                       'gris_fonce': ((0.2, 0.2, 0.21), 0.2, 20, ''), 'ecran': ((0.02, 0.02, 0.03), 0.9, 120, ''),
                       'joycon_bleu': ((0.0, 0.65, 0.85), 0.3, 40, ''), 'joycon_rouge': ((0.95, 0.27, 0.22), 0.3, 40, '')})

# ============ XGIMI Horizon Pro on its floor stand (total 114 cm) ============
reset()
N = 512
yy, xx = np.mgrid[0:N, 0:N]
dots = ((np.sin(xx * 2 * np.pi / 6) * np.sin(yy * 2 * np.pi / 6)) > 0.35).astype(float)
img = np.array([0.20, 0.20, 0.21]) * (1 - 0.5 * dots)[..., None]
Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).save('/tmp/grille.png')
# stand : round base plate, black tube, silver collar, mounting head
rbox_v(26, 20, 1.4, 0, 'metal_noir', 6.0, 0.5)
cyl(1.6, 98.0, 0, 2.0, 1.4, 'metal_noir', 24)
cyl(1.75, 4.0, 0, 2.0, 52.0, 'alu', 24)
cyl(1.2, 1.5, 0, 2.0, 99.4, 'metal_noir', 16)
cyl(0.9, 1.6, 1.8, 2.0, 98.6, 'metal_noir', 12, axis='X')          # tightening knob
# projector 21 x 22.3 x 13.6 sitting on top (z 100.4)
Z = 100.4
rbox_v(21.0, 22.3, 1.0, Z, 'noir_mat', 4.5, 0.3)                   # bottom ring
body = rbox_v(21.2, 22.5, 10.0, Z + 1.0, 'grille', 4.6)             # speaker grille wrap
rbox_v(21.4, 22.7, 2.6, Z + 11.0, 'gris_metal', 4.8, 0.4)          # upper band
rbox_v(20.6, 21.9, 0.8, Z + 13.4, 'noir_brillant', 4.2, 0.3)       # glossy top
cyl(4.0, 1.2, -5.0, -11.3, Z + 7.0, 'alu', 48, axis='Y')            # lens ring
cyl(3.2, 0.8, -5.0, -11.8, Z + 7.0, 'lentille', 48, axis='Y')       # lens glass
cyl(1.8, 0.4, -5.0, -12.1, Z + 7.0, 'lentille_bleue', 32, axis='Y')
box(3.0, 0.3, 1.4, 1.5, -11.45, Z + 6.6, 'noir_brillant', 0.3)       # sensor pill
# grille UVs : cylindrical-ish box projection
bpy.ops.object.select_all(action='DESELECT'); body.select_set(True); bpy.context.view_layer.objects.active = body
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.cube_project(cube_size=8.0); bpy.ops.object.mode_set(mode='OBJECT')
export('videoprojecteur', {'metal_noir': ((0.07, 0.07, 0.075), 0.35, 45, ''), 'alu': ((0.75, 0.76, 0.77), 0.8, 90, ''),
                           'noir_mat': ((0.05, 0.05, 0.05), 0.15, 15, ''), 'grille': ((1, 1, 1), 0.1, 10, 'map_Kd grille.png\n'),
                           'gris_metal': ((0.22, 0.22, 0.23), 0.6, 70, ''), 'noir_brillant': ((0.04, 0.04, 0.045), 0.7, 100, ''),
                           'lentille': ((0.05, 0.06, 0.08), 0.95, 128, ''), 'lentille_bleue': ((0.15, 0.25, 0.45), 0.95, 128, '')},
       textures=['/tmp/grille.png'])
print('MEDIA OK')
