import sys, os, math
src = open('/home/claude/scripts/make_items.py').read()
exec(src[:src.index("TEX = ")])
reset()
R = 15.0
def ring(r_out, r_in, z0, z1, mat, segs=96):
    bm = bmesh.new(); rs = []
    for r, z in [(r_in, z0), (r_out, z0), (r_out, z1), (r_in, z1)]:
        rs.append([bm.verts.new((r * math.cos(2 * math.pi * k / segs), r * math.sin(2 * math.pi * k / segs), z)) for k in range(segs)])
    for i in range(4):
        a, b = rs[i], rs[(i + 1) % 4]
        for k in range(segs): bm.faces.new((a[k], a[(k + 1) % segs], b[(k + 1) % segs], b[k]))
    me = bpy.data.meshes.new('r'); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new('r', me); bpy.context.collection.objects.link(o); me.materials.append(M(mat))
    for p in me.polygons: p.use_smooth = True
def curved_panel(r, z0, z1, span, mat, corner=2.0, nu=60, nv=24, thick=0.0):
    """rounded-rectangle patch lying on a cylinder of radius r, centred on the front (-Y)."""
    bm = bmesh.new(); grid = []
    half = span / 2
    for j in range(nv + 1):
        z = z0 + (z1 - z0) * j / nv; row = []
        for i in range(nu + 1):
            s = -half + span * i / nu                      # arc length from centre
            # rounded corners: pull corner points inward
            dz = min(z - z0, z1 - z); ds = half - abs(s)
            if dz < corner and ds < corner:
                d = corner - math.hypot(corner - dz, corner - ds)
                if d < 0:  # outside the rounded corner -> clamp onto the arc
                    a = math.atan2(corner - dz, corner - ds)
                    ds2 = corner - corner * math.cos(a); dz2 = corner - corner * math.sin(a)
                    s = math.copysign(half - ds2, s); z = (z0 + dz2) if (z - z0) < (z1 - z) else (z1 - dz2)
            th = -math.pi / 2 + s / r
            row.append(bm.verts.new((r * math.cos(th), r * math.sin(th), z)))
        grid.append(row)
    for j in range(nv):
        for i in range(nu):
            bm.faces.new((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]))
    me = bpy.data.meshes.new('p'); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new('p', me); bpy.context.collection.objects.link(o); me.materials.append(M(mat))
    for p in me.polygons: p.use_smooth = True
    return o
def hole(r, zc, s_off, rad, mat):
    th = -math.pi / 2 + s_off / r
    bm = bmesh.new(); c = bm.verts.new((r * math.cos(th), r * math.sin(th), zc)); ring_ = []
    n = Vector((math.cos(th), math.sin(th), 0)); t = Vector((-math.sin(th), math.cos(th), 0))
    for k in range(32):
        a = 2 * math.pi * k / 32
        ring_.append(bm.verts.new(c.co + t * (rad * math.cos(a)) + Vector((0, 0, rad * math.sin(a)))))
    for k in range(32): bm.faces.new((c, ring_[k], ring_[(k + 1) % 32]))
    me = bpy.data.meshes.new('h'); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new('h', me); bpy.context.collection.objects.link(o); me.materials.append(M(mat))
cyl(13.5, 1.6, 0, 0, 0, 'socle_noir', 96)                         # black plinth
cyl(R, 0.8, 0, 0, 1.4, 'vert', 96)                                # bottom edge
SPAN = 24.5
for k, (z0, z1) in enumerate([(2.2, 19.6), (20.6, 38.0)]):
    cyl(R - 0.25, z1 - z0, 0, 0, z0, 'vert', 128)                  # module body (slightly inset)
    ring(R + 0.05, R - 0.3, z0 - 0.0, z0 + 0.9 if k == 0 else z0 + 1.0, 'vert')    # lower lip
    curved_panel(R - 0.05, z0 + 1.0, z1 - 1.0, SPAN + 0.8, 'vert_ombre', 2.4)        # recess shadow
    curved_panel(R + 0.05, z0 + 1.3, z1 - 1.3, SPAN, 'vert', 2.0)                     # door (sliding)
    hole(R + 0.08, (z0 + z1) / 2, -SPAN / 2 + 5.5, 2.1, 'trou_noir')                  # finger hole on the left
ring(R + 0.05, R - 0.3, 19.6, 20.6, 'vert_ombre')                  # joint between modules
ring(R + 0.05, R - 1.2, 38.0, 40.0, 'vert')                        # top lid rim
cyl(R - 1.2, 0.6, 0, 0, 38.9, 'vert', 96)                          # recessed top tray
export('babel', {'vert': ((0.40, 0.48, 0.27), 0.45, 80, ''),
                 'vert_ombre': ((0.20, 0.25, 0.13), 0.2, 20, ''),
                 'trou_noir': ((0.03, 0.03, 0.03), 0.0, 1, ''),
                 'socle_noir': ((0.05, 0.05, 0.05), 0.2, 20, '')})
