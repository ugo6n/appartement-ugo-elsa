"""Lit 140x190 : remplace la couette 'boîte' par une couette drapée (simulation de tissu), un revers et des oreillers moelleux.
Garde le cadre / sommier / matelas d'origine."""
import bpy, bmesh, math, sys, os
import numpy as np
from mathutils import Vector, Matrix
SRC, OUT = sys.argv[sys.argv.index('--') + 1:][:2]
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene

bpy.ops.wm.obj_import(filepath=f'{SRC}/model.obj')
bed = [o for o in sc.objects if o.type == 'MESH'][0]
bpy.context.view_layer.objects.active = bed; bed.select_set(True)
if len(sc.objects) > 1: bpy.ops.object.join()
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
# drop the old box duvet
bm = bmesh.new(); bm.from_mesh(bed.data)
idx = [i for i, m in enumerate(bed.data.materials) if m.name.startswith('couette')]
bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.material_index in idx], context='FACES')
bm.to_mesh(bed.data); bm.free()
# blender coords: x 0..152, y -203..-2 (head at y ~ -4, foot at y ~ -198), mattress top z = 38
X0, X1, YH, YF, ZT = 6, 146, -4, -198, 38.0
cx = (X0 + X1) / 2

# --- collision helpers ---
bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, (YH + YF) / 2, ZT / 2))
mat_box = bpy.context.active_object; mat_box.scale = (X1 - X0, YH - YF, ZT); bpy.ops.object.transform_apply(scale=True)
bv = mat_box.modifiers.new('b', 'BEVEL'); bv.width = 3; bv.segments = 3; bpy.ops.object.modifier_apply(modifier='b')
mat_box.modifiers.new('c', 'COLLISION'); mat_box.collision.thickness_outer = 0.5; mat_box.collision.cloth_friction = 60
bpy.ops.mesh.primitive_plane_add(size=600, location=(cx, -100, 0))
floor = bpy.context.active_object; floor.modifiers.new('c', 'COLLISION')

# --- pillows (made first so the duvet can drape against them a little) ---
def pillow(x, y, rot):
    me = bpy.data.meshes.new('pillow'); bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts: v.co = Vector((v.co.x * 64, v.co.y * 42, v.co.z * 16))
    bmesh.ops.bevel(bm, geom=list(bm.edges), offset=7, segments=5, affect='EDGES')
    bm.to_mesh(me); bm.free()
    p = bpy.data.objects.new('pillow', me); sc.collection.objects.link(p)
    bpy.ops.object.select_all(action='DESELECT'); p.select_set(True); bpy.context.view_layer.objects.active = p
    r = p.modifiers.new('r', 'REMESH'); r.voxel_size = 0.8; bpy.ops.object.modifier_apply(modifier='r')
    for v in p.data.vertices:
        u, w = v.co.x / 32, v.co.y / 21
        k = max(0.0, 1 - u * u) ** 0.6 * max(0.0, 1 - w * w) ** 0.6
        v.co.z = v.co.z * (0.25 + 0.85 * k)
    s_ = p.modifiers.new('s', 'SMOOTH'); s_.factor = 0.7; s_.iterations = 8; bpy.ops.object.modifier_apply(modifier='s')
    M = Matrix.Translation((x, y, ZT + 8)) @ Matrix.Rotation(math.radians(rot), 4, 'Z') @ Matrix.Rotation(math.radians(8), 4, 'X')
    me.transform(M)
    return p
pillows = [pillow(cx - 34, YH - 22, 3), pillow(cx + 34, YH - 23, -4)]
for p in pillows:
    import numpy as _n; c=_n.array([v.co[:] for v in p.data.vertices]); print("PILLOW", c.min(0).round(1), c.max(0).round(1))

# --- duvet : cloth simulation ---
DW, DL = 186.0, 168.0
bpy.ops.mesh.primitive_grid_add(x_subdivisions=90, y_subdivisions=80, size=1, location=(cx, YF + DL / 2 - 14, ZT + 6))
duv = bpy.context.active_object; duv.scale = (DW, DL, 1); bpy.ops.object.transform_apply(scale=True)
# a bit of initial randomness -> natural folds
rng = np.random.default_rng(4)
for v in duv.data.vertices:
    v.co.z += 0.6 * math.sin(v.co.x * 0.07 + 1.3) * math.sin(v.co.y * 0.05) + rng.normal(0, 0.05)
cl = duv.modifiers.new('cloth', 'CLOTH').settings
cl.quality = 10; cl.mass = 0.6; cl.tension_stiffness = 12; cl.compression_stiffness = 12
cl.shear_stiffness = 6; cl.bending_stiffness = 1.5; cl.air_damping = 6
duv.modifiers['cloth'].collision_settings.distance_min = 0.8
duv.modifiers['cloth'].collision_settings.use_self_collision = False
sc.gravity = (0, 0, -981)
sc.frame_start, sc.frame_end = 1, 70
duv.modifiers['cloth'].point_cache.frame_end = 70
for f in range(1, 71): sc.frame_set(f)
bpy.context.view_layer.objects.active = duv
bpy.ops.object.modifier_apply(modifier='cloth')
sol = duv.modifiers.new('s', 'SOLIDIFY'); sol.thickness = 3.5; sol.offset = 1
bpy.ops.object.modifier_apply(modifier='s')
sm = duv.modifiers.new('sm', 'SMOOTH'); sm.factor = 0.5; sm.iterations = 3; bpy.ops.object.modifier_apply(modifier='sm')

