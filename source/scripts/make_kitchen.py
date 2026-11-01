"""Cuisine refaite proprement : façades finition 'Venus' (anthracite mat veiné), caissons, plinthes, plan de travail,
évier, robinet, lave-linge, crédence, meubles hauts. Garde les dimensions et l'implantation d'origine."""
import sys, os, math, shutil
src = open('/home/claude/scripts/make_items.py').read()
exec(src[:src.index("TEX = ")])
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
SRCX = '/home/claude/src/x'
TEX = os.path.join(OUT, '_tex'); os.makedirs(TEX, exist_ok=True)

# ---------- texture "Venus" : anthracite mat, fines veines claires et dorées (tileable) ----------
def venus(path, N=2048, seed=5, base=(0.235, 0.232, 0.232), nveins=16, alpha=1.0):
    rng = np.random.default_rng(seed)
    def pn(f, s):
        g = np.random.default_rng(s); F = np.fft.fft2(g.standard_normal((N, N)))
        k = np.hypot(np.fft.fftfreq(N)[:, None] * N, np.fft.fftfreq(N)[None, :] * N)
        x = np.real(np.fft.ifft2(F * np.exp(-(k / f) ** 2))); return (x - x.mean()) / x.std()
    base = np.array(base)
    v = 1 + 0.05 * pn(4, 1) + 0.03 * pn(25, 2) + 0.025 * pn(400, 3)
    img = np.clip(base * v[..., None], 0, 1)
    S = 2  # supersampling for thin anti-aliased veins
    layer = Image.new('RGBA', (N * S, N * S), (0, 0, 0, 0)); dr = ImageDraw.Draw(layer)
    def vein(x, y, ang, length, col, width):
        pts = [(x, y)]
        for _ in range(int(length / 6)):
            if rng.random() < 0.06: ang += rng.normal(0, 0.45)   # sharp kinks, straight segments
            else: ang += rng.normal(0, 0.015)
            x += 6 * S * math.cos(ang); y += 6 * S * math.sin(ang); pts.append((x, y))
            if rng.random() < 0.012:   # small branch
                vein(x, y, ang + rng.choice([-1, 1]) * rng.uniform(0.3, 0.7), length * 0.25, col, max(1, width - 1))
        for ox in (-N * S, 0, N * S):  # wrap -> tileable
            for oy in (-N * S, 0, N * S):
                dr.line([(px + ox, py + oy) for px, py in pts], fill=col, width=width)
    for i in range(nveins):
        main = rng.uniform(0.55, 0.85)  # mostly diagonal
        warm = rng.random() < 0.35
        warm = rng.random() < 0.6
        col = (186, 132, 100, int(alpha * rng.uniform(140, 220))) if warm else (196, 194, 190, int(alpha * rng.uniform(110, 200)))
        vein(rng.uniform(0, N * S), rng.uniform(0, N * S), main * math.pi if rng.random() < 0.5 else -main * math.pi / 2,
             rng.uniform(500, 1600), col, int(rng.choice([1, 2, 2, 3])))
    layer = layer.resize((N, N), Image.LANCZOS).filter(ImageFilter.GaussianBlur(0.4))
    a = np.asarray(layer).astype(np.float32) / 255
    img = img * (1 - a[..., 3:4]) + a[..., :3] * a[..., 3:4]
    Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).save(path, quality=93)
venus(f'{TEX}/venus.jpg')
venus(f'{TEX}/plan_venus.jpg', seed=9, base=(0.20, 0.20, 0.205), nveins=7, alpha=0.6)
for f in ('marbre.jpg', 'credence.jpg'):
    shutil.copy(f'{SRCX}/cuisine_nord/{f}', f'{TEX}/{f}')

MT = {
    'venus':        ((1, 1, 1), 0.12, 18, 'map_Kd venus.jpg\n'),
    'plan_travail': ((1, 1, 1), 0.2, 35, 'map_Kd plan_venus.jpg\n'),
    'credence':     ((1, 1, 1), 0.3, 60, 'map_Kd credence.jpg\n'),
    'caisson':      ((0.16, 0.16, 0.165), 0.1, 10, ''),
    'plinthe':      ((0.13, 0.13, 0.135), 0.15, 15, ''),
    'laiton':       ((0.60, 0.42, 0.29), 0.7, 70, ''),
    'evier_noir':   ((0.09, 0.09, 0.10), 0.3, 40, ''),
    'inox':         ((0.75, 0.75, 0.76), 0.85, 90, ''),
    'blanc':        ((0.94, 0.94, 0.93), 0.35, 60, ''),
    'hublot':       ((0.10, 0.11, 0.13), 0.9, 120, 'd 0.85\n'),
    'gris_joint':   ((0.05, 0.05, 0.05), 0.0, 1, ''),
    'gris_led':     ((0.70, 0.71, 0.72), 0.6, 60, ''),
    'led':          ((1.0, 1.0, 1.0), 0.2, 20, ''),
}

def uv_box(o, size):
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active = o
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.cube_project(cube_size=size); bpy.ops.object.mode_set(mode='OBJECT')

# coordinates: x from 0 (left) to W ; y : 0 = wall (back), -D = front ; z up. Front faces -Y.
def B(x0, x1, y0, y1, z0, z1, mat, bevel=0.0):
    return box(x1 - x0, y1 - y0, z1 - z0, (x0 + x1) / 2, (y0 + y1) / 2, z0, mat, bevel)

