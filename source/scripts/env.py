"""Exterior environment seen from the balcony (west): elevated flat (~3rd floor), garden courtyard with lawn,
paths and autumn trees, modern white/grey residential buildings with coloured balcony panels, golden-hour sky."""
import bpy, bmesh, math, os
import numpy as np
from mathutils import Vector, Matrix
from PIL import Image, ImageDraw

def setup_env(sc, sun_az_deg, sun_el_deg, strength=1.0, texdir='/home/claude/env_tex'):
    os.makedirs(texdir, exist_ok=True)
    rng = np.random.default_rng(21)
    # ---------- sky ----------
    w = sc.world; nt = w.node_tree
    for n in list(nt.nodes):
        if n.type not in ('OUTPUT_WORLD',): nt.nodes.remove(n)
    out = [n for n in nt.nodes if n.type == 'OUTPUT_WORLD'][0]
    sky = nt.nodes.new('ShaderNodeTexSky'); sky.sky_type = 'MULTIPLE_SCATTERING'
    sky.sun_elevation = math.radians(sun_el_deg)
    sky.sun_rotation = math.radians(sun_az_deg - 90)   # blender sky: rotation 0 = sun towards +Y? adjust: az measured from +X
    sky.altitude = 30; sky.sun_disc = True
    bg = nt.nodes.new('ShaderNodeBackground'); bg.inputs['Strength'].default_value = 0.35 * strength
    nt.links.new(sky.outputs['Color'], bg.inputs['Color']); nt.links.new(bg.outputs['Background'], out.inputs['Surface'])

    def mat(name, col, rough=0.8, tex=None, scale=1.0):
        m = bpy.data.materials.new(name); m.use_nodes = True
        b = m.node_tree.nodes['Principled BSDF']
        b.inputs['Base Color'].default_value = (*col, 1); b.inputs['Roughness'].default_value = rough
        if tex:
            t = m.node_tree.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(tex)
            m.node_tree.links.new(t.outputs['Color'], b.inputs['Base Color'])
        return m

    def obj_from_bm(bm, name, m):
        me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
        o = bpy.data.objects.new(name, me); sc.collection.objects.link(o); me.materials.append(m)
        return o

    def boxm(sx, sy, sz, loc, m, name='env'):
        bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
        for v in bm.verts: v.co = Vector((v.co.x * sx + loc[0], v.co.y * sy + loc[1], v.co.z * sz + loc[2] + sz / 2))
        return obj_from_bm(bm, name, m)

    def cube_uv(o, size):
        me = o.data; uv = me.uv_layers.new()
        for p in me.polygons:
            n = p.normal
            for li in p.loop_indices:
                c = me.vertices[me.loops[li].vertex_index].co
                if abs(n.z) > 0.7: u, v = c.x, c.y
                elif abs(n.x) > abs(n.y): u, v = c.y, c.z
                else: u, v = c.x, c.z
                uv.data[li].uv = (u / size, v / size)

    GZ = -10.0   # courtyard ground level (flat on the 3rd/4th floor)
    # lawn texture
    N = 512
    g = np.random.default_rng(1).standard_normal((N, N))
    F = np.fft.fft2(g); k = np.hypot(np.fft.fftfreq(N)[:, None] * N, np.fft.fftfreq(N)[None, :] * N)
    nz = np.real(np.fft.ifft2(F * np.exp(-(k / 12) ** 2))); nz = (nz - nz.mean()) / nz.std()
    fine = np.random.default_rng(2).standard_normal((N, N))
    lawn = np.array([0.20, 0.30, 0.10]) * (1 + 0.12 * nz + 0.06 * fine)[..., None]
    Image.fromarray((np.clip(lawn, 0, 1) * 255).astype(np.uint8)).save(f'{texdir}/lawn.jpg')
    ground = boxm(400, 400, 0.1, (-150, 0, GZ - 0.1), mat('lawn', (1, 1, 1), 0.95, f'{texdir}/lawn.jpg'), 'ground')
    cube_uv(ground, 6)
    # building base under the flat (facade below the balcony)
    boxm(14, 30, -GZ - 0.05, (5, -5, GZ), mat('facade_bas', (0.82, 0.80, 0.76), 0.9), 'facade_bas')
    # paths
    pathm = mat('allee', (0.55, 0.54, 0.52), 0.9)
    for (x0, y0, x1, y1) in [(-8, -40, -30, 30), (-30, 30, -60, 45), (-14, -10, -55, -25)]:
        d = Vector((x1 - x0, y1 - y0, 0)); L = d.length
        o = boxm(L, 2.2, 0.05, (0, 0, GZ), pathm, 'allee')
        o.data.transform(Matrix.Translation(((x0 + x1) / 2, (y0 + y1) / 2, 0)) @ Matrix.Rotation(math.atan2(d.y, d.x), 4, 'Z'))
    # low concrete wall / hedge
    boxm(1.2, 40, 1.0, (-26, 5, GZ), mat('haie', (0.16, 0.24, 0.09), 0.95), 'haie')

    # ---------- trees (autumn) ----------
    leaf_cols = [(0.16, 0.22, 0.05), (0.32, 0.25, 0.05), (0.12, 0.19, 0.05), (0.40, 0.30, 0.07), (0.10, 0.16, 0.04)]
    leaf_m = [mat(f'feuillage{i}', c, 0.85) for i, c in enumerate(leaf_cols)]
    trunk_m = mat('tronc', (0.22, 0.18, 0.14), 0.9)
    tex = bpy.data.textures.new('leafnoise', 'CLOUDS'); tex.noise_scale = 0.9
    for i in range(34):
        x = rng.uniform(-48, -6); y = rng.uniform(-45, 40)
        if abs(x + 18) < 2 and abs(y) < 3: continue
        h = rng.uniform(5, 11); r = rng.uniform(1.6, 3.4)
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=0.18, radius2=0.10, depth=h * 0.6)
        for v in bm.verts: v.co += Vector((x, y, GZ + h * 0.3))
        obj_from_bm(bm, 'tronc', trunk_m)
        for j in range(rng.integers(2, 4)):
            bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=3, radius=1.0)
            sx, sz = r * rng.uniform(0.7, 1.0), r * rng.uniform(0.9, 1.4)
            off = Vector((rng.normal(0, r * 0.3), rng.normal(0, r * 0.3), GZ + h * 0.62 + rng.normal(0, r * 0.25)))
            for v in bm.verts:
                v.co = Vector((v.co.x * sx, v.co.y * sx, v.co.z * sz)) + Vector((x, y, 0)) + off
            o = obj_from_bm(bm, 'arbre', leaf_m[int(rng.integers(0, len(leaf_m)))])
            dm = o.modifiers.new('d', 'DISPLACE'); dm.texture = tex; dm.strength = r * 0.7
            for p in o.data.polygons: p.use_smooth = True

    # ---------- residential buildings ----------
    def facade_tex(path, wall, panel=None, seed=0):
        r = np.random.default_rng(seed)
        S = 512; im = Image.new('RGB', (S, S), tuple(int(c * 255) for c in wall)); d = ImageDraw.Draw(im)
        # texture = 6 m x 6 m : 2 floors x 2 bays
        for fl in range(2):
            y0 = fl * S // 2
            for bay in range(2):
                x0 = bay * S // 2
                d.rectangle((x0 + 40, y0 + 50, x0 + 210, y0 + 200), fill=(40, 46, 52))           # window
                d.rectangle((x0 + 40, y0 + 50, x0 + 210, y0 + 58), fill=(70, 74, 78))
                d.line((x0 + 125, y0 + 50, x0 + 125, y0 + 200), fill=(150, 150, 150), width=4)
                if panel is not None and r.random() < 0.55:
                    d.rectangle((x0 + 20, y0 + 150, x0 + 230, y0 + 240), fill=tuple(int(c * 255) for c in panel))  # balcony panel
                else:
                    d.rectangle((x0 + 20, y0 + 200, x0 + 230, y0 + 206), fill=(200, 200, 200))      # balcony rail
            d.rectangle((0, y0 + 244, S, y0 + 256), fill=tuple(int(c * 200) for c in wall))     # slab edge
        im.transpose(Image.FLIP_TOP_BOTTOM).save(path)
    variants = [((0.93, 0.93, 0.92), (0.72, 0.10, 0.10)), ((0.62, 0.63, 0.64), (0.30, 0.55, 0.45)),
                ((0.92, 0.92, 0.90), (0.20, 0.35, 0.62)), ((0.80, 0.80, 0.80), None), ((0.95, 0.94, 0.92), (0.85, 0.55, 0.20)),
                ((0.45, 0.46, 0.48), None)]
    fmats = []
    for i, (wall, panel) in enumerate(variants):
        facade_tex(f'{texdir}/facade{i}.png', wall, panel, i)
        fmats.append(mat(f'facade{i}', (1, 1, 1), 0.85, f'{texdir}/facade{i}.png'))
    roof_m = mat('toit', (0.5, 0.5, 0.5), 0.9)
    blds = [(-62, -12, 26, 16, 18), (-58, 22, 18, 14, 15), (-75, 45, 22, 16, 21), (-90, -40, 30, 18, 24),
            (-55, -48, 16, 14, 12), (-110, 10, 28, 20, 27), (-48, 55, 14, 12, 14), (-95, 70, 24, 18, 18),
            (-120, -70, 30, 20, 21), (-40, -75, 18, 14, 15), (-130, 40, 26, 18, 30)]
    for i, (x, y, sy, sx, h) in enumerate(blds):
        o = boxm(sx, sy, h, (x, y, GZ), fmats[i % len(fmats)], 'immeuble')
        cube_uv(o, 6)
        boxm(sx + 0.4, sy + 0.4, 0.4, (x, y, GZ + h), roof_m, 'acrotere')
        if rng.random() < 0.6:   # setback top floor
            o2 = boxm(sx * 0.7, sy * 0.6, 3, (x + sx * 0.1, y, GZ + h), fmats[(i + 2) % len(fmats)], 'attique'); cube_uv(o2, 6)
    # far skyline haze (simple boxes, bluish grey)
    hz = mat('lointain', (0.62, 0.66, 0.72), 1.0)
    for i in range(14):
        boxm(rng.uniform(20, 40), rng.uniform(20, 40), rng.uniform(15, 35), (rng.uniform(-260, -180), rng.uniform(-150, 150), GZ), hz, 'lointain')