# --- turned-down top (revers) : soft roll across the bed ---
ytop = YF + DL - 14
bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=1, location=(cx, ytop + 3, 0), vertices=32)
roll = bpy.context.active_object
roll.data.transform(Matrix.Translation((cx, ytop + 3, 0)) @ Matrix.Rotation(math.radians(90), 4, 'Y') @ Matrix.Diagonal((5.5, 16, DW - 2, 1)))
roll.location = (0, 0, 0); roll.rotation_euler = (0, 0, 0); roll.scale = (1, 1, 1)
r = roll.modifiers.new('r', 'REMESH'); r.voxel_size = 0.8; bpy.ops.object.modifier_apply(modifier='r')
# follow the duvet surface (bend down over the sides)
dv = [v.co.copy() for v in duv.data.vertices]
import mathutils.kdtree as kd
tree = kd.KDTree(len(dv))
for i, c in enumerate(dv): tree.insert(Vector((c.x, c.y, 0)), i)
tree.balance()
for v in roll.data.vertices:
    co, i, d = tree.find(Vector((v.co.x, v.co.y, 0)))
    v.co.z += dv[i].z + 3.5 + 0.8 * math.sin(v.co.x * 0.11)
s = roll.modifiers.new('s', 'SMOOTH'); s.factor = 0.7; s.iterations = 6; bpy.ops.object.modifier_apply(modifier='s')

for o in (mat_box, floor): bpy.data.objects.remove(o)
import numpy as _n
for o in (duv, roll): c=_n.array([v.co[:] for v in o.data.vertices]); print("OBJ", o.name, c.min(0).round(1), c.max(0).round(1))

# --- textures : windowpane-check linen (same pattern as before, but soft & fabric-like) ---
N = 1024
def pn(f, seed):
    g = np.random.default_rng(seed); F = np.fft.fft2(g.standard_normal((N, N)))
    k = np.hypot(np.fft.fftfreq(N)[:, None] * N, np.fft.fftfreq(N)[None, :] * N)
    x = np.real(np.fft.ifft2(F * np.exp(-(k / f) ** 2))); return (x - x.mean()) / x.std()
yy, xx = np.mgrid[0:N, 0:N]
period = N / 5
def line(c):
    d = np.abs(((c + period / 2) % period) - period / 2)
    return np.exp(-(d / 3.2) ** 2)
wob = pn(4, 1) * 2.0
grid = np.maximum(line(xx + wob), line(yy + wob))
weave = 0.5 + 0.5 * np.sin(xx * 2 * np.pi / 3.0) * np.sin(yy * 2 * np.pi / 3.0)
slub = pn(300, 2)
base = np.array([0.935, 0.930, 0.905])
v = 1 + 0.025 * (weave - 0.5) + 0.02 * slub + 0.015 * pn(20, 3)
img = base * v[..., None]
img = img * (1 - 0.62 * grid[..., None]) + np.array([0.30, 0.30, 0.31]) * 0.62 * grid[..., None] * 0  # dark grey lines
img = np.clip(img, 0, 1)
from PIL import Image
Image.fromarray((img * 255).astype(np.uint8)).save(f'{OUT}/couette_lin.jpg', quality=92)

lin = bpy.data.materials.new('couette_lin'); lin.use_nodes = True
t = lin.node_tree.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(f'{OUT}/couette_lin.jpg')
lin.node_tree.links.new(t.outputs['Color'], lin.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
lin.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.9
for o in [duv] + pillows:
    o.data.materials.clear(); o.data.materials.append(lin)
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active = o
    bpy.ops.object.shade_smooth()
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.cube_project(cube_size=60.0)  # one grid tile = 60 cm -> squares of 12 cm
    bpy.ops.object.mode_set(mode='OBJECT')

bpy.ops.object.select_all(action='DESELECT')
bpy.data.objects.remove(roll)
for o in [bed, duv] + pillows: o.select_set(True)
bpy.context.view_layer.objects.active = bed; bpy.ops.object.join()
d = bed.modifiers.new('d', 'DECIMATE'); d.ratio = 0.5; bpy.ops.object.modifier_apply(modifier='d')
bpy.ops.wm.obj_export(filepath=f'{OUT}/model.obj', export_materials=True, path_mode='STRIP',
                      export_normals=True, export_uv=True, forward_axis='NEGATIVE_Z', up_axis='Y')
orig = open(f'{SRC}/model.mtl').read()
blocks = ['newmtl ' + b for b in orig.split('newmtl ')[1:] if not b.startswith('couette')]
open(f'{OUT}/model.mtl', 'w').write(''.join(blocks) +
    'newmtl couette_lin\nKa 0.2 0.2 0.2\nKd 1 1 1\nKs 0.02 0.02 0.02\nNs 3\nmap_Kd couette_lin.jpg\n')
import shutil; shutil.copy(f'{SRC}/chene.jpg', f'{OUT}/chene.jpg')
bpy.ops.wm.save_as_mainfile(filepath=f'{OUT}/bed.blend')
print('faces', len(bed.data.polygons), [m.name for m in bed.data.materials])
