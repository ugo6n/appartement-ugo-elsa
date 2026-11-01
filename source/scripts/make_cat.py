"""Litière CATLINK Open-X (avec dessus) 58.5 x 53.4 x 59.2 + arbre à chat Leeby Marcelo 39 x 38.5 x 85.5. Front = -Y."""
import sys, os, math
src = open('/home/claude/scripts/make_items.py').read()
exec(src[:src.index("TEX = ")])
import numpy as np
from PIL import Image

def rbox_mesh(sx, sy, sz, cx, cy, z0, mat, r, segs=4):
    o = box(sx, sy, sz, cx, cy, z0, mat, bevel=r, segs=segs)
    for p in o.data.polygons: p.use_smooth = True
    return o

def ring(r_out, r_in, h, cx, cy, z0, mat, segs=64):
    bm = bmesh.new(); rings = []
    prof = [(r_in, z0), (r_out, z0), (r_out, z0 + h), (r_in, z0 + h)]
    for r, z in prof:
        rings.append([bm.verts.new((cx + r * math.cos(2 * math.pi * k / segs), cy + r * math.sin(2 * math.pi * k / segs), z)) for k in range(segs)])
    for i in range(4):
        a, b = rings[i], rings[(i + 1) % 4]
        for k in range(segs): bm.faces.new((a[k], a[(k + 1) % segs], b[(k + 1) % segs], b[k]))
    me = bpy.data.meshes.new('r'); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new('r', me); bpy.context.collection.objects.link(o); me.materials.append(M(mat))
    for p in me.polygons: p.use_smooth = True
    return o

# ================= Litière CATLINK Open-X =================
reset()
L, Wd, H = 53.4, 58.5, 59.2        # width (x), depth (y), height
for sx in (-1, 1):
    for sy in (-1, 1):
        cyl(2.0, 2.0, sx * (L / 2 - 6), sy * (Wd / 2 - 6), 0, 'gris_fonce', 20)      # 4 feet
rbox_mesh(L, Wd, 16, 0, 0, 2, 'gris_fonce', 3.5)                                  # base
rbox_mesh(L - 1, 2, 9, 0, -Wd / 2 + 0.6, 5, 'gris_moyen', 1.2)                    # waste drawer front
box(16, 1.2, 1.6, 0, -Wd / 2 - 0.6, 11.5, 'gris_fonce', 0.4)                      # drawer grip
body = rbox_mesh(L, Wd - 1, H - 18 - 6, 0, 0.5, 17.5, 'blanc', 7.0, 6)           # white drum housing
# large front opening (dark rounded window) with litter inside
rbox_mesh(38, 1.0, 22, 0, -Wd / 2 + 0.2, 22, 'gris_fonce', 5.0, 6)               # opening rim
rbox_mesh(35, 1.0, 19, 0, -Wd / 2 - 0.1, 23.5, 'interieur', 4.5, 6)               # interior shadow
box(34, 18, 2.0, 0, -Wd / 2 + 9, 24.0, 'litiere')                                # litter bed seen inside
box(33, 0.6, 1.2, 0, -Wd / 2 - 0.5, 22.7, 'gris_moyen')                          # step lip
# top cover ("dessus")
rbox_mesh(L - 0.5, Wd - 1.5, 6.5, 0, 0.5, H - 6.5, 'blanc', 3.0, 5)
cyl(1.6, 0.4, 0, -Wd / 2 + 6, H, 'gris_moyen', 24)                               # button on top
box(6, 0.3, 1.2, 0, -Wd / 2 + 0.8, H - 4.0, 'led_bleu')                          # status LED
N = 256; g = np.random.default_rng(3).random((N, N))
Image.fromarray((np.clip(np.array([0.80, 0.74, 0.62]) * (0.85 + 0.3 * g)[..., None], 0, 1) * 255).astype(np.uint8)).save('/tmp/litiere.jpg')
export('litiere_catlink', {'blanc': ((0.94, 0.94, 0.93), 0.3, 50, ''), 'gris_fonce': ((0.24, 0.25, 0.26), 0.2, 30, ''),
                           'gris_moyen': ((0.55, 0.56, 0.57), 0.2, 30, ''), 'interieur': ((0.12, 0.12, 0.13), 0.1, 10, ''),
                           'litiere': ((1, 1, 1), 0.0, 1, 'map_Kd litiere.jpg\n'), 'led_bleu': ((0.4, 0.7, 1.0), 0.3, 30, '')},
       textures=['/tmp/litiere.jpg'])

