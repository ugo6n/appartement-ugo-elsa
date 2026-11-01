import sys, os, math
src = open('/home/claude/scripts/make_items.py').read()
exec(src[:src.index("TEX = ")])          # helper functions (box, cyl, export, ...)
from PIL import Image, ImageDraw

# ---------------- Four Rosières FC3O5871PN : 59.5 x 56.8 x 59.5, façade verre noir, poignée + manettes inox ----------------
reset()
box(56, 54, 58, 0, 1.5, 0.5, 'noir_mat')                                   # body (hidden in cabinet)
box(59.5, 1.8, 47.5, 0, -27.5, 0, 'verre_noir_four', bevel=0.3)            # glass door
box(52, 0.3, 33, 0, -28.5, 6, 'verre_fume_hublot')                         # darker window zone
box(59.5, 1.8, 11.8, 0, -27.5, 47.7, 'noir_bandeau', bevel=0.3)            # control strip
tube((-24, -31.6, 44.0), (24, -31.6, 44.0), 0.9, 'inox', 16)               # bar handle
for x in (-24, 24):
    tube((x, -28.4, 44.0), (x, -31.6, 44.0), 0.6, 'inox', 10)
for x in (-21, 21):                                                        # 2 knobs
    cyl(2.1, 2.2, x, -29.4, 53.6, 'inox', 32, axis='Y')
box(11, 0.3, 3.2, 0, -28.5, 52.0, 'ecran_noir')                            # display
box(5.5, 0.2, 1.4, 0, -28.7, 52.9, 'affichage_blanc')
for x in (-9, -7, 7, 9):
    cyl(0.45, 0.2, x, -28.6, 53.6, 'affichage_blanc', 10, axis='Y')
export('four_rosieres', {'noir_mat': ((0.05, 0.05, 0.05), 0.1, 10, ''),
                         'verre_noir_four': ((0.035, 0.035, 0.04), 0.9, 120, ''),
                         'verre_fume_hublot': ((0.015, 0.015, 0.018), 0.9, 120, ''),
                         'noir_bandeau': ((0.04, 0.04, 0.045), 0.8, 110, ''),
                         'inox': ((0.75, 0.75, 0.76), 0.85, 90, ''),
                         'ecran_noir': ((0.01, 0.01, 0.01), 0.6, 80, ''),
                         'affichage_blanc': ((0.95, 0.95, 0.95), 0.2, 20, '')})

# ---------------- Plaque induction EssentielB ETI31c : 59 x 52 x 6.2, 3 foyers ----------------
W, D = 590, 520  # 1 px = 1 mm
img = Image.new('RGB', (W, D), (10, 10, 12)); dr = ImageDraw.Draw(img)
def ring(cx, cy, d, col=(105, 105, 110)):
    r = d / 2
    dr.ellipse((cx - r, cy - r, cx + r, cy + r), outline=col, width=3)
    dr.ellipse((cx - r + 14, cy - r + 14, cx + r - 14, cy + r - 14), outline=(45, 45, 48), width=2)
# image y=0 is the rear edge, y=D the front edge (controls)
ring(405, 215, 290)          # grand foyer 29 cm, à droite
ring(140, 135, 210)          # arrière gauche 21 cm
ring(140, 345, 160)          # avant gauche 16 cm
for i, x in enumerate(range(150, 450, 50)):   # touch controls along the front
    dr.ellipse((x - 9, 470 - 9, x + 9, 470 + 9), outline=(120, 120, 125), width=2)
dr.rectangle((270, 455, 320, 485), outline=(150, 40, 35), width=2)   # red display
dr.rectangle((0, 0, W - 1, D - 1), outline=(60, 60, 62), width=4)    # bevelled edge
d = os.path.join(OUT, '_tex'); os.makedirs(d, exist_ok=True)
img.save(f'{d}/plaque_induction.png')
reset()
box(56, 49, 5.6, 0, 0, 0, 'noir_mat')
top = box(59, 52, 0.6, 0, 0, 5.6, 'vitroceramique', bevel=0.15)
# planar UVs on the glass top
me = top.data
uv = me.uv_layers.new()
for poly in me.polygons:
    for li in poly.loop_indices:
        co = me.vertices[me.loops[li].vertex_index].co
        uv.data[li].uv = ((co.x + 29.5) / 59, (co.y + 26) / 52)   # v=0 front(-Y), v=1 rear
export('plaque_induction', {'noir_mat': ((0.05, 0.05, 0.05), 0.1, 10, ''),
                            'vitroceramique': ((1, 1, 1), 0.9, 120, 'map_Kd plaque_induction.png\n')},
       textures=[f'{d}/plaque_induction.png'])
print('DONE')
