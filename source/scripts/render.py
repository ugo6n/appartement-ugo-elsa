import bpy, sys, math, json
from mathutils import Vector

args = json.loads(sys.argv[sys.argv.index('--')+1])
bpy.ops.wm.open_mainfile(filepath='/home/claude/scene.blend')
sc = bpy.context.scene
def P(x, y, z): return Vector((x/100.0, -y/100.0, z/100.0))

# ---- world: soft sky ----
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
bg = w.node_tree.nodes['Background']
bg.inputs['Color'].default_value = (0.55, 0.7, 0.95, 1)
bg.inputs['Strength'].default_value = args.get('sky', 2.5)

# ---- exterior environment + sky ----
sys.path.insert(0, '/home/claude/scripts'); import env
for o in list(sc.objects):
    if o.name.startswith('ground'): bpy.data.objects.remove(o)
_env_pending = True
# ---- sun from the west (through the baie vitrée / bedroom window) ----
sun = bpy.data.lights.new('sun', 'SUN'); sun.energy = args.get('sun', 4.5)
sun.color = (1.0, 0.86, 0.68); sun.angle = math.radians(2.5)
so = bpy.data.objects.new('sun', sun); sc.collection.objects.link(so)
az = math.radians(args.get('sun_az', 250)); el = math.radians(args.get('sun_el', 18))
d = Vector((math.cos(az)*math.cos(el), math.sin(az)*math.cos(el), math.sin(el)))  # direction to the sun
so.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
env.setup_env(sc, args.get('sun_az', 250), args.get('sun_el', 18), args.get('skyk', 1.0))

# ---- portal-like area lights in window openings for soft daylight ----
for (x, y, h, wdt, z0) in [(190, 205, 215, 208, 0), (12, 562, 186, 158, 19)]:
    L = bpy.data.lights.new('win', 'AREA'); L.shape = 'RECTANGLE'
    L.size, L.size_y = wdt/100, h/100; L.energy = args.get('win', 180); L.color = (0.85, 0.92, 1.0)
    o = bpy.data.objects.new('win', L); sc.collection.objects.link(o)
    o.location = P(x+10, y, z0 + h/2)
    o.rotation_euler = (0, math.radians(90), 0)  # facing +X (into the flat)
    o.visible_camera = False; o.visible_glossy = False; o.visible_transmission = False

# ---- warm lamps: suspensions ----
lamp_on = args.get('lamps', True)
for o in list(sc.objects):
    if o.get('model', '').startswith('suspension') and lamp_on:
        L = bpy.data.lights.new('bulb', 'POINT'); L.energy = args.get('bulb', 35)
        L.color = (1.0, 0.72, 0.42); L.shadow_soft_size = 0.04
        lo = bpy.data.objects.new('bulb', L); sc.collection.objects.link(lo)
        lo.location = P(o['x'], o['y'], o['elev'] + 12)
# recessed LED ceiling spots (spot_led pieces) -> real downlights
for o in list(sc.objects):
    if o.get('model', '') == 'spot_led':
        L = bpy.data.lights.new('spot', 'SPOT'); L.energy = args.get('spot', 45)
        L.color = (1.0, 0.86, 0.70); L.spot_size = math.radians(110); L.spot_blend = 0.7; L.shadow_soft_size = 0.04
        lo = bpy.data.objects.new('spot', L); sc.collection.objects.link(lo)
        lo.location = P(o['x'], o['y'], o['elev'] - 0.6)          # pointing down by default
# kitchen under-cabinet LED spots (cool white, pointing down)
for (x, y) in [(746, 56), (810, 56)]:
    L = bpy.data.lights.new('ledk', 'SPOT'); L.energy = args.get('ledk', 8); L.color = (0.92, 0.95, 1.0)
    L.spot_size = math.radians(120); L.spot_blend = 0.8; L.shadow_soft_size = 0.03
    lo = bpy.data.objects.new('ledk', L); sc.collection.objects.link(lo); lo.location = P(x, y, 148.8)
# bathroom: soft ceiling bounce (no window in the room) + LED mirror strip
for (x, y, w, d, e) in [(671, 585, 2.6, 1.6, args.get('sde_fill', 40)), (878, 585, 0.7, 1.5, args.get('wc_fill', 20))]:
    L = bpy.data.lights.new('fill', 'AREA'); L.shape = 'RECTANGLE'; L.size, L.size_y = w, d
    L.energy = e; L.color = (1.0, 0.9, 0.78)
    lo = bpy.data.objects.new('fill', L); sc.collection.objects.link(lo); lo.location = P(x, y, 246)
    lo.visible_camera = False; lo.visible_glossy = False
