"""Chaise Sklum Jolie (d'après photos) : assise ronde épaisse, dossier bandeau galbé, 4 pieds plats chêne clair.
50 W x 54 D x 74 H, assise 48. Front = -Y."""
import sys, os, math
src = open('/home/claude/scripts/make_items.py').read()
exec(src[:src.index("TEX = ")])
import numpy as np
from PIL import Image
reset()
D = os.path.join(OUT, 'chaise_jolie'); os.makedirs(D, exist_ok=True)

def sweep(path_pts, prof_fn, ring_n, mat, cap_shrink=0):
    """path_pts: list of (center Vector, normal-out Vector, up Vector); prof_fn(t)->(u,v) offsets in (normal, up)."""
    bm = bmesh.new(); rings = []
    n = len(path_pts)
    for i, (c, nrm, up) in enumerate(path_pts):
        s = 1.0
        if cap_shrink:
            e = min(i, n - 1 - i)
            if e < cap_shrink: s = math.sin(0.5 * math.pi * (e + 0.0001) / cap_shrink) ** 0.5
        ring = []
        for k in range(ring_n):
            u, v = prof_fn(k / ring_n)
            ring.append(bm.verts.new(c + nrm * (u * s) + up * (v * s)))
        rings.append(ring)
    for i in range(n - 1):
        for k in range(ring_n):
            bm.faces.new((rings[i][k], rings[i][(k + 1) % ring_n], rings[i + 1][(k + 1) % ring_n], rings[i + 1][k]))
    for r in (rings[0], rings[-1][::-1]):
        bm.faces.new(r[::-1] if r is rings[0] else r)
    me = bpy.data.meshes.new('sw'); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new('sw', me); bpy.context.collection.objects.link(o); me.materials.append(M(mat))
    for p in me.polygons: p.use_smooth = True
    return o

def rrect(w, h, r):
    """rounded rectangle perimeter param t in [0,1) -> (u, v), centred."""
    def f(t):
        a = 2 * math.pi * t
        cx, cy = math.cos(a), math.sin(a)
        # superellipse approximation of a rounded rectangle
        e = 2 / 6.0
        u = (w / 2) * math.copysign(abs(cx) ** e, cx)
        v = (h / 2) * math.copysign(abs(cy) ** e, cy)
        return u, v
    return f

SEAT_TOP, R_SEAT, TH = 48.0, 24.0, 10.5
CY = 1.5
# --- round seat cushion (disc with soft rounded edge) ---
path = []
for i in range(2):
    pass
bm = bmesh.new()
prof = []  # (r, z) around the edge, from bottom centre to top centre
for i in range(0, 13):
    a = -math.pi / 2 + math.pi * i / 12
    rr = 3.2
    prof.append((R_SEAT - rr + rr * math.cos(a), SEAT_TOP - TH / 2 + (TH / 2 - rr) * (1 if a > 0 else -1) + rr * math.sin(a)))
prof = [(0.0, SEAT_TOP - TH)] + [(R_SEAT - 3.2, SEAT_TOP - TH)] + prof + [(R_SEAT - 3.2, SEAT_TOP + 0.6), (0.0, SEAT_TOP + 1.2)]
SEG = 64; rings = []
for (r, z) in prof:
    rings.append([bm.verts.new((r * math.cos(2 * math.pi * k / SEG), CY + r * math.sin(2 * math.pi * k / SEG), z)) for k in range(SEG)])
for i in range(len(rings) - 1):
    for k in range(SEG):
        bm.faces.new((rings[i][k], rings[i + 1][k], rings[i + 1][(k + 1) % SEG], rings[i][(k + 1) % SEG]))
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.01)
me = bpy.data.meshes.new('seat'); bm.to_mesh(me); bm.free()
seat = bpy.data.objects.new('seat', me); bpy.context.collection.objects.link(seat); me.materials.append(M('chenille_creme'))
for p in me.polygons: p.use_smooth = True

# --- legs : flat rounded planks (5 x 3.2) hugging the seat ---
def leg(ang_deg, top, back_post=False):
    a = math.radians(ang_deg)
    rad = R_SEAT + 1.7
    base = Vector((rad * math.cos(a), CY + rad * math.sin(a), 0))
    nrm = Vector((math.cos(a), math.sin(a), 0))        # outward
    tan = Vector((-math.sin(a), math.cos(a), 0))
    pts = []
    zs = list(np.linspace(0, top, 24))
    for z in zs:
        c = base.copy(); c.z = z
        if back_post and z > SEAT_TOP:
            t = (z - SEAT_TOP) / (top - SEAT_TOP)
            c += nrm * (2.2 * t * t)                   # posts lean slightly backwards
        pts.append((c, tan, nrm))
    # sweep along vertical: section in plane (tan, nrm); we need path direction = Z, so build manually
    bm = bmesh.new(); rings = []
    f = rrect(5.2, 3.2, 1.0)
    for i, (c, t_, n_) in enumerate(pts):
        s = 1.0
        if i == len(pts) - 1: s = 0.92
        rings.append([bm.verts.new(c + t_ * (f(k / 20)[0] * s) + n_ * (f(k / 20)[1] * s)) for k in range(20)])
    top_c = pts[-1][0] + Vector((0, 0, 0.5))
    tc = bm.verts.new(top_c)
    for i in range(len(rings) - 1):
        for k in range(20):
            bm.faces.new((rings[i][k], rings[i][(k + 1) % 20], rings[i + 1][(k + 1) % 20], rings[i + 1][k]))
    for k in range(20):
        bm.faces.new((rings[-1][k], rings[-1][(k + 1) % 20], tc))
    bm.faces.new(rings[0][::-1])
    me = bpy.data.meshes.new('leg'); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new('leg', me); bpy.context.collection.objects.link(o); me.materials.append(M('chene_clair'))
    for p in me.polygons: p.use_smooth = True
    box(1.0, 1.0, 0.4, base.x, base.y, 0, 'patin')  # glide
    return base

