"""Suspension Bezany (Sklum) – abat-jour verre cannelé Ø15 x 13 cm, multicolore 'fresh', structure fer galvanisé.
Piece height 70 cm (shade at bottom, cable up to ceiling canopy). cm units, up = Z."""
import bpy, bmesh, math, sys, os
OUTDIR = sys.argv[sys.argv.index('--') + 1]; os.makedirs(OUTDIR, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
H = 70.0
COLORS = ['verre_vert_eau', 'verre_rose', 'verre_ambre', 'verre_lilas']

def mat(n):
    return bpy.data.materials.get(n) or bpy.data.materials.new(n)

# --- fluted glass shade (bell / tulip profile), one colour band per group of flutes ---
FL = 24          # flutes
SEG = 6          # verts per flute
RING = FL * SEG
prof = []        # (z, r) from bottom rim to top
for i in range(0, 27):
    t = i / 26
    z = 13.0 * t
    r = 7.5 * (1 - 0.55 * t ** 2.2) + 0.15 * math.sin(t * math.pi)  # wide open rim, closing to the top
    prof.append((z, max(r, 1.6)))
bm = bmesh.new()
rings = []
for z, r in prof:
    ring = []
    for k in range(RING):
        a = 2 * math.pi * k / RING
        flute = 1 + 0.045 * abs(math.sin(math.pi * (k % SEG) / SEG))  # rounded ribs
        ring.append(bm.verts.new((r * flute * math.cos(a), r * flute * math.sin(a), z)))
    rings.append(ring)
mats = [mat(c) for c in COLORS]
for i in range(len(rings) - 1):
    for k in range(RING):
        f = bm.faces.new((rings[i][k], rings[i][(k + 1) % RING], rings[i + 1][(k + 1) % RING], rings[i + 1][k]))
        f.material_index = (k // (SEG * 3)) % len(COLORS)  # 3 flutes per colour band
        f.smooth = True
me = bpy.data.meshes.new('shade'); bm.to_mesh(me); bm.free()
shade = bpy.data.objects.new('shade', me); bpy.context.collection.objects.link(shade)
for m in mats: me.materials.append(m)
s = shade.modifiers.new('s', 'SOLIDIFY'); s.thickness = 0.35
bpy.context.view_layer.objects.active = shade; bpy.ops.object.modifier_apply(modifier='s')

metal = mat('fer_galvanise')
def cyl(r, d, z, name, m, verts=24):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d, location=(0, 0, z), vertices=verts)
    o = bpy.context.active_object; o.name = name; o.data.materials.append(m)
    bpy.ops.object.shade_smooth(); return o
parts = [shade]
parts.append(cyl(2.0, 3.0, 13.5, 'douille', metal))          # top cap / socket holder
parts.append(cyl(1.2, 2.0, 15.5, 'collier', metal))
parts.append(cyl(0.25, H - 18.5, 16.5 + (H - 18.5) / 2, 'cable', metal, 8))
parts.append(cyl(5.0, 2.0, H - 1.0, 'rosace', metal, 32))   # ceiling canopy
bulb = mat('ampoule')
bpy.ops.mesh.primitive_uv_sphere_add(radius=2.2, location=(0, 0, 8.5), segments=16, ring_count=10)
b = bpy.context.active_object; b.data.materials.append(bulb); bpy.ops.object.shade_smooth(); parts.append(b)

bpy.ops.object.select_all(action='DESELECT')
for o in parts: o.select_set(True)
bpy.context.view_layer.objects.active = shade; bpy.ops.object.join()
bpy.ops.wm.obj_export(filepath=os.path.join(OUTDIR, 'model.obj'), export_materials=False,
                      export_normals=True, export_uv=False, forward_axis='NEGATIVE_Z', up_axis='Y')
# OBJ needs the mtllib line since we write our own MTL
p = os.path.join(OUTDIR, 'model.obj'); t = open(p).read()
open(p, 'w').write('mtllib model.mtl\n' + t)
open(os.path.join(OUTDIR, 'model.mtl'), 'w').write(
"""newmtl verre_vert_eau
Ka 0.2 0.2 0.2
Kd 0.560 0.800 0.660
Ks 0.9 0.9 0.9
Ns 110
d 0.55
newmtl verre_rose
Ka 0.2 0.2 0.2
Kd 0.960 0.700 0.760
Ks 0.9 0.9 0.9
Ns 110
d 0.55
newmtl verre_ambre
Ka 0.2 0.2 0.2
Kd 0.980 0.800 0.480
Ks 0.9 0.9 0.9
Ns 110
d 0.55
newmtl verre_lilas
Ka 0.2 0.2 0.2
Kd 0.760 0.690 0.900
Ks 0.9 0.9 0.9
Ns 110
d 0.55
newmtl fer_galvanise
Ka 0.2 0.2 0.2
Kd 0.720 0.730 0.740
Ks 0.7 0.7 0.7
Ns 80
newmtl ampoule
Ka 1 1 1
Kd 1.000 0.960 0.880
Ks 0.3 0.3 0.3
Ns 40
d 0.85
""")
# Blender preview materials
for n, c in [('verre_vert_eau', (0.56, 0.8, 0.66)), ('verre_rose', (0.96, 0.7, 0.76)), ('verre_ambre', (0.98, 0.8, 0.48)), ('verre_lilas', (0.76, 0.69, 0.9))]:
    m = bpy.data.materials[n]; m.use_nodes = True; bs = m.node_tree.nodes['Principled BSDF']
    bs.inputs['Base Color'].default_value = (*c, 1); bs.inputs['Transmission Weight'].default_value = 0.9; bs.inputs['Roughness'].default_value = 0.05
metal.use_nodes = True; metal.node_tree.nodes['Principled BSDF'].inputs['Metallic'].default_value = 1
metal.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.3
bulb.use_nodes = True; bb = bulb.node_tree.nodes['Principled BSDF']
bb.inputs['Emission Color'].default_value = (1, 0.8, 0.55, 1); bb.inputs['Emission Strength'].default_value = 25
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUTDIR, 'lamp.blend'))
print('OK')
