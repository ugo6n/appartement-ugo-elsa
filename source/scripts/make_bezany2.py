"""Suspension Bezany (photo de référence) : rosace laiton, câble textile noir, boule lilas, galet vert d'eau,
cloche en verre rose ouverte, douille laiton, ampoule claire. Piece height 70 cm. Up = Z."""
import sys, os, math
src = open('/home/claude/scripts/make_items.py').read()
exec(src[:src.index("TEX = ")])
reset()
H = 70.0

def lathe(profile, mat, segs=48):
    """profile: list of (r, z) from bottom to top; closed surface of revolution (open where r>0 at ends)."""
    bm = bmesh.new(); rings = []
    for r, z in profile:
        if r < 1e-4:
            rings.append([bm.verts.new((0, 0, z))])
        else:
            rings.append([bm.verts.new((r * math.cos(2 * math.pi * k / segs), r * math.sin(2 * math.pi * k / segs), z)) for k in range(segs)])
    for i in range(len(rings) - 1):
        a, b = rings[i], rings[i + 1]
        if len(a) == 1:
            for k in range(segs): bm.faces.new((a[0], b[(k + 1) % segs], b[k]))
        elif len(b) == 1:
            for k in range(segs): bm.faces.new((a[k], a[(k + 1) % segs], b[0]))
        else:
            for k in range(segs): bm.faces.new((a[k], a[(k + 1) % segs], b[(k + 1) % segs], b[k]))
    me = bpy.data.meshes.new('l'); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new('l', me); bpy.context.collection.objects.link(o); me.materials.append(M(mat))
    for p in me.polygons: p.use_smooth = True
    return o

# pink glass bell (open at the bottom), Ø15, h 14, thin wall (outer + inner surface)
bell = []
for i in range(0, 25):
    t = i / 24
    a = t * math.pi / 2
    r = 7.5 * math.cos(a) if t > 0.45 else 7.5
    z = 6.0 + 7.5 * math.sin(a) if t > 0.45 else 13.5 * t / 0.45 * 0.444
    bell.append((r, z))
# simpler explicit profile: straight cylinder 0-6 cm, then quarter-circle dome to the top
bell = [(7.5, 0.0), (7.5, 6.0)] + [(7.5 * math.cos(math.pi / 2 * i / 16), 6.0 + 7.5 * math.sin(math.pi / 2 * i / 16)) for i in range(1, 17)]
bell[-1] = (0.0, 13.5)
outer = lathe(bell, 'verre_rose', 64)
inner = lathe([(r * 0.965, z * 0.975) for r, z in bell], 'verre_rose', 64)
inner.data.flip_normals() if hasattr(inner.data, 'flip_normals') else None
# brass socket inside the bell + clear bulb
cyl(1.7, 5.5, 0, 0, 8.0, 'laiton', 32)
bulb = lathe([(0, 2.2), (2.0, 2.8), (3.0, 4.4), (3.0, 5.4), (2.4, 6.8), (1.4, 7.8), (1.3, 8.4), (0, 8.4)], 'ampoule', 40)
# stacked glass beads : green pebble, lilac ball
peb = [(0, 0)] + [(5.6 * math.sin(math.pi * i / 16), 3.7 - 3.7 * math.cos(math.pi * i / 16)) for i in range(1, 16)] + [(0, 7.4)]
o = lathe(peb, 'verre_vert', 48); o.data.transform(Matrix.Translation((0, 0, 13.6)))
ball = [(0, 0)] + [(3.9 * math.sin(math.pi * i / 16), 3.9 - 3.9 * math.cos(math.pi * i / 16)) for i in range(1, 16)] + [(0, 7.8)]
o = lathe(ball, 'verre_lilas', 48); o.data.transform(Matrix.Translation((0, 0, 21.1)))
cyl(0.45, 16.0, 0, 0, 13.4, 'laiton', 16)          # brass rod through the beads
cyl(0.9, 1.2, 0, 0, 28.9, 'laiton', 24)           # top cap
cyl(0.32, H - 31.5, 0, 0, 30.0, 'cable_noir', 12)  # black textile cable
cyl(0.7, 1.6, 0, 0, H - 3.4, 'laiton', 20)
cyl(5.5, 2.0, 0, 0, H - 2.0, 'laiton', 48)          # round brass canopy
export('suspension_perles', {
    'verre_rose':  ((0.98, 0.72, 0.70), 0.9, 120, 'd 0.35\n'),
    'verre_vert':  ((0.40, 0.62, 0.58), 0.9, 120, 'd 0.6\n'),
    'verre_lilas': ((0.76, 0.70, 0.86), 0.9, 120, 'd 0.5\n'),
    'laiton':      ((0.78, 0.62, 0.36), 0.8, 90, ''),
    'cable_noir':  ((0.04, 0.04, 0.04), 0.05, 5, ''),
    'ampoule':     ((1.0, 0.97, 0.90), 0.6, 100, 'd 0.6\n')})
print('LAMP OK')
