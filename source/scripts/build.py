import bpy, re, math, sys, os
from mathutils import Vector, Matrix

SRC = sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else '/home/claude/src/x'
OUT = '/home/claude/scene.blend'

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
xml = open(os.path.join(SRC, 'Home.xml'), encoding='utf-8').read()
def attrs(s): return dict(re.findall(r"(\w+)='([^']*)'", s))

def P(x, y, z=0.0): return Vector((x/100.0, -y/100.0, z/100.0))

def mat(name, color, rough=0.5, metal=0.0, transm=0.0, emit=None, estr=0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*color, 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    b.inputs['Transmission Weight'].default_value = transm
    if emit:
        b.inputs['Emission Color'].default_value = (*emit, 1)
        b.inputs['Emission Strength'].default_value = estr
    return m

wall_m = mat('wall', (0.86, 0.85, 0.82), 0.85)
ceil_m = mat('ceiling', (0.92, 0.92, 0.91), 0.9)
ground_m = mat('ground', (0.25, 0.28, 0.22), 0.95)

# ---------- furniture ----------
coll_furn = []
openings = []
for m in re.finditer(r"<(pieceOfFurniture|doorOrWindow|light) ([^>]*?)\s*/?>", xml):
    kind, a = m.group(1), attrs(m.group(2))
    path = os.path.join(SRC, a['model'])
    before = set(bpy.data.objects)
    bpy.ops.wm.obj_import(filepath=path)
    new = [o for o in bpy.data.objects if o not in before and o.type == 'MESH']
    if not new: continue
    bpy.ops.object.select_all(action='DESELECT')
    for o in new: o.select_set(True)
    bpy.context.view_layer.objects.active = new[0]
    if len(new) > 1: bpy.ops.object.join()
    o = bpy.context.view_layer.objects.active
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    vs = [v.co for v in o.data.vertices]
    mn = Vector((min(v.x for v in vs), min(v.y for v in vs), min(v.z for v in vs)))
    mx = Vector((max(v.x for v in vs), max(v.y for v in vs), max(v.z for v in vs)))
    W, D, H = float(a['width']), float(a['depth']), float(a['height'])
    size = mx - mn
    sx = W/100/size.x if size.x > 1e-6 else 1
    sy = D/100/size.y if size.y > 1e-6 else 1
    sz = H/100/size.z if size.z > 1e-6 else 1
    ctr = Vector(((mn.x+mx.x)/2, (mn.y+mx.y)/2, mn.z))
    M = (Matrix.Translation(P(float(a['x']), float(a['y']), float(a.get('elevation', 0))))
         @ Matrix.Rotation(-float(a.get('angle', 0)), 4, 'Z')
         @ Matrix.Diagonal((sx, sy, sz, 1))
         @ Matrix.Translation(-ctr))
    o.data.transform(M)
    # clean coincident duplicate faces (they cause black self-shadowing in Cycles)
    import bmesh as _bm
    bm = _bm.new(); bm.from_mesh(o.data)
    _bm.ops.remove_doubles(bm, verts=bm.verts, dist=0.0004)
    seen = {}; dup = []
    for f in bm.faces:
        key = tuple(sorted(v.index for v in f.verts))
        if key in seen: dup.append(f)
        else: seen[key] = f
    if dup: _bm.ops.delete(bm, geom=dup, context='FACES_ONLY')
    bm.to_mesh(o.data); bm.free()
    if a['model'].split('/')[0].startswith(('placard', 'gtl', 'gaine', 'coffrage', 'linteau', 'plinthes')):
        if o.data.has_custom_normals:
            bpy.context.view_layer.objects.active = o
            bpy.ops.mesh.customdata_custom_splitnormals_clear()
        for poly in o.data.polygons: poly.use_smooth = False
    o.name = a['name']
    o['model'] = a['model'].split('/')[0]
    o['x'], o['y'] = float(a['x']), float(a['y'])
    o['elev'], o['H'] = float(a.get('elevation', 0)), H
    coll_furn.append(o)
    if kind == 'doorOrWindow':
        openings.append(a)

# ---------- material fixes ----------
for m in bpy.data.materials:
    if not m.use_nodes: continue
    b = m.node_tree.nodes.get('Principled BSDF')
    if not b: continue
    n = m.name.lower()
    a = b.inputs['Alpha'].default_value
    if a < 0.99 or any(k in n for k in ('verre', 'glass', 'vitre', 'vitrage')):
        # thin architectural glass: transparent (lets sun through) + fresnel reflection
        col = b.inputs['Base Color'].default_value
        nt = m.node_tree; out = nt.nodes['Material Output']
        tr = nt.nodes.new('ShaderNodeBsdfTransparent')
        sat = max(col[:3]) - min(col[:3])
        tint = [1 - 0.7*(1-c) for c in col[:3]] if sat > 0.08 else [0.92 + 0.08*c for c in col[:3]]
        if a > 0.8: tint = [t*(1.2 - a) for t in tint]  # smoked glass
        tr.inputs['Color'].default_value = (*tint, 1)
        gl = nt.nodes.new('ShaderNodeBsdfGlossy'); gl.inputs['Roughness'].default_value = 0.0
        fr = nt.nodes.new('ShaderNodeFresnel'); fr.inputs['IOR'].default_value = 1.5
        mix = nt.nodes.new('ShaderNodeMixShader')
        mix.inputs[0].default_value = 0.07; nt.links.new(tr.outputs[0], mix.inputs[1]); nt.links.new(gl.outputs[0], mix.inputs[2])
        nt.links.new(mix.outputs[0], out.inputs['Surface'])
        continue
    if any(k in n for k in ('chrome', 'inox', 'metal', 'acier', 'laiton', 'or_', 'brass')):
        b.inputs['Metallic'].default_value = 1.0
        b.inputs['Roughness'].default_value = 0.18
    if 'acier_noir' in n or 'plastique_noir' in n:
        b.inputs['Roughness'].default_value = 0.55
        if b.inputs.get('Specular IOR Level'): b.inputs['Specular IOR Level'].default_value = 0.3
    if 'miroir' in n or 'mirror' in n:
        b.inputs['Metallic'].default_value = 1.0
        b.inputs['Roughness'].default_value = 0.0
        b.inputs['Base Color'].default_value = (0.95, 0.95, 0.95, 1)
    sp = b.inputs.get('Specular IOR Level')
    if sp and b.inputs['Metallic'].default_value < 0.5:
        sp.default_value = min(sp.default_value, 0.5)

# ---------- walls ----------
def box(name, p0, p1, thick, h, z0=0.0, ext0=None, ext1=None):
    d = (p1 - p0); L = d.length
    if L < 1e-6: return None
    if ext0 is not None:
        u = d.normalized(); p0 = p0 - u * ext0; p1 = p1 + u * ext1; d = p1 - p0; L = d.length; thick_len = 0
    else: thick_len = thick
    bpy.ops.mesh.primitive_cube_add(size=1)
    o = bpy.context.active_object; o.name = name
    o.scale = (L + thick_len, thick, h)
    o.rotation_euler = (0, 0, math.atan2(d.y, d.x))
    o.location = ((p0 + p1)/2).to_2d().to_3d() + Vector((0, 0, z0 + h/2))
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return o

walls = []
THK = {attrs(m.group(1))['id']: float(attrs(m.group(1))['thickness'])/100 for m in re.finditer(r"<wall ([^>]*)/>", xml)}
for m in re.finditer(r"<wall ([^>]*)/>", xml):
    a = attrs(m.group(1))
    t = float(a['thickness'])/100
    o = box('wall_'+a['id'], P(float(a['xStart']), float(a['yStart'])), P(float(a['xEnd']), float(a['yEnd'])), t, float(a['height'])/100 + 0.0012*len(walls),
            ext0=(THK[a['wallAtStart']]/2 - 0.004 if 'wallAtStart' in a else 0.0), ext1=(THK[a['wallAtEnd']]/2 - 0.004 if 'wallAtEnd' in a else 0.0))
    # shrink extension for thin partitions so they don't poke through
    o.data.materials.append(wall_m); walls.append(o)

cutters = []
for a in openings:
    bpy.ops.mesh.primitive_cube_add(size=1)
    c = bpy.context.active_object
    W, D, H = float(a['width'])/100, float(a['depth'])/100 + 0.6, float(a['height'])/100
    c.scale = (W - 0.002, D, H)
    c.rotation_euler = (0, 0, -float(a['angle']))
    z0 = float(a['elevation'])
    if z0 < 1: H += 0.02; z0 -= 1.0
    c.scale = (W - 0.002, D, H)
    c.location = P(float(a['x']), float(a['y']), z0) + Vector((0, 0, H/2))
    c.display_type = 'WIRE'; c.hide_render = True
    cutters.append(c)
for w in walls:
    for c in cutters:
        mod = w.modifiers.new('cut', 'BOOLEAN'); mod.object = c; mod.solver = 'EXACT'; mod.operation = 'DIFFERENCE'; mod.use_hole_tolerant = True
    bpy.context.view_layer.objects.active = w
    for mod in list(w.modifiers): bpy.ops.object.modifier_apply(modifier=mod.name)
for c in cutters: bpy.data.objects.remove(c)

# header strip above the entrance closet (hides a dark self-shadowed band)
hd = box('bandeau_placard', P(752, 346.2), P(923, 346.2), 0.06, 0.12, 2.378)
hd.data.materials.append(wall_m)

# faint light inside the bedroom wardrobe so the door seams read grey, not black
glow = bpy.data.materials.new('placard_interieur'); glow.use_nodes = True
gb = glow.node_tree.nodes['Principled BSDF']; gb.inputs['Base Color'].default_value = (0.8, 0.8, 0.78, 1)
gb.inputs['Emission Color'].default_value = (1, 0.97, 0.92, 1); gb.inputs['Emission Strength'].default_value = 0.35
bpy.ops.mesh.primitive_plane_add(size=1); gp = bpy.context.active_object; gp.name = 'placard_glow'
gp.scale = (0.01, 1.78, 2.4); gp.rotation_euler = (0, math.radians(90), 0)
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
gp.location = P(447.5, 590.5, 122); gp.data.materials.append(glow)
gp.visible_glossy = False

# ---------- ceilings ----------
for m in re.finditer(r"<room ([^>]*)>(.*?)</room>", xml, re.S):
    a = attrs(m.group(1))
    if a.get('ceilingVisible') != 'true': continue
    pts = [P(float(x), float(y), 249.7) for x, y in re.findall(r"<point x='([^']*)' y='([^']*)'", m.group(2))]
    me = bpy.data.meshes.new('ceil'); me.from_pydata(pts, [], [list(range(len(pts)))[::-1]])
    o = bpy.data.objects.new('ceiling_'+a['name'], me); sc.collection.objects.link(o)
    me.materials.append(ceil_m)
    s = o.modifiers.new('s', 'SOLIDIFY'); s.thickness = 0.2; s.offset = 1
# big roof slab to block sky everywhere (incl. above walls)
bpy.ops.mesh.primitive_cube_add(size=1, location=(4.3, -3.5, 2.605)); r = bpy.context.active_object
r.scale = (10.6, 7.2, 0.2); r.data.materials.append(ceil_m); r.name = 'roof'
# ground
bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, -0.01)); g = bpy.context.active_object
g.data.materials.append(ground_m); g.name = 'ground'

bpy.ops.wm.save_as_mainfile(filepath=OUT)
print('OK', len(coll_furn), 'pieces')