# ================= Arbre à chat Leeby Marcelo =================
reset()
W, D = 39.0, 38.5
# plush and sisal textures
N = 512
def pn(f, s):
    r = np.random.default_rng(s); F = np.fft.fft2(r.standard_normal((N, N)))
    k = np.hypot(np.fft.fftfreq(N)[:, None] * N, np.fft.fftfreq(N)[None, :] * N)
    x = np.real(np.fft.ifft2(F * np.exp(-(k / f) ** 2))); return (x - x.mean()) / x.std()
pl = np.array([0.30, 0.36, 0.47]) * (1 + 0.10 * pn(30, 1) + 0.06 * pn(200, 2) + 0.05 * pn(5, 3))[..., None]
Image.fromarray((np.clip(pl, 0, 1) * 255).astype(np.uint8)).save('/tmp/peluche_bleue.jpg')
yy = np.arange(N)[:, None]
rope = 0.5 + 0.5 * np.sin(2 * np.pi * yy * 48 / N + 0.3 * pn(4, 4))
si = np.array([0.88, 0.85, 0.74]) * (0.88 + 0.16 * rope + 0.05 * pn(250, 5))[..., None] * np.ones((1, N, 1))
Image.fromarray((np.clip(si, 0, 1) * 255).astype(np.uint8)).save('/tmp/sisal.jpg')
xx = np.arange(N)[None, :]
weave = 0.5 + 0.25 * (np.sin(2 * np.pi * xx * 60 / N) + np.sin(2 * np.pi * yy * 60 / N))
jt = np.array([0.86, 0.83, 0.72]) * (0.85 + 0.2 * weave + 0.05 * pn(250, 6))[..., None]
Image.fromarray((np.clip(jt, 0, 1) * 255).astype(np.uint8)).save('/tmp/toile_sisal.jpg')

rbox_mesh(W, D, 2.2, 0, 0, 0, 'peluche', 0.8)                                    # base board
def post(x, y, z0, z1, r=4.2, sisal=(None, None)):
    if sisal[0] is None:
        cyl(r, z1 - z0, x, y, z0, 'peluche', 32)
    else:
        cyl(r, sisal[0] - z0, x, y, z0, 'peluche', 32)
        cyl(r - 0.2, sisal[1] - sisal[0], x, y, sisal[0], 'sisal', 32)
        cyl(r, z1 - sisal[1], x, y, sisal[1], 'peluche', 32)
PZ = 45.0                                   # middle platform height
post(-14.5, -12.0, 2.2, PZ, 4.4, (8.0, 38.0))   # front-left sisal post
post(-12.0, 12.5, 2.2, PZ, 4.0)                 # back plush post
post(8.0, 5.0, 24.0, PZ, 4.0)                   # right post standing on the tunnel
rbox_mesh(30, 26, 2.6, -3.0, 4.0, PZ, 'peluche', 1.0)                            # middle platform
post(-3.0, 9.0, PZ + 2.6, 72.0, 4.2, (55.0, 68.0))                               # upper post (plush/sisal/plush)
# round bed on top, Ø29 with rim
cyl(14.5, 2.0, -3.0, 9.0, 72.0, 'peluche', 64)
ring(14.5, 12.0, 6.5, -3.0, 9.0, 74.0, 'peluche', 64)
cyl(12.2, 1.0, -3.0, 9.0, 74.0, 'peluche', 64)
# hanging pompom toy
cyl(0.12, 18.0, 9.0, 0.5, 60.0, 'fil_noir', 6)
bpy.ops.object.select_all(action='DESELECT')
bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=3, radius=2.6)
for v in bm.verts: v.co += Vector((9.0, 0.5, 57.8))
me = bpy.data.meshes.new('pom'); bm.to_mesh(me); bm.free()
o = bpy.data.objects.new('pom', me); bpy.context.collection.objects.link(o); me.materials.append(M('peluche'))
for p in me.polygons: p.use_smooth = True
# scratching tunnel (half arch) on the right-front of the base
bm = bmesh.new(); prof = []
R_out, R_in, Lt = 11.5, 9.5, 24.0
segs = 24
outer = [(R_out * math.cos(math.pi * i / segs), R_out * math.sin(math.pi * i / segs)) for i in range(segs + 1)]
inner = [(R_in * math.cos(math.pi * i / segs), R_in * math.sin(math.pi * i / segs)) for i in range(segs + 1)][::-1]
prof = outer + inner                     # closed profile in (x, z), extruded along y
cxT, cyT, zT = 8.0, -6.0, 2.2
front = [bm.verts.new((cxT + u, cyT - Lt / 2, zT + v)) for u, v in prof]
back = [bm.verts.new((cxT + u, cyT + Lt / 2, zT + v)) for u, v in prof]
n = len(prof)
for i in range(n):
    f = bm.faces.new((front[i], front[(i + 1) % n], back[(i + 1) % n], back[i]))
    f.material_index = 1 if i < segs else 0          # outer arch face = sisal canvas
