"""OMHU TEDDY 2-seater (200 x 100 x 70 cm, seat 34 cm) – puffy floor sofa, emerald teddy fabric.
Builds the mesh in Blender (cm units, front = -Y, up = Z) and exports an OBJ for Sweet Home 3D."""
import bpy, bmesh, math, sys, os
import numpy as np
from mathutils import Vector

OUTDIR = sys.argv[sys.argv.index('--') + 1]
os.makedirs(OUTDIR, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)

def rbox(name, size, loc, bevel, segs=8):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.active_object; o.name = name
    o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    m = o.modifiers.new('b', 'BEVEL'); m.width = bevel; m.segments = segs; m.limit_method = 'NONE'
    bpy.ops.object.modifier_apply(modifier='b')
    return o

def puff(o, voxel, smooth_iter, crease_z=None):
    r = o.modifiers.new('r', 'REMESH'); r.mode = 'VOXEL'; r.voxel_size = voxel
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.modifier_apply(modifier='r')
    s = o.modifiers.new('s', 'SMOOTH'); s.factor = 0.8; s.iterations = smooth_iter
    bpy.ops.object.modifier_apply(modifier='s')

def join(objs):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    return bpy.context.active_object

W, D, H, SEAT = 200.0, 100.0, 70.0, 34.0
T = 33.0  # thickness of back / arms

# --- base : two stacked mattresses, soft rounded edges ---
base = rbox('base', (W, D, SEAT + 1), (0, 0, (SEAT + 1) / 2), 10)
puff(base, 1.0, 12)
# puffy top + mattress seam crease at mid-height
bm = bmesh.new(); bm.from_mesh(base.data)
for v in bm.verts:
    x, y, z = v.co
    # seat dome : rises a little toward centre of the seat
    if z > SEAT - 6:
        fx = max(0.0, 1 - (abs(x) / (W / 2)) ** 4); fy = max(0.0, 1 - (abs(y + 8) / (D / 2)) ** 4)
        v.co.z += 1.8 * fx * fy
    # horizontal seam between the two mattresses
    dz = z - SEAT * 0.5
    if abs(dz) < 3.0:
        k = (1 - abs(dz) / 3.0) ** 2 * 1.6
        n = Vector((x, y, 0))
        if n.length > 1e-3:
            ex = abs(x) / (W / 2); ey = abs(y) / (D / 2)
            if max(ex, ey) > 0.9:
                v.co -= n.normalized() * k
bm.to_mesh(base.data); bm.free()

# --- U-shaped surround : back + two arms, very rounded "pillow" ---
z0 = SEAT - 4
hb = H - z0
back = rbox('back', (W, T, hb), (0, D / 2 - T / 2, z0 + hb / 2), 15, 10)
armL = rbox('armL', (T, D - 2, hb - 2), (-(W / 2 - T / 2), 1, z0 + (hb - 2) / 2), 15, 10)
armR = rbox('armR', (T, D - 2, hb - 2), ((W / 2 - T / 2), 1, z0 + (hb - 2) / 2), 15, 10)
u = join([back, armL, armR])
puff(u, 1.0, 25)
# inflate a bit (pillow look) + fold where arms meet back
bm = bmesh.new(); bm.from_mesh(u.data)
bm.normal_update()
for v in bm.verts:
    x, y, z = v.co
    v.co += v.normal * 0.8
    # soft vertical dent at the arm/back junction (inside)
    for sx in (-1, 1):
        cx, cy = sx * (W / 2 - T), D / 2 - T
        d = math.hypot(x - cx, y - cy)
        if d < 6: v.co -= v.normal * (6 - d) * 0.35
bm.to_mesh(u.data); bm.free()

sofa = join([base, u])
# fabric micro-puffiness
tex = bpy.data.textures.new('n', 'CLOUDS'); tex.noise_scale = 18
dm = sofa.modifiers.new('d', 'DISPLACE'); dm.texture = tex; dm.strength = 0.6; dm.mid_level = 0.5
bpy.ops.object.modifier_apply(modifier='d')
dec = sofa.modifiers.new('dec', 'DECIMATE'); dec.ratio = 0.2
bpy.ops.object.modifier_apply(modifier='dec')
bpy.ops.object.shade_smooth()

# UVs : box projection, fabric texture repeats every 25 cm
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.cube_project(cube_size=25.0)
bpy.ops.object.mode_set(mode='OBJECT')

# --- emerald teddy fabric texture (tileable) ---
N = 1024
rng = np.random.default_rng(3)
def pnoise(f, seed):
    r = np.random.default_rng(seed); w = r.standard_normal((N, N)); F = np.fft.fft2(w)
    k = np.hypot(np.fft.fftfreq(N)[:, None] * N, np.fft.fftfreq(N)[None, :] * N)
    n = np.real(np.fft.ifft2(F * np.exp(-(k / f) ** 2))); return (n - n.mean()) / n.std()
curls = pnoise(90, 1); fine = pnoise(300, 2); soft = pnoise(8, 3)
tips = np.clip(curls, 0, None) ** 1.5
col = np.array([0.070, 0.330, 0.255])          # émeraude (sRGB)
v = 1.0 + 0.09 * tips - 0.06 * np.clip(-curls, 0, None) + 0.03 * fine + 0.03 * soft
img = np.clip(col[None, None, :] * v[..., None], 0, 1)
img[..., 1] += 0.025 * tips; img = np.clip(img, 0, 1)
from PIL import Image
Image.fromarray((img * 255).astype(np.uint8)).save(os.path.join(OUTDIR, 'teddy_emeraude.jpg'), quality=92)

m = bpy.data.materials.new('teddy_emeraude'); m.use_nodes = True
nt = m.node_tree; b = nt.nodes['Principled BSDF']
ti = nt.nodes.new('ShaderNodeTexImage'); ti.image = bpy.data.images.load(os.path.join(OUTDIR, 'teddy_emeraude.jpg'))
nt.links.new(ti.outputs['Color'], b.inputs['Base Color'])
b.inputs['Roughness'].default_value = 0.85
b.inputs['Sheen Weight'].default_value = 0.6
b.inputs['Sheen Tint'].default_value = (0.6, 0.95, 0.8, 1)
sofa.data.materials.clear(); sofa.data.materials.append(m)
sofa.name = 'teddy'
print('faces', len(sofa.data.polygons))

bpy.ops.wm.obj_export(filepath=os.path.join(OUTDIR, 'model.obj'), export_selected_objects=False,
                      export_materials=True, path_mode='STRIP', export_normals=True, export_uv=True,
                      forward_axis='NEGATIVE_Z', up_axis='Y')
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUTDIR, 'teddy.blend'))
