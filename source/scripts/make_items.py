"""Builds several furniture models (cm units, front = -Y, up = Z) and exports each as OBJ+MTL folder."""
import bpy, bmesh, math, sys, os, shutil
import numpy as np
from mathutils import Vector, Matrix
from PIL import Image
OUT = sys.argv[sys.argv.index('--') + 1]

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def M(name):
    return bpy.data.materials.get(name) or bpy.data.materials.new(name)

def box(sx, sy, sz, cx, cy, z0, mat, bevel=0.0, segs=2):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * sx + cx, v.co.y * sy + cy, v.co.z * sz + z0 + sz / 2))
    if bevel > 0:
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=bevel, segments=segs, affect='EDGES')
    me = bpy.data.meshes.new('b'); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new('b', me); bpy.context.collection.objects.link(o); me.materials.append(M(mat))
    return o

def cyl(r, h, cx, cy, z0, mat, verts=32, r2=None, axis='Z'):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=verts, radius1=r, radius2=r if r2 is None else r2, depth=h)
    me = bpy.data.meshes.new('c'); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new('c', me); bpy.context.collection.objects.link(o); me.materials.append(M(mat))
    R = {'Z': Matrix(), 'X': Matrix.Rotation(math.pi / 2, 4, 'Y'), 'Y': Matrix.Rotation(math.pi / 2, 4, 'X')}[axis]
    me.transform(Matrix.Translation((cx, cy, z0 + (h / 2 if axis == 'Z' else 0))) @ R)
    for p in me.polygons: p.use_smooth = True
    return o

def tube(p0, p1, r, mat, verts=12, square=False):
    p0, p1 = Vector(p0), Vector(p1); d = p1 - p0
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=4 if square else verts, radius1=r, radius2=r, depth=d.length)
    me = bpy.data.meshes.new('t'); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new('t', me); bpy.context.collection.objects.link(o); me.materials.append(M(mat))
    rot = d.to_track_quat('Z', 'Y').to_matrix().to_4x4()
    if square: rot = rot @ Matrix.Rotation(math.pi / 4, 4, 'Z')
    me.transform(Matrix.Translation((p0 + p1) / 2) @ rot)
    if not square:
        for p in me.polygons: p.use_smooth = True
    return o

def export(folder, mtls, textures=()):
    d = os.path.join(OUT, folder); shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    objs = [o for o in bpy.data.objects if o.type == 'MESH']
    for o in objs:
        if not o.data.uv_layers:
            bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active = o
            bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.uv.cube_project(cube_size=60.0); bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.wm.obj_export(filepath=os.path.join(d, 'model.obj'), export_materials=True, path_mode='STRIP',
                          export_normals=True, export_uv=True, forward_axis='NEGATIVE_Z', up_axis='Y')
    txt = ''
    for name, (kd, ks, ns, extra) in mtls.items():
        txt += f'newmtl {name}\nKa 0.2 0.2 0.2\nKd {kd[0]:.3f} {kd[1]:.3f} {kd[2]:.3f}\nKs {ks} {ks} {ks}\nNs {ns}\n{extra}'
    open(os.path.join(d, 'model.mtl'), 'w').write(txt)
    for t in textures: shutil.copy(t, d)
    # preview materials for Blender (so the .blend scene looks right too)
    print('exported', folder)

def oak_texture(path, base=(0.80, 0.66, 0.48)):
    N = 1024; r = np.random.default_rng(11)
    def pn(fx, fy, s):
        g = np.random.default_rng(s); F = np.fft.fft2(g.standard_normal((N, N)))
        ky = np.fft.fftfreq(N)[:, None] * N; kx = np.fft.fftfreq(N)[None, :] * N
        x = np.real(np.fft.ifft2(F * np.exp(-(kx / fx) ** 2 - (ky / fy) ** 2))); return (x - x.mean()) / x.std()
    y = np.arange(N)[:, None] / N
    lines = np.clip(np.sin(2 * np.pi * (y * 30 + 0.8 * pn(1.5, 6, 1))), 0, 1) ** 4
    v = 1 - 0.10 * lines - 0.04 * np.clip(pn(5, 400, 2), -2, 2) + 0.03 * pn(3, 6, 3)
    img = np.clip(np.array(base) * v[..., None], 0, 1)
    Image.fromarray((img * 255).astype(np.uint8)).save(path, quality=92)

