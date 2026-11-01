"""Lave-linge Bosch WGE02406FR Série 2 : 59.8 x 84.8 x 55, blanc, hublot, tiroir à lessive, sélecteur, écran."""
import sys, os, math
src = open('/home/claude/scripts/make_items.py').read()
exec(src[:src.index("TEX = ")])
reset()
W, H, Dp = 59.8, 84.8, 55.0
F = -Dp / 2  # front plane
box(W, Dp, H, 0, 0, 0, 'blanc', bevel=0.8, segs=3)
# top control zone
box(19, 0.8, 9.5, -17.5, F - 0.3, 72.5, 'blanc', bevel=0.4)                 # detergent drawer
box(10, 0.3, 1.2, -17.5, F - 0.75, 74.0, 'gris_clair')                       # drawer grip slot
box(6, 0.2, 1.0, -17.5, F - 0.75, 79.5, 'gris_texte')                        # BOSCH logo block
cyl(3.4, 1.6, 2.0, F - 0.6, 77.3, 'blanc', 40, axis='Y')                     # program knob
cyl(3.0, 0.4, 2.0, F - 1.5, 77.3, 'gris_clair', 40, axis='Y')
box(1.0, 0.3, 2.2, 2.0, F - 1.8, 78.6, 'gris_texte')                          # knob mark
for i in range(8):                                                           # program labels around the knob
    a = math.radians(-60 + i * 17)
    box(3.0, 0.15, 0.5, -6.5 + 0 * a, F - 0.1, 81.5 - i * 1.4, 'gris_texte')
    box(3.0, 0.15, 0.5, 10.5, F - 0.1, 81.5 - i * 1.4, 'gris_texte')
box(9.5, 0.3, 4.2, 20.0, F - 0.2, 77.5, 'noir_ecran')                         # display
box(3.2, 0.2, 1.4, 18.0, F - 0.4, 78.6, 'rouge_led')
for x in (16.5, 20.0, 23.5):
    box(2.6, 0.2, 1.2, x, F - 0.2, 74.0, 'gris_clair')                       # buttons
box(57, 0.2, 0.25, 0, F - 0.1, 70.6, 'gris_clair')                           # panel seam
# porthole : white ring + chrome-ish inner ring + tinted glass + drum
cx, cz = 0.0, 40.5
cyl(18.5, 2.4, cx, F - 1.1, cz, 'blanc_brillant', 72, axis='Y')
cyl(15.8, 2.8, cx, F - 1.5, cz, 'gris_clair', 72, axis='Y')
cyl(14.5, 3.4, cx, F - 1.9, cz, 'verre_hublot', 72, axis='Y')
cyl(13.0, 0.5, cx, F + 6, cz, 'inox_tambour', 72, axis='Y')                 # drum back
# service flap bottom right
cyl(6.2, 0.4, 19.5, F - 0.2, 8.5, 'blanc_brillant', 48, axis='Y')
box(W - 1, 0.3, 0.3, 0, F - 0.1, 2.0, 'gris_clair')                          # foot shadow line
export('lave_linge', {'blanc': ((0.95, 0.95, 0.95), 0.25, 40, ''),
                      'blanc_brillant': ((0.97, 0.97, 0.97), 0.5, 80, ''),
                      'gris_clair': ((0.78, 0.79, 0.80), 0.3, 40, ''),
                      'gris_texte': ((0.45, 0.46, 0.48), 0.1, 10, ''),
                      'noir_ecran': ((0.03, 0.03, 0.035), 0.8, 110, ''),
                      'rouge_led': ((0.95, 0.15, 0.10), 0.3, 30, ''),
                      'verre_hublot': ((0.55, 0.58, 0.62), 0.9, 120, 'd 0.45\n'),
                      'inox_tambour': ((0.70, 0.71, 0.72), 0.8, 90, '')})
print('WASHER OK')
