import bpy, sys, json, math
a = json.loads(sys.argv[sys.argv.index('--')+1])
bpy.ops.wm.open_mainfile(filepath=a['blend'])
sc = bpy.context.scene
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes=True
w.node_tree.nodes['Background'].inputs['Color'].default_value=(0.9,0.9,0.92,1)
w.node_tree.nodes['Background'].inputs['Strength'].default_value=0.6
bpy.ops.mesh.primitive_plane_add(size=2000)
fl = bpy.context.active_object; m = bpy.data.materials.new('f'); m.use_nodes=True
m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(0.75,0.68,0.58,1); fl.data.materials.append(m)
L = bpy.data.lights.new('k','AREA'); L.size=150; L.energy=a.get('e',4e6)
o = bpy.data.objects.new('k',L); sc.collection.objects.link(o); o.location=(-150,-250,300)
o.rotation_euler=(math.radians(45),0,math.radians(-30))
cam = bpy.data.cameras.new('c'); cam.lens=a.get('lens',50); co=bpy.data.objects.new('c',cam); sc.collection.objects.link(co); sc.camera=co
co.location=a['cam']; cam.clip_end=10000
from mathutils import Vector
co.rotation_euler=(Vector(a['target'])-co.location).to_track_quat('-Z','Y').to_euler()
sc.render.engine='CYCLES'; sc.cycles.samples=a.get('s',48); sc.cycles.use_denoising=True
sc.render.resolution_x, sc.render.resolution_y = a.get('res',[1200,800])
sc.view_settings.view_transform='AgX'
sc.render.filepath=a['out']; bpy.ops.render.render(write_still=True)