TEX = os.path.join(OUT, '_tex'); os.makedirs(TEX, exist_ok=True)
oak_texture(f'{TEX}/chene_clair.jpg')

WHITE = ((0.93, 0.93, 0.92), 0.15, 20, '')

# ---------------- 1. IKEA LAGKAPTEN / ALEX desk 120 x 60 x 73 ----------------
reset()
box(120, 60, 2.6, 0, 0, 70.4, 'blanc_plateau', bevel=0.3)
# ALEX drawer unit 36 x 58 x 70 on the left, 5 drawers of different heights
ax = -60 + 18 + 1
box(36, 58, 70, ax, 0.5, 0, 'blanc', bevel=0.2)
hs = [16.6, 16.6, 16.6, 9.6, 9.6]; z = 1.0
for h in hs:  # drawer fronts slightly proud, with grip cut-out shadow at the top
    box(35.4, 1.2, h - 0.5, ax, -29.0, z, 'blanc', bevel=0.15)
    box(14, 0.4, 1.4, ax, -29.65, z + h - 2.6, 'gris_ombre')
    z += h
# ADILS legs (2) on the right
for y in (-26, 26):
    cyl(1.6, 70.4, 56, y, 0, 'blanc_metal', 24)
    cyl(1.8, 1.0, 56, y, 0, 'gris_ombre', 24)
export('bureau', {'blanc_plateau': WHITE, 'blanc': WHITE, 'blanc_metal': ((0.92, 0.92, 0.91), 0.4, 60, ''),
                  'gris_ombre': ((0.35, 0.35, 0.36), 0.1, 10, '')})

# ---------------- 2. IKEA LOBERGET / MALSKÄR swivel chair ----------------
reset()
# shell : swept surface along a profile (seat -> curved back), width tapering
prof = []
for i in range(14):            # seat, front lip curving down
    t = i / 13; y = -22 + 38 * t; z = 0.0
    if t < 0.15: z = -3.5 * (1 - t / 0.15) ** 2
    prof.append((y, z))
for i in range(1, 12):         # rounded transition into the back
    a = math.radians(90 * i / 11); prof.append((16 + 9 * math.sin(a), 9 * (1 - math.cos(a))))
for i in range(1, 12):         # backrest, slightly reclined
    t = i / 11; prof.append((25 + 6 * t, 9 + 33 * t))
NW = 24
bm = bmesh.new(); rows = []
for j, (py, pz) in enumerate(prof):
    s = j / (len(prof) - 1)
    hw = 22 - 3 * s if s < 0.7 else 19 * math.cos((s - 0.7) / 0.3 * 0.9) + 0.0
    hw = max(hw, 12.5)
    row = []
    for k in range(NW + 1):
        u = -1 + 2 * k / NW
        curl = 2.5 * u ** 4                 # edges curl up -> hollow shell
        row.append(bm.verts.new((u * hw, py - (curl * 0.6 if s > 0.5 else 0), pz + (curl if s <= 0.5 else 0))))
    rows.append(row)
for j in range(len(rows) - 1):
    for k in range(NW):
        bm.faces.new((rows[j][k], rows[j][k + 1], rows[j + 1][k + 1], rows[j + 1][k]))