for m in bpy.data.materials:
    if m.name.split('.')[0] == 'led' and m.node_tree:
        b = m.node_tree.nodes.get('Principled BSDF')
        if b:
            b.inputs['Emission Color'].default_value = (1.0, 0.93, 0.82, 1); b.inputs['Emission Strength'].default_value = args.get('led', 12)
# extra room-specific practical lights
for (x, y, z, e, r) in args.get('extra', []):
    L = bpy.data.lights.new('x', 'POINT'); L.energy = e; L.color = (1.0, 0.78, 0.55); L.shadow_soft_size = r
    lo = bpy.data.objects.new('x', L); sc.collection.objects.link(lo); lo.location = P(x, y, z)

# ---- camera ----
cam = bpy.data.cameras.new('cam'); cam.lens = args.get('lens', 18); cam.sensor_width = 36
co = bpy.data.objects.new('cam', cam); sc.collection.objects.link(co); sc.camera = co
co.location = P(*args['cam'])
t = P(*args['target'])
q = (t - co.location).to_track_quat('-Z', 'Y'); co.rotation_euler = q.to_euler()
cam.clip_start = 0.05
if args.get('ortho'):
    cam.type = 'ORTHO'; cam.ortho_scale = args['ortho']; co.rotation_euler = (0, 0, 0)
if args.get('pano'):
    cam.type = 'PANO'
    try: cam.panorama_type = 'EQUIRECTANGULAR'
    except Exception: cam.cycles.panorama_type = 'EQUIRECTANGULAR'
    co.rotation_euler = (math.pi / 2, 0, 0)   # image centre = plan north (-y)
# hide objects blocking the view (e.g. wall in front of camera)
for name in args.get('hide', []):
    for o in sc.objects:
        if o.name.startswith(name): o.hide_render = True

# ---- render ----
sc.render.engine = 'CYCLES'
sc.cycles.device = 'CPU'
sc.cycles.samples = args.get('samples', 256)
sc.cycles.use_denoising = True
sc.cycles.use_preview_denoising = True
sc.cycles.preview_samples = 64
sc.cycles.denoiser = 'OPENIMAGEDENOISE'
sc.cycles.max_bounces = 8; sc.cycles.diffuse_bounces = 4; sc.cycles.glossy_bounces = 4
sc.cycles.transmission_bounces = 8; sc.cycles.caustics_reflective = False; sc.cycles.caustics_refractive = False
sc.cycles.sample_clamp_indirect = 8
sc.render.resolution_x, sc.render.resolution_y = args.get('res', [1920, 1280])
sc.render.resolution_percentage = 100
sc.view_settings.view_transform = 'AgX'
sc.view_settings.look = args.get('look', 'AgX - Medium High Contrast')
sc.view_settings.exposure = args.get('exposure', 0.0)
sc.render.image_settings.file_format = 'JPEG'; sc.render.image_settings.quality = 94
sc.render.filepath = args['out']
if args.get('save'):
    import re as _re
    src = open('/home/claude/scripts/enhance_sh3d.py', encoding='utf-8').read()
    blk = src[src.index('views = ['):src.index(']\ndef cam_xml')+1]
    ns = {}; exec(blk, ns)
    for (name, x, y, z, tx, ty, tz, fov) in ns['views']:
        c = bpy.data.cameras.new(name); c.sensor_width = 36; c.sensor_fit = 'HORIZONTAL'
        c.angle = fov; c.clip_start = 0.05
        o = bpy.data.objects.new(name, c); sc.collection.objects.link(o)
        o.location = P(x, y, z)
        o.rotation_euler = (P(tx, ty, tz) - o.location).to_track_quat('-Z', 'Y').to_euler()
    sc.camera = bpy.data.objects[ns['views'][0][0]]
    bpy.data.objects.remove(co)
    sc.render.image_settings.file_format = 'PNG'
    sc.render.filepath = '//rendus/'
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=args['save'], compress=True)
    print('SAVED', args['save'])
else:
    bpy.ops.render.render(write_still=True)
print('DONE', args['out'])
