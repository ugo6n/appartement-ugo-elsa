import sys, os
src = open('/home/claude/scripts/make_items.py').read()
exec(src[:src.index("TEX = ")])
reset()
W, D, H = 147.0, 39.0, 77.0
T = 3.9; t = 1.6
box(W, D, T, 0, 0, H - T, 'blanc_kallax')                     # top
box(W - 0.4, D - 0.4, T, 0, 0.2, 0, 'blanc_kallax')            # bottom (slightly smaller -> no coplanar faces)
for sx in (-1, 1):
    box(T, D - 0.2, H - 2 * T + 0.4, sx * (W / 2 - T / 2 - 0.1), 0.1, T - 0.2, 'blanc_kallax')   # sides
iw = (W - 2 * T - 3 * t) / 4
for i in range(1, 4):
    x = -W / 2 + T + i * iw + (i - 0.5) * t
    box(t, D - 0.6, H - 2 * T + 0.2, x, 0.3, T - 0.1, 'blanc_kallax')     # vertical dividers, set back
box(W - 2 * T + 0.2, D - 0.6, t, 0, 0.3, H / 2 - t / 2, 'blanc_kallax')    # middle shelf, set back
box(W - 2 * T + 0.1, 0.6, H - 2 * T + 0.1, 0, D / 2 - 0.25, T - 0.05, 'blanc_fond')  # back panel
export('kallax', {'blanc_kallax': ((0.93, 0.93, 0.92), 0.12, 20, ''), 'blanc_fond': ((0.88, 0.88, 0.87), 0.05, 10, '')})