bm.faces.new(front[::-1]); bm.faces.new(back)
me = bpy.data.meshes.new('tunnel'); bm.to_mesh(me); bm.free()
o = bpy.data.objects.new('tunnel', me); bpy.context.collection.objects.link(o)
me.materials.append(M('peluche')); me.materials.append(M('toile_sisal'))
for p in me.polygons: p.use_smooth = True
# plush borders on the tunnel edges
for yy_ in (cyT - Lt / 2 + 1.2, cyT + Lt / 2 - 1.2):
    bm = bmesh.new(); rs = []
    for i in range(segs + 1):
        a = math.pi * i / segs
        c = Vector((cxT + (R_out + 0.3) * math.cos(a), yy_, zT + (R_out + 0.3) * math.sin(a)))
        rs.append(c)
    me = bpy.data.meshes.new('b'); o = bpy.data.objects.new('b', me); bpy.context.collection.objects.link(o)
    bm.free()
    for i in range(segs):
        tube(rs[i], rs[i + 1], 1.3, 'peluche', 10)
    bpy.data.objects.remove(o)
box(4, 0.3, 2.2, -10, -D / 2 - 0.1, 0.0, 'etiquette')                            # small leather label
export('arbre_chat_marcelo', {'peluche': ((1, 1, 1), 0.02, 3, 'map_Kd peluche_bleue.jpg\n'),
                              'sisal': ((1, 1, 1), 0.02, 3, 'map_Kd sisal.jpg\n'),
                              'toile_sisal': ((1, 1, 1), 0.02, 3, 'map_Kd toile_sisal.jpg\n'),
                              'fil_noir': ((0.05, 0.05, 0.05), 0.1, 5, ''),
                              'etiquette': ((0.62, 0.38, 0.22), 0.2, 20, '')},
       textures=['/tmp/peluche_bleue.jpg', '/tmp/sisal.jpg', '/tmp/toile_sisal.jpg'])
print('CAT OK')

# ================= Poubelle inox à pédale (SDE) 20 x 20 x 28 =================
reset()
R = 9.6
cyl(R, 1.2, 0, 0, 0, 'plastique_noir', 64)                       # black base ring
cyl(R, 24.0, 0, 0, 1.2, 'inox_brosse', 64)                       # brushed steel body
cyl(R - 0.15, 0.4, 0, 0, 25.0, 'plastique_noir', 64)             # shadow joint under the lid
lid = lathe = None
bm = bmesh.new(); rings = []
prof = [(R + 0.15, 25.4), (R + 0.15, 26.6), (R - 0.6, 27.4), (R * 0.6, 27.85), (0.0, 28.0)]
for r, z in prof:
    rings.append([bm.verts.new((r * math.cos(2 * math.pi * k / 64), r * math.sin(2 * math.pi * k / 64), z)) for k in range(64)] if r > 0 else [bm.verts.new((0, 0, z))])