me = bpy.data.meshes.new('shell'); bm.to_mesh(me); bm.free()
shell = bpy.data.objects.new('shell', me); bpy.context.collection.objects.link(shell)
me.materials.append(M('pp_blanc'))
me.transform(Matrix.Translation((0, 0, 47)))
bpy.context.view_layer.objects.active = shell; shell.select_set(True)
sol = shell.modifiers.new('s', 'SOLIDIFY'); sol.thickness = 1.2; sol.offset = 0
bpy.ops.object.modifier_apply(modifier='s')
sub = shell.modifiers.new('sub', 'SUBSURF'); sub.levels = 1; bpy.ops.object.modifier_apply(modifier='sub')
for p in me.polygons: p.use_smooth = True
# base : gas column + 5-star base + castors (all white)
cyl(3.0, 4, 0, 0, 41.5, 'blanc_metal', 24)                       # seat mechanism
cyl(2.5, 30, 0, 0, 12, 'blanc_metal', 24)                       # gas column
cyl(4.0, 4, 0, 0, 9, 'blanc_metal', 24)
for i in range(5):
    a = 2 * math.pi * i / 5 - math.pi / 2
    end = (31 * math.cos(a), 31 * math.sin(a), 6.5)
    tube((0, 0, 10.5), end, 2.0, 'blanc_metal', 10)
    cyl(1.0, 2.5, end[0], end[1], 4.5, 'blanc_metal', 12)
    cyl(2.6, 4.0, end[0], end[1], 2.6, 'roulette', 20, axis='X')   # castor wheel
export('chaise_bureau', {'pp_blanc': ((0.94, 0.94, 0.93), 0.25, 30, ''),
                         'blanc_metal': ((0.92, 0.92, 0.91), 0.4, 60, ''),
                         'roulette': ((0.85, 0.85, 0.84), 0.2, 20, '')})

# ---------------- 3. Componibili-style round storage, 2 modules, Ø32 x 40 ----------------
reset()
R = 16
cyl(R - 0.6, 1.2, 0, 0, 0, 'plastique_vert', 64)            # base
for k in range(2):
    z0 = 1.2 + k * 19
    cyl(R, 18.4, 0, 0, z0, 'plastique_vert', 64)             # module body
    cyl(R - 0.3, 0.6, 0, 0, z0 + 18.4, 'plastique_vert_ombre', 64)  # joint groove
    # sliding door : thin curved panel in front (front = -Y)
    bm = bmesh.new(); rows = []
    for zz in (z0 + 1.2, z0 + 17.2):
        rows.append([bm.verts.new(((R + 0.15) * math.cos(a), -(R + 0.15) * math.sin(a), zz))
                     for a in np.linspace(math.radians(35), math.radians(145), 24)])
    for i in range(23):
        bm.faces.new((rows[0][i], rows[0][i + 1], rows[1][i + 1], rows[1][i]))
    me = bpy.data.meshes.new('door'); bm.to_mesh(me); bm.free()
    door = bpy.data.objects.new('door', me); bpy.context.collection.objects.link(door); me.materials.append(M('plastique_vert'))
    for p in me.polygons: p.use_smooth = True
    # finger holes (3 small dark discs near the door edge)
    for j in range(3):
        a = math.radians(42); zz = z0 + 6 + j * 3.2
        cyl(0.9, 0.3, (R + 0.25) * math.cos(a), -(R + 0.25) * math.sin(a), zz, 'plastique_vert_ombre', 16, axis='Y')
cyl(R, 0.8, 0, 0, 39.2, 'plastique_vert', 64)                # top lid
export('babel', {'plastique_vert': ((0.36, 0.52, 0.27), 0.45, 90, ''),
                 'plastique_vert_ombre': ((0.15, 0.24, 0.11), 0.2, 30, '')})

# ---------------- 4. Beko DVN06431A dishwasher (anthracite) 59.8 x 60 x 85 ----------------
reset()
box(59.8, 58, 85, 0, 1, 0, 'anthracite', bevel=0.3)
box(59.6, 2.2, 74, 0, -29.2, 9, 'anthracite_porte', bevel=0.4)         # door
box(59.6, 2.2, 8.5, 0, -29.2, 0.3, 'anthracite', bevel=0.3)             # plinth
box(56, 0.4, 5.5, 0, -30.4, 77, 'noir_brillant', bevel=0.2)              # control panel strip
for i in range(6):
    cyl(0.6, 0.3, -20 + i * 5, -30.65, 79.7, 'gris_symbole', 12, axis='Y')
