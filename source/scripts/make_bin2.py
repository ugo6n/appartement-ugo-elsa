import sys, os, math
src = open('/home/claude/scripts/make_items.py').read()
exec(src[:src.index("TEX = ")])
reset()
W, D, H = 34.8, 29.7, 63.3
def rbox_v(sx, sy, sz, z0, mat, rv, rtop=0.0, cx=0, cy=0):
    """box with large-radius vertical corners (+ optional small bevel on top edges)."""
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * sx + cx, v.co.y * sy + cy, v.co.z * sz + z0 + sz / 2))
    vert_edges = [e for e in bm.edges if abs((e.verts[0].co - e.verts[1].co).normalized().z) > 0.9]
    bmesh.ops.bevel(bm, geom=vert_edges, offset=rv, segments=10, profile=0.5, affect='EDGES')
    if rtop > 0:
        top_edges = [e for e in bm.edges if all(v.co.z > z0 + sz - 1e-3 for v in e.verts)]
        bmesh.ops.bevel(bm, geom=top_edges, offset=rtop, segments=4, affect='EDGES')
    me = bpy.data.meshes.new('b'); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new('b', me); bpy.context.collection.objects.link(o); me.materials.append(M(mat))
    for p in me.polygons: p.use_smooth = True
    return o
rbox_v(W - 0.3, D - 0.3, 2.2, 0, 'plastique_noir', 6.5, 0.6)                 # base ring
rbox_v(W - 0.8, D - 0.8, 55.6, 2.0, 'acier_noir_mat', 6.3)                    # body
rbox_v(W - 1.2, D - 1.2, 0.5, 57.5, 'plastique_noir', 6.0)                    # joint
rbox_v(W, D, 5.3, 58.0, 'acier_noir_lid', 6.6)
box(9.0, 0.15, 1.1, W / 2 - 7.5, -D / 2 + 0.33, 49.5, 'logo')                 # SONGMICS logo (top right front)
box(14, 2.0, 4.0, 0, D / 2 + 0.2, 50.0, 'plastique_noir', 0.6)               # rear handle
# brushed steel pedal, rounded front
bm = bmesh.new(); pts = []
for i in range(17):
    a = math.pi * i / 16
    pts.append((6.5 * math.cos(a), -1.5 - 3.0 * math.sin(a)))
pts = [(6.5, 1.0)] + pts + [(-6.5, 1.0)]
bot = [bm.verts.new((x, y - D / 2, 1.6)) for x, y in pts]
top = [bm.verts.new((x, y - D / 2, 3.4)) for x, y in pts]
n = len(pts)
for i in range(n):
    bm.faces.new((bot[i], bot[(i + 1) % n], top[(i + 1) % n], top[i]))
bm.faces.new(top); bm.faces.new(bot[::-1])
me = bpy.data.meshes.new('ped'); bm.to_mesh(me); bm.free()
o = bpy.data.objects.new('ped', me); bpy.context.collection.objects.link(o); me.materials.append(M('inox_brosse'))
box(11, 0.15, 0.25, 0, -D / 2 - 3.6, 3.0, 'inox_poli')                        # pedal groove highlight
box(10, 3, 1.5, 0, -D / 2 - 0.5, 0.2, 'plastique_noir', 0.4)                  # pedal housing
export('poubelle_songmics', {'acier_noir_mat': ((0.07, 0.07, 0.075), 0.03, 2, ''),
                             'acier_noir_lid': ((0.06, 0.06, 0.065), 0.05, 3, ''),
                             'plastique_noir': ((0.03, 0.03, 0.03), 0.15, 15, ''),
                             'logo': ((0.13, 0.13, 0.14), 0.4, 40, ''),
                             'inox_brosse': ((0.78, 0.79, 0.80), 0.8, 80, ''),
                             'inox_poli': ((0.9, 0.9, 0.9), 0.9, 110, '')})
