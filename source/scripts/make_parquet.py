"""Procedural, seamlessly tiling light-oak plank texture (chêne clair brossé)."""
import numpy as np
from PIL import Image, ImageFilter
import sys

N = 2048
ROWS = 8
rng = np.random.default_rng(7)
out = sys.argv[1]

def periodic_noise(sx, sy, seed):
    """Tileable noise via FFT filtering; sx/sy = cut-off frequencies (cycles per tile)."""
    r = np.random.default_rng(seed)
    w = r.standard_normal((N, N))
    F = np.fft.fft2(w)
    ky = np.fft.fftfreq(N)[:, None] * N
    kx = np.fft.fftfreq(N)[None, :] * N
    filt = np.exp(-(kx / sx) ** 2 - (ky / sy) ** 2)
    n = np.real(np.fft.ifft2(F * filt))
    return (n - n.mean()) / n.std()

warp   = periodic_noise(1.2, 5.0, 1)    # long, slow waves -> grain flow
rings  = periodic_noise(2.5, 160.0, 2)    # growth-ring streaks
fiber  = periodic_noise(25.0, 500.0, 3)  # fine fibres / brushing
blotch = periodic_noise(4.0, 8.0, 4)
streak = periodic_noise(4.0, 700.0, 6)    # soft tone variation
pores  = periodic_noise(250.0, 900.0, 5)

Y, X = np.mgrid[0:N, 0:N].astype(np.float32)
h = N // ROWS
img = np.zeros((N, N, 3), np.float32)
base = np.array([0.835, 0.735, 0.610])  # chêne clair naturel (sRGB)
mask_gap = np.ones((N, N), np.float32)

for r in range(ROWS):
    y0, y1 = r * h, (r + 1) * h
    # plank joints along the row (wrap-around so the tile is seamless)
    xs = [rng.uniform(0, N)]
    while True:
        L = rng.uniform(0.45, 1.0) * N
        if xs[-1] + L >= xs[0] + N - 0.25 * N: break
        xs.append(xs[-1] + L)
    joints = [x % N for x in xs]
    # segment ids for each x
    order = np.sort(np.array(joints))
    seg = np.searchsorted(order, X[y0, :], side='right') % len(order)
    for s in range(len(order)):
        cols = seg == s
        tone = rng.normal(0, 0.025)
        warm = abs(rng.normal(0, 0.012))
        shift = int(rng.integers(0, N))
        ly = (Y[y0:y1, cols] - y0) / h
        wv = np.roll(warp, shift, axis=1)[y0:y1][:, cols]
        rg = np.roll(rings, shift, axis=1)[y0:y1][:, cols]
        fb = np.roll(fiber, shift, axis=1)[y0:y1][:, cols]
        bl = np.roll(blotch, shift, axis=1)[y0:y1][:, cols]
        st = np.roll(streak, shift, axis=1)[y0:y1][:, cols]
        freq = rng.uniform(4, 9)
        lines = np.sin(2 * np.pi * (ly * freq + 0.9 * wv + 0.15 * rg))
        lines = np.clip(lines, 0, 1) ** 4          # thin late-wood lines
        thin = np.clip(1 - np.abs(st) * 1.6, 0, 1) ** 3
        v = 1.0 + tone + 0.015 * bl - 0.11 * lines - 0.07 * thin - 0.035 * np.clip(fb, -2, 2)
        c = np.stack([v * (base[0] + warm), v * base[1], v * (base[2] - warm * 0.6)], -1)
        img[y0:y1][:, cols] = c
    # gaps: long edge + end joints (subtle bevel)
    for d, k in ((0, 0.70), (1, 0.85), (2, 0.95)):
        mask_gap[(y0 + d) % N, :] *= k
    for j in joints:
        jx = int(j)
        for d, k in ((0, 0.72), (1, 0.88)):
            mask_gap[y0:y1, (jx + d) % N] *= k

# knots (few, small, like the reference)
for _ in range(16):
    cx, cy = rng.uniform(0, N), rng.uniform(0, N)
    rx, ry = rng.uniform(10, 22), rng.uniform(6, 12)
    dx = (X - cx + N / 2) % N - N / 2
    dy = (Y - cy + N / 2) % N - N / 2
    d = np.sqrt((dx / rx) ** 2 + (dy / ry) ** 2)
    core = np.exp(-d ** 2 * 1.5)
    halo = np.exp(-d ** 2 * 0.12) * (0.5 + 0.5 * np.sin(d * 5)) * 0.25
    k = (0.6 * core + 0.15 * halo)[..., None]
    img = img * (1 - k) + k * np.array([0.42, 0.32, 0.22])

img *= (1 - 0.04 * np.clip(pores, 0, 3) / 3)[..., None]
img *= mask_gap[..., None]
img = np.clip(img, 0, 1)
im = Image.fromarray((img * 255).astype(np.uint8))
im = im.filter(ImageFilter.GaussianBlur(0.6))
im.save(out, quality=92)
print('saved', out)