for i in range(len(rings) - 1):
    a, b = rings[i], rings[i + 1]
    if len(b) == 1:
        for k in range(64): bm.faces.new((a[k], a[(k + 1) % 64], b[0]))
    else:
        for k in range(64): bm.faces.new((a[k], a[(k + 1) % 64], b[(k + 1) % 64], b[k]))
bm.faces.new(rings[0][::-1])
me = bpy.data.meshes.new('lid'); bm.to_mesh(me); bm.free()
o = bpy.data.objects.new('lid', me); bpy.context.collection.objects.link(o); me.materials.append(M('inox_poli'))
for p in me.polygons: p.use_smooth = True
box(4.0, 1.6, 6.0, 0, R + 0.4, 20.5, 'plastique_noir', 0.3)        # rear hinge block
tube((-1.6, R + 1.4, 18.5), (-1.6, R + 1.4, 24.5), 0.18, 'inox_poli', 8)
tube((1.6, R + 1.4, 18.5), (1.6, R + 1.4, 24.5), 0.18, 'inox_poli', 8)
tube((-1.6, R + 1.4, 18.5), (1.6, R + 1.4, 18.5), 0.18, 'inox_poli', 8)
box(6.0, 3.6, 0.8, 0, -R - 1.4, 1.6, 'inox_poli', 0.2)           # pedal
box(5.6, 3.2, 0.2, 0, -R - 1.4, 2.4, 'plastique_noir')           # pedal grip
box(6.0, 2.0, 1.4, 0, -R - 0.4, 0.2, 'plastique_noir', 0.2)      # pedal hinge
export('poubelle_inox', {'inox_brosse': ((0.72, 0.73, 0.74), 0.75, 60, ''), 'inox_poli': ((0.80, 0.81, 0.82), 0.9, 110, ''),
                         'plastique_noir': ((0.05, 0.05, 0.05), 0.2, 20, '')})
print('BIN OK')

# ================= Poubelle cuisine SONGMICS LTB03 30 L noire : 29 (front) x 41 x 65 =================
reset()
Wf, Dp, Hh = 29.0, 41.0, 65.0
def rr(sx, sy, sz, z0, mat, r, segs=6, cx=0, cy=0):
    o = box(sx, sy, sz, cx, cy, z0, mat, bevel=r, segs=segs)
    for p in o.data.polygons: p.use_smooth = True
    return o
rr(Wf - 0.6, Dp - 0.6, 2.0, 0, 'plastique_noir', 3.5)                 # plastic base
rr(Wf, Dp, 58.6, 1.8, 'acier_noir', 4.0)                              # steel body (rounded corners)
rr(Wf - 0.4, Dp - 0.4, 0.5, 60.3, 'plastique_noir', 3.8)              # shadow joint
rr(Wf + 0.4, Dp + 0.4, 3.6, 60.8, 'acier_noir_lisse', 4.2, 8)         # lid
rr(Wf - 3, Dp - 3, 0.8, 64.2, 'acier_noir_lisse', 3.0, 8)             # slight top dome
box(10, 2.0, 5.0, 0, Dp / 2 + 0.6, 56.0, 'plastique_noir', 0.4)       # rear hinge
box(11, 4.5, 1.0, 0, -Dp / 2 - 2.0, 2.0, 'plastique_noir', 0.4)       # pedal
box(10, 3.8, 0.25, 0, -Dp / 2 - 2.0, 3.0, 'plastique_gris')           # pedal grip
box(12, 2.0, 2.2, 0, -Dp / 2 - 0.4, 0.4, 'plastique_noir', 0.3)       # pedal housing
export('poubelle_songmics', {'acier_noir': ((0.05, 0.05, 0.055), 0.35, 45, ''),
                             'acier_noir_lisse': ((0.06, 0.06, 0.065), 0.5, 70, ''),
                             'plastique_noir': ((0.03, 0.03, 0.03), 0.15, 15, ''),
                             'plastique_gris': ((0.18, 0.18, 0.19), 0.1, 10, '')})
print('SONGMICS OK')