box(9, 0.3, 1.4, 18, -30.65, 79.0, 'led_bleu')
box(30, 1.2, 1.5, 0, -30.8, 73.0, 'anthracite_poignee', bevel=0.4)      # recessed handle lip
export('lave_vaisselle', {'anthracite': ((0.18, 0.19, 0.2), 0.3, 40, ''),
                          'anthracite_porte': ((0.21, 0.22, 0.23), 0.45, 70, ''),
                          'anthracite_poignee': ((0.12, 0.12, 0.13), 0.3, 40, ''),
                          'noir_brillant': ((0.03, 0.03, 0.035), 0.8, 110, ''),
                          'gris_symbole': ((0.75, 0.75, 0.76), 0.2, 20, ''),
                          'led_bleu': ((0.45, 0.75, 1.0), 0.5, 50, '')})

# ---------------- 5. Fridge LISTO RDL130-50hob5 : 50 x 58 x 123, white, freezer on top ----------------
reset()
box(50, 54, 122, 0, 2, 1, 'blanc_frigo', bevel=0.8, segs=3)
box(49.6, 4, 37.6, 0, -27, 84.6, 'blanc_frigo', bevel=1.0, segs=3)     # freezer door (top)
box(49.6, 4, 82.6, 0, -27, 1.4, 'blanc_frigo', bevel=1.0, segs=3)      # fridge door
box(46, 0.6, 1.2, 0, -29.2, 83.6, 'gris_joint')                          # gap shadow between doors
box(44, 0.5, 1.0, 0, -29.15, 84.2, 'gris_joint')
for zz in (84.2, 121.6):                                                 # hidden handle grooves (top edges of doors)
    box(30, 1.0, 0.8, 0, -29.0, zz - 1.4, 'gris_joint')
cyl(1.2, 1.0, -20, -25, 0, 'noir', 12); cyl(1.2, 1.0, 20, -25, 0, 'noir', 12)
export('frigo', {'blanc_frigo': ((0.95, 0.95, 0.94), 0.35, 60, ''),
                 'gris_joint': ((0.55, 0.56, 0.57), 0.1, 10, ''),
                 'noir': ((0.05, 0.05, 0.05), 0.1, 10, '')})

# ---------------- 6. IKEA SKÄLSTA table 140 x 80 x 75, oak top, U-shaped black-grey legs ----------------
reset()
top = box(140, 80, 3.2, 0, 0, 71.8, 'chene_motif', bevel=0.25)
# U-shaped legs: inverted U frames at each end (rectangular tube 6 x 2.5)
for sx in (-1, 1):
    x = sx * 56
    for y in (-35, 35):
        box(2.5, 5.0, 69.5, x, y, 0, 'acier_noir_gris', bevel=0.3)       # uprights
    box(2.5, 75, 5.0, x, 0, 66.8, 'acier_noir_gris', bevel=0.3)          # top rail under the tabletop
    for y in (-35, 35):
        box(2.6, 5.1, 0.6, x, y, 0, 'patin_noir')
bpy.ops.object.select_all(action='DESELECT'); top.select_set(True); bpy.context.view_layer.objects.active = top
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.cube_project(cube_size=140.0); bpy.ops.object.mode_set(mode='OBJECT')
export('table_skalsta', {'chene_motif': ((1, 1, 1), 0.12, 25, 'map_Kd chene_clair.jpg\n'),
                         'acier_noir_gris': ((0.13, 0.13, 0.14), 0.35, 50, ''),
                         'patin_noir': ((0.05, 0.05, 0.05), 0.1, 10, '')},
       textures=[f'{TEX}/chene_clair.jpg'])
print('ALL DONE')
