import sys, os
src = open('/home/claude/scripts/make_items.py').read()
exec(src[:src.index("TEX = ")])
TEX = os.path.join(OUT, '_tex'); os.makedirs(TEX, exist_ok=True)
oak_texture(f'{TEX}/chene_skalsta.jpg', base=(0.80, 0.71, 0.55))
reset()
top = box(140, 80, 3.0, 0, 0, 72.0, 'chene_motif', bevel=0.2)
# closed rectangular (O-shaped) frames at both ends : 2 uprights + top rail + floor rail
for sx in (-1, 1):
    x = sx * 63.0
    for y in (-35.5, 35.5):
        box(4.0, 6.0, 72.0, x, y, 0, 'acier_noir_gris', bevel=0.3)       # uprights (flat bar, 6 cm seen from the side)
    box(4.0, 77.0, 4.0, x, 0, 68.0, 'acier_noir_gris', bevel=0.3)       # top rail
    box(4.0, 77.0, 4.0, x, 0, 0.6, 'acier_noir_gris', bevel=0.3)        # floor rail
    for y in (-35.5, 35.5):
        box(4.1, 6.1, 0.6, x, y, 0, 'patin_noir')
bpy.ops.object.select_all(action='DESELECT'); top.select_set(True); bpy.context.view_layer.objects.active = top
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.cube_project(cube_size=140.0); bpy.ops.object.mode_set(mode='OBJECT')
export('table_skalsta', {'chene_motif': ((1, 1, 1), 0.12, 25, 'map_Kd chene_skalsta.jpg\n'),
                         'acier_noir_gris': ((0.12, 0.12, 0.13), 0.3, 45, ''),
                         'patin_noir': ((0.05, 0.05, 0.05), 0.1, 10, '')},
       textures=[f'{TEX}/chene_skalsta.jpg'])