BACK_TOP = 60.0
fl = leg(-125, SEAT_TOP - 0.5); fr = leg(-55, SEAT_TOP - 0.5)
bl = leg(122, BACK_TOP, True); br = leg(58, BACK_TOP, True)
# rails under the seat (round, connecting the legs)
zr = SEAT_TOP - TH - 1.5
for p0, p1 in ((fl, bl), (fr, br), (fl, fr), (bl, br)):
    tube((p0.x, p0.y, zr), (p1.x, p1.y, zr), 0.9, 'chene_clair', 12)

# --- backrest : curved upholstered band with rounded ends, in front of the posts ---
RB = 22.0; ZB = 64.5; HB = 20.0; TB = 7.0
path = []
for a in np.linspace(math.radians(18), math.radians(162), 60):
    nrm = Vector((math.cos(a), math.sin(a), 0))
    c = Vector((RB * math.cos(a), CY + RB * math.sin(a), ZB))
    path.append((c, nrm, Vector((0, 0, 1))))
back = sweep(path, rrect(TB, HB, 3.0), 32, 'chenille_creme', cap_shrink=6)

# textures
N = 512
def pn(fx, fy, seed):
    r = np.random.default_rng(seed); F = np.fft.fft2(r.standard_normal((N, N)))
    ky = np.fft.fftfreq(N)[:, None] * N; kx = np.fft.fftfreq(N)[None, :] * N
    x = np.real(np.fft.ifft2(F * np.exp(-(kx / fx) ** 2 - (ky / fy) ** 2))); return (x - x.mean()) / x.std()
v = 1 + 0.03 * pn(140, 140, 1) + 0.02 * pn(8, 8, 2) + 0.02 * pn(300, 40, 3)
Image.fromarray((np.clip(np.array([0.90, 0.88, 0.83]) * v[..., None], 0, 1) * 255).astype(np.uint8)).save(f'{D}/chenille_creme.jpg', quality=92)
y = np.arange(N)[None, :] / N
g = np.clip(np.sin(2 * np.pi * (y * 34 + 0.25 * pn(1.0, 6, 4))), 0, 1) ** 3
v = 1 - 0.07 * g + 0.035 * pn(3, 300, 5)
Image.fromarray((np.clip(np.array([0.80, 0.62, 0.42]) * v[..., None], 0, 1) * 255).astype(np.uint8)).save(f'{D}/chene_clair.jpg', quality=92)
for o in [ob for ob in bpy.data.objects if ob.type == 'MESH']:
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active = o
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.cube_project(cube_size=40.0); bpy.ops.object.mode_set(mode='OBJECT')
for m, img, rough in ((M('chenille_creme'), 'chenille_creme.jpg', 0.9), (M('chene_clair'), 'chene_clair.jpg', 0.45)):
    m.use_nodes = True; nt = m.node_tree; bs = nt.nodes['Principled BSDF']
    t = nt.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(f'{D}/{img}')
    nt.links.new(t.outputs['Color'], bs.inputs['Base Color']); bs.inputs['Roughness'].default_value = rough
bpy.ops.wm.obj_export(filepath=f'{D}/model.obj', export_materials=True, path_mode='STRIP',
                      export_normals=True, export_uv=True, forward_axis='NEGATIVE_Z', up_axis='Y')
open(f'{D}/model.mtl', 'w').write(
    'newmtl chenille_creme\nKa 0.2 0.2 0.2\nKd 1 1 1\nKs 0.03 0.03 0.03\nNs 4\nmap_Kd chenille_creme.jpg\n'
    'newmtl chene_clair\nKa 0.2 0.2 0.2\nKd 1 1 1\nKs 0.2 0.2 0.2\nNs 35\nmap_Kd chene_clair.jpg\n'
    'newmtl patin\nKa 0.2 0.2 0.2\nKd 0.05 0.05 0.05\nKs 0 0 0\nNs 1\n')
bpy.ops.wm.save_as_mainfile(filepath=f'{D}/chair.blend')
print('JOLIE OK')
