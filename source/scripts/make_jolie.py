"""Chaise Sklum Jolie – chenille beige crème, structure fer imitation bois. 50 W x 54 D x 74 H cm, assise 48 cm.
Front = -Y, up = Z, cm units."""
import bpy, bmesh, math, sys, os
import numpy as np
from mathutils import Vector
OUT = sys.argv[sys.argv.index('--') + 1]; os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)

fab = bpy.data.materials.new('chenille_creme')
wood = bpy.data.materials.new('fer_imitation_bois')

def finish(o, m, voxel=None, smooth=0):
    bpy.context.view_layer.objects.active = o; o.select_set(True)
    if voxel:
        r = o.modifiers.new('r', 'REMESH'); r.mode = 'VOXEL'; r.voxel_size = voxel
        bpy.ops.object.modifier_apply(modifier='r')
    if smooth:
        s = o.modifiers.new('s', 'SMOOTH'); s.factor = 0.8; s.iterations = smooth
        bpy.ops.object.modifier_apply(modifier='s')
    o.data.materials.clear(); o.data.materials.append(m)
    bpy.ops.object.shade_smooth()
    return o

parts = []
# seat cushion : soft rounded square, slightly domed
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -2, 43.5))
seat = bpy.context.active_object; seat.scale = (48, 46, 9); bpy.ops.object.transform_apply(scale=True)
b = seat.modifiers.new('b', 'BEVEL'); b.width = 4.0; b.segments = 6; b.limit_method = 'NONE'
bpy.ops.object.modifier_apply(modifier='b')
finish(seat, fab, 0.5, 10)
for v in seat.data.vertices:
    if v.co.z > 46:
        f = max(0, 1 - (abs(v.co.x) / 24) ** 4) * max(0, 1 - (abs(v.co.y + 2) / 23) ** 4)
        v.co.z += 1.0 * f
parts.append(seat)

# backrest : curved cylindrical bolster (horseshoe) floating above the seat
cu = bpy.data.curves.new('arc', 'CURVE'); cu.dimensions = '3D'
sp = cu.splines.new('POLY'); n = 40
a0, a1 = math.radians(12), math.radians(168)
sp.points.add(n - 1)
R, cy, zb = 21.0, 1.0, 67.0
for i in range(n):
    a = a0 + (a1 - a0) * i / (n - 1)
    sp.points[i].co = (R * math.cos(a), cy + R * math.sin(a), zb, 1)
cu.bevel_depth = 6.5; cu.bevel_resolution = 6; cu.use_fill_caps = True
arc = bpy.data.objects.new('back', cu); bpy.context.collection.objects.link(arc)
bpy.context.view_layer.objects.active = arc; arc.select_set(True)
bpy.ops.object.convert(target='MESH')
finish(arc, fab, 0.5, 14)   # remesh rounds the cylinder ends
parts.append(arc)

# metal frame (wood look) : 4 tapered legs + 2 back posts + seat rails
def tube(p0, p1, r0, r1, verts=16):
    p0, p1 = Vector(p0), Vector(p1); d = p1 - p0
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r0, radius2=r1, depth=d.length, location=(p0 + p1) / 2)
    o = bpy.context.active_object
    o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    bpy.ops.object.transform_apply(rotation=True)
    return finish(o, wood)
for sx in (-1, 1):
    for sy, ty in ((-1, -20), (1, 18)):
        parts.append(tube((sx * 21.5, sy * 22.5 - 1 if sy > 0 else -23.5, 0), (sx * 19.5, ty, 39.2), 1.1, 1.5))
    # back post: from the rear of the seat up into the bolster
    a = math.radians(40 if sx > 0 else 140)
    px, py = R * math.cos(a), cy + R * math.sin(a)
    parts.append(tube((px, py, 46), (px, py, zb - 2), 1.0, 1.0))
# seat frame (thin rails under the cushion)
for p0, p1 in [((-19.5, -20, 38.7), (19.5, -20, 38.7)), ((-19.5, 18, 38.7), (19.5, 18, 38.7)),
               ((-19.5, -20, 38.7), (-19.5, 18, 38.7)), ((19.5, -20, 38.7), (19.5, 18, 38.7))]:
    parts.append(tube(p0, p1, 0.9, 0.9, 10))

bpy.ops.object.select_all(action='DESELECT')
for o in parts: o.select_set(True)
bpy.context.view_layer.objects.active = parts[0]; bpy.ops.object.join()
chair = bpy.context.active_object
dec = chair.modifiers.new('d', 'DECIMATE'); dec.ratio = 0.35; bpy.ops.object.modifier_apply(modifier='d')
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.cube_project(cube_size=12.0); bpy.ops.object.mode_set(mode='OBJECT')

# textures
N = 512
def pn(fx, fy, seed):
    r = np.random.default_rng(seed); F = np.fft.fft2(r.standard_normal((N, N)))
    ky = np.fft.fftfreq(N)[:, None] * N; kx = np.fft.fftfreq(N)[None, :] * N
    x = np.real(np.fft.ifft2(F * np.exp(-(kx / fx) ** 2 - (ky / fy) ** 2))); return (x - x.mean()) / x.std()
from PIL import Image
# chenille : soft velvety ribs + fluff
y = np.arange(N)[:, None]
ribs = 0.5 + 0.5 * np.sin(2 * np.pi * y * 40 / N + 0.6 * pn(3, 3, 1))
v = 1 + 0.05 * (ribs - 0.5) + 0.035 * pn(120, 120, 2) + 0.02 * pn(10, 10, 3)
c = np.array([0.88, 0.82, 0.72])
Image.fromarray((np.clip(c * v[..., None], 0, 1) * 255).astype(np.uint8)).save(f'{OUT}/chenille_creme.jpg', quality=92)
# wood imitation
g = np.sin(2 * np.pi * (np.arange(N)[None, :] * 14 / N + 0.8 * pn(1.5, 6, 4))) * 0.5 + 0.5
v = 1 - 0.18 * g ** 3 + 0.05 * pn(4, 200, 5)
c = np.array([0.55, 0.38, 0.24])
Image.fromarray((np.clip(c * v[..., None], 0, 1) * 255).astype(np.uint8)).save(f'{OUT}/bois.jpg', quality=92)

for m, img in ((fab, 'chenille_creme.jpg'), (wood, 'bois.jpg')):
    m.use_nodes = True; nt = m.node_tree; bs = nt.nodes['Principled BSDF']
    t = nt.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(f'{OUT}/{img}')
    nt.links.new(t.outputs['Color'], bs.inputs['Base Color'])
    bs.inputs['Roughness'].default_value = 0.8 if m is fab else 0.4
    if m is fab: bs.inputs['Sheen Weight'].default_value = 0.5

bpy.ops.wm.obj_export(filepath=f'{OUT}/model.obj', export_materials=True, path_mode='STRIP',
                      export_normals=True, export_uv=True, forward_axis='NEGATIVE_Z', up_axis='Y')
open(f'{OUT}/model.mtl', 'w').write(
    'newmtl chenille_creme\nKa 0.2 0.2 0.2\nKd 1 1 1\nKs 0.04 0.04 0.04\nNs 5\nmap_Kd chenille_creme.jpg\n'
    'newmtl fer_imitation_bois\nKa 0.2 0.2 0.2\nKd 1 1 1\nKs 0.25 0.22 0.2\nNs 40\nmap_Kd bois.jpg\n')
bpy.ops.wm.save_as_mainfile(filepath=f'{OUT}/chair.blend')
print('faces', len(chair.data.polygons))