GAP = 0.3
def door(x0, x1, z0, z1, handle='top_h', front_y=-62):
    o = B(x0 + GAP, x1 - GAP, front_y, front_y + 1.9, z0 + GAP, z1 - GAP, 'venus', 0.12); uv_box(o, 120)
    cx = (x0 + x1) / 2
    L = min(26.0, (x1 - x0) * 0.55)
    if handle == 'top_h':        # thin bronze profile sitting on the top edge of the door
        B(cx - L / 2, cx + L / 2, front_y - 0.4, front_y + 2.4, z1 - GAP - 0.1, z1 - GAP + 1.1, 'laiton', 0.1)
        B(cx - L / 2, cx + L / 2, front_y - 0.6, front_y - 0.1, z1 - GAP - 1.6, z1 - GAP + 1.1, 'laiton', 0.1)
    elif handle == 'bottom_h':   # same profile on the bottom edge for wall units
        B(cx - L / 2, cx + L / 2, front_y - 0.4, front_y + 2.4, z0 + GAP - 1.1, z0 + GAP + 0.1, 'laiton', 0.1)
        B(cx - L / 2, cx + L / 2, front_y - 0.6, front_y - 0.1, z0 + GAP - 1.1, z0 + GAP + 1.6, 'laiton', 0.1)
    return o

def base_run(W, D, top=90.0):
    B(0, W, -D + 7, -0.5, 0, 12, 'plinthe')                         # recessed plinth
    B(0, W, -58.5, -0.5, 12, top - 3.8, 'caisson')                  # carcasses
    wt = B(0, W, -D, 0, top - 3.8, top, 'plan_travail', 0.15); uv_box(wt, 100)   # worktop 3.8 cm
    cr = B(0, W, -1.0, 0, top, 150, 'credence'); uv_box(cr, 120)      # splashback tiles on the wall

def wall_cab(x0, x1, z0, z1, depth, doors):
    B(x0, x1, -depth + 1.9, 0, z0, z1, 'caisson')
    w = (x1 - x0) / doors
    for i in range(doors):
        door(x0 + i * w, x0 + (i + 1) * w, z0, z1, 'bottom_h', front_y=-depth)

# ================= CUISINE NORD : 221 x 65 x 220 =================
reset()
W, D = 221, 65
base_run(W, D)
# 0-60 : niche lave-vaisselle (appareil posé à part) -> pas de façade, fond sombre
B(0.3, 59.7, -58, -57.5, 10, 86, 'gris_joint')
# 60-120 : niche lave-linge (appareil Bosch posé à part)
B(60.3, 119.7, -58, -57.5, 12, 86, 'gris_joint')
# 120-221 : meuble évier 2 portes
door(120, 170.5, 12, 86.2)
door(170.5, 221, 12, 86.2)
# évier noir 1 bac + égouttoir (posé sur le plan)
B(124, 212, -56, -6, 90, 90.4, 'evier_noir', 0.2)
for i in range(5):
    B(127, 157, -46 + i * 8, -45 + i * 8, 90.4, 90.55, 'gris_joint')
B(162, 208, -51, -11, 90.4, 90.42, 'gris_joint')                # bowl edge shadow
B(163.5, 206.5, -49.5, -12.5, 72, 90.41, 'evier_noir')          # bowl (top face at the rim)
B(164, 206, -49, -13, 90.3, 90.45, 'gris_joint')                # dark opening
cyl(2.0, 0.2, 185, -31, 90.42, 'inox', 24)                      # drain
# robinet col de cygne inox
cyl(2.6, 2.0, 185, -5.5, 90.4, 'inox', 24)
tube((185, -5.5, 92), (185, -5.5, 117), 1.3, 'inox', 20)
tube((185, -5.5, 117), (185, -22, 117), 1.1, 'inox', 20)
tube((185, -22, 117), (185, -22, 109), 1.1, 'inox', 20)
tube((185, -3.5, 104), (191, -3.5, 106), 0.6, 'inox', 10)       # lever
# meubles hauts 80-200 (2 x 60), 150-220
wall_cab(80, 200, 150, 220, 35, 2)
for xl in (108, 172):   # square LED under-cabinet lights (cf. photo)
    B(xl - 3.2, xl + 3.2, -28, -21.6, 149.2, 150, 'gris_led', 0.2)
    B(xl - 2.4, xl + 2.4, -27.2, -22.4, 149.0, 149.25, 'led')
export('cuisine_nord', {k: v for k, v in MT.items()}, textures=[f'{TEX}/{t}' for t in ('venus.jpg', 'plan_venus.jpg', 'credence.jpg')])

# ================= CUISINE EST : 102 x 64 x 220 (four 60 + placard 42), cf. photo =================
reset()
W, D = 102, 64
base_run(W, D)
B(0.3, 59.7, -58, -57.5, 12, 86, 'gris_joint')                  # oven niche back (oven = separate piece)
door(0, 60, 12, 20, None)                                       # strip under the oven
door(0, 60, 79.6, 86.2, None)                                   # strip above the oven
door(60, 102, 12, 86.2)                                         # narrow cabinet right of the oven
wall_cab(0, 60, 165, 220, 38, 1)
B(4, 56, -34, -4, 164.6, 165.1, 'gris_joint')
export('cuisine_est', {k: v for k, v in MT.items()}, textures=[f'{TEX}/{t}' for t in ('venus.jpg', 'plan_venus.jpg', 'credence.jpg')])
print('KITCHEN DONE')
