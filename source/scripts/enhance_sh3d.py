"""Improve lighting / photo quality of a Sweet Home 3D file (Home.xml based)."""
import re, math, os, shutil, sys, zipfile

SRC = '/home/claude/src/x'
WORK = '/home/claude/enh'
OUT = '/home/claude/out/Appartement-303_eclairage-HD.sh3d'
shutil.rmtree(WORK, ignore_errors=True); shutil.copytree(SRC, WORK)
xml = open(f'{WORK}/Home.xml', encoding='utf-8').read()

# 0) Vrais miroirs : diffus quasi noir + spéculaire blanc + brillance max
#    -> dans le rendu photo de SH3D, la surface ne renvoie plus que le reflet
MIRROR = 'newmtl miroir\nKa 0 0 0\nKd 0.020 0.022 0.024\nKs 1 1 1\nNs 128\nillum 3\n'
for model in ('vasque', 'miroir_ikornnes'):
    p = f'{WORK}/{model}/model.mtl'
    t = open(p).read()
    t = re.sub(r'newmtl miroir\n(?:(?!newmtl).)*', MIRROR, t, flags=re.S)
    open(p, 'w').write(t)
TIME = '1793543400000'  # 1 nov. 2026, 15:30 heure de Paris : soleil bas d'ouest/sud-ouest

# 0b) Retirer les vantaux des portes salle d'eau et WC (gênent la visite)
xml = re.sub(r"  <pieceOfFurniture [^>]*model='(?:dsde|dwc)_vantail/model\.obj'[^>]*/>\n", '', xml)
for d in ('dsde_vantail', 'dwc_vantail'):
    shutil.rmtree(f'{WORK}/{d}', ignore_errors=True)

# 0c) Nouveau parquet chêne clair
shutil.copy('/home/claude/out/parquet_chene_clair.jpg', f'{WORK}/sol_parquet/parquet_chene_clair.jpg')
os.remove(f'{WORK}/sol_parquet/parquet.jpg')
open(f'{WORK}/sol_parquet/model.mtl', 'w').write(
    'newmtl sol_parquet\nKa 0.2 0.2 0.2\nKd 1.000 1.000 1.000\nKs 0.08 0.08 0.07\nNs 25\nmap_Kd parquet_chene_clair.jpg\n')

# 0d) Canapé OMHU Teddy remodélisé
shutil.rmtree(f'{WORK}/teddy')
os.makedirs(f'{WORK}/teddy')
for fn in ('model.obj', 'model.mtl', 'teddy_emeraude.jpg'):
    shutil.copy(f'/home/claude/teddy_new/{fn}', f'{WORK}/teddy/{fn}')

# 0e) Suspension cuisine -> Sklum Bezany (verre cannelé multicolore)
shutil.rmtree(f'{WORK}/suspension_perles')
shutil.copytree('/home/claude/items/suspension_perles', f'{WORK}/suspension_perles',
                ignore=shutil.ignore_patterns('*.blend', '*.blend1'))
xml = re.sub(r"name='Suspension cuisine[^']*'( model='suspension_perles/model\.obj' icon='icon\.png' x='[^']*' y='[^']*' elevation=')[^']*(' width=')[^']*(' depth=')[^']*(' height=')[^']*'",
             r"name='Suspension cuisine Sklum Bezany (verre rose, vert, lilas – laiton)'\g<1>180\g<2>15\g<3>15\g<4>70'", xml)

# 0f) Mur avancé derrière la cuisine (retour de mur à droite du frigo, cf. photo)
RETOUR = 10  # cm
xml = xml.replace("</home>", f"  <wall id='wRetourCuisine' xStart='636' yStart='{21 + RETOUR/2}' xEnd='859' yEnd='{21 + RETOUR/2}' height='250' thickness='{RETOUR}' pattern='hatchUp'/>\n</home>")
xml = re.sub(r"(model='cuisine_nord/model\.obj' icon='icon\.png' x='748\.5' y=')53\.5'", lambda m: m.group(1) + f"{53.5 + RETOUR}'", xml)

# 0g) Nouveaux modèles : chaises Jolie, lit/couette, bureau, chaise bureau, chevets, frigo, table, lave-vaisselle
def replace_model(folder, src):
    shutil.rmtree(f'{WORK}/{folder}', ignore_errors=True)
    shutil.copytree(src, f'{WORK}/{folder}', ignore=shutil.ignore_patterns('*.blend', '*.blend1'))
replace_model('chaise_jolie', '/home/claude/items/chaise_jolie')
replace_model('lit_140', '/home/claude/bed')
for f in ('bureau', 'chaise_bureau', 'babel', 'frigo', 'table_skalsta', 'lave_vaisselle', 'four_rosieres', 'plaque_induction', 'cuisine_nord', 'cuisine_est', 'lave_linge', 'litiere_catlink', 'arbre_chat_marcelo', 'poubelle_inox', 'poubelle_songmics', 'switch_dock', 'videoprojecteur', 'kallax'):
    replace_model(f, f'/home/claude/items/{f}')

def set_piece(model, **kw):
    global xml
    def fix(m):
        s = m.group(0)
        for k, v in kw.items():
            s = re.sub(rf" {k}='[^']*'", f" {k}='{v}'", s)
        return s
    xml = re.sub(rf"<pieceOfFurniture [^>]*model='{model}/model\.obj'[^>]*/>", fix, xml)
set_piece('bureau', name='Bureau IKEA LAGKAPTEN / ALEX 120x60 blanc', x=100, y=422, width=120, depth=60, height=73)
set_piece('chaise_bureau', name='Chaise pivotante IKEA LOBERGET / MALSKÄR blanc', x=108, y=478, width=67, depth=67, height=90)
xml = re.sub(r"(<pieceOfFurniture name=')Chevet Sklum Babel vert olive(' model='babel/model\.obj' icon='icon\.png' x=')141\.0(' y='663\.0' elevation='0' width=')30(' depth=')30(' height=')40'",
             r"\1Chevet Kartell Componibili rond vert\g<2>137\g<3>30\g<4>30\g<5>40'", xml)
xml = re.sub(r"(<pieceOfFurniture name=')Chevet Sklum Babel vert olive(' model='babel/model\.obj' icon='icon\.png' x=')323\.0(' y='663\.0' elevation='0' width=')30(' depth=')30(' height=')40'",
             r"\1Chevet Kartell Componibili rond vert\g<2>327\g<3>30\g<4>30\g<5>40'", xml)
set_piece('frigo', name='Réfrigérateur LISTO blanc (2 portes)', x=607, y=50, width=55, depth=58, height=144)
set_piece('table_skalsta', name='Table IKEA SKÄLSTA 140x80 chêne / pieds U noir-gris', width=140, depth=80, height=75)
xml = xml.replace("</home>", "  <pieceOfFurniture name='Lave-vaisselle Beko DVN06431A anthracite' model='lave_vaisselle/model.obj' icon='icon.png' "
                  "x='668' y='63.5' elevation='0' width='59.8' depth='60' height='85' angle='0' movable='true' resizable='true'/>\n"
                  "  <pieceOfFurniture name='Lave-linge Bosch WGE02406FR Série 2' model='lave_linge/model.obj' icon='icon.png' "
                  "x='728' y='66' elevation='0' width='59.8' depth='55' height='84.8' angle='0' movable='true' resizable='true'/>\n"
                  "  <pieceOfFurniture name='Four Rosières FC3O5871PN (verre noir, inox)' model='four_rosieres/model.obj' icon='icon.png' "
                  "x='887.9' y='187' elevation='20' width='59.5' depth='56.8' height='59.5' angle='1.5707963267948966' movable='true' resizable='true'/>\n"
                  "  <pieceOfFurniture name='Plaque induction EssentielB ETI31c (3 foyers)' model='plaque_induction/model.obj' icon='icon.png' "
                  "x='887' y='187' elevation='84.8' width='59' depth='52' height='6.2' angle='1.5707963267948966' movable='true' resizable='true'/>\n</home>")

set_piece('cuisine_est', name='Cuisine – four, plaque, placard (finition Venus)', y=208, width=102)
set_piece('cuisine_nord', name='Cuisine – lave-vaisselle, lave-linge, évier (finition Venus)')
xml = xml.replace("</home>", "  <wall id='wRetourFour' xStart='859' yStart='268' xEnd='923' yEnd='268' height='250' thickness='18' pattern='hatchUp'/>\n</home>")

xml = re.sub(r"(model='babel/model\.obj' icon='icon\.png' x='[^']*' y='[^']*' elevation='0' width='30' depth='30' height='40' angle=')0'", r"\g<1>3.141592653589793'", xml)
set_piece('switch_dock', name='Console de jeu dans son dock', width=24.2, depth=5.4, height=15.8)
set_piece('videoprojecteur', name='Vidéoprojecteur XGIMI Horizon Pro sur pied', width=26, depth=22.7, height=114.5)
set_piece('poubelle_songmics', name='Poubelle cuisine SONGMICS 30 L noire (pédale)', x=740, y=261.5, width=34.8, depth=29.7, height=63.3, angle=3.141592653589793)
set_piece('poubelle_inox', name='Poubelle inox à pédale', angle=3.141592653589793)
set_piece('litiere_catlink', name='Litière CATLINK Open-X (avec dessus)', width=53.4, depth=58.5, height=59.2)
set_piece('arbre_chat_marcelo', name='Arbre à chat Leeby Marcelo bleu-gris', width=39, depth=38.5, height=85.5)

xml = re.sub(r"  <pieceOfFurniture [^>]*model='winnie_cuddleez/model\.obj'[^>]*/>\n", '', xml)
shutil.rmtree(f'{WORK}/winnie_cuddleez', ignore_errors=True)

# chaises plus sous la table, litière et objets de l'étagère retirés (sauf l'affiche)
for m in ('litiere_catlink', 'winnie', 'vase_succulente', 'vase_fleurs', 'lego_mcqueen', 'chameau', 'elephant'):
    xml = re.sub(r"  <pieceOfFurniture [^>]*model='" + m + r"/model\.obj'[^>]*/>\n", '', xml)
    shutil.rmtree(f'{WORK}/{m}', ignore_errors=True)
xml = xml.replace("model='chaise_jolie/model.obj' icon='icon.png' x='533.0'", "model='chaise_jolie/model.obj' icon='icon.png' x='549.0'")
xml = xml.replace("model='chaise_jolie/model.obj' icon='icon.png' x='667.0'", "model='chaise_jolie/model.obj' icon='icon.png' x='651.0'")

# 1) Environment : best photo quality, warm ambient light, HD photo size
xml = re.sub(r"<environment [^>]*/>",
    "<environment groundColor='FF8FA06E' skyColor='FFB9D7F2' lightColor='FFE8DDCF' "
    "ceilingLightColor='FFFFF1DC' wallsAlpha='0' drawingMode='FILL' "
    "photoWidth='2400' photoHeight='1600' photoAspectRatio='RATIO_3_2' photoQuality='3'/>", xml)

# 2) Compass : Paris, nord en haut du plan (soleil réaliste)
compass = ("  <compass x='-150' y='620' diameter='80' northDirection='0' "
           "longitude='0.041015237' latitude='0.85259347' timeZone='Europe/Paris' visible='true'/>\n")

# 3) Walls : blanc cassé chaud des deux côtés, plafonds blancs
xml = re.sub(r"(<wall [^>]*?) pattern='hatchUp'/>",
             r"\1 pattern='hatchUp' leftSideColor='FFF2EEE7' rightSideColor='FFF2EEE7' leftSideShininess='0.05' rightSideShininess='0.05'/>", xml)
xml = re.sub(r"<room ([^>]*)ceilingVisible='true'>", r"<room \1ceilingVisible='true' ceilingColor='FFFBFAF7'>", xml)

# 4) Suspensions -> vraies lumières
def to_light(m, src):
    attrs = m.group(1)
    return f"<light {attrs} power='0.55'>\n    {src}\n  </light>"
bulbs = {
    'suspension_dipsy':     "<lightSource x='0.5' y='0.5' z='0.30' color='FFFFD9A0' diameter='0.25'/>",
    'suspension_dome_fume': "<lightSource x='0.5' y='0.5' z='0.25' color='FFFFD9A0' diameter='0.25'/>",
    'suspension_perles':    "<lightSource x='0.5' y='0.5' z='0.08' color='FFFFD9A0' diameter='0.25'/>",
}
for model, src in bulbs.items():
    xml = re.sub(r"<pieceOfFurniture ((?:(?!/>).)*model='" + model + r"/model\.obj'(?:(?!/>).)*)/>",
                 lambda m, s=src: to_light(m, s), xml)

# 5) Spots LED encastrés (modèle disque blanc) dans les pièces sans luminaire
os.makedirs(f'{WORK}/spot_led', exist_ok=True)
N = 24; v = []; f = []
for z in (0.0, 1.0):
    v.append((0.5, z, 0.5))
    for i in range(N):
        a = 2*math.pi*i/N; v.append((0.5+0.5*math.cos(a), z, 0.5+0.5*math.sin(a)))
with open(f'{WORK}/spot_led/model.obj', 'w') as o:
    o.write('mtllib model.mtl\n')
    for p in v: o.write('v %.4f %.4f %.4f\n' % p)
    o.write('usemtl diffuseur\n')
    for i in range(N):  # bottom (diffuser)
        o.write(f'f 1 {2+(i+1)%N} {2+i}\n')
    o.write('usemtl blanc\n')
    for i in range(N):  # side + top
        a, b = 2+i, 2+(i+1)%N
        o.write(f'f {a} {b} {b+N+1} {a+N+1}\n')
        o.write(f'f {N+2} {a+N+1} {b+N+1}\n')
with open(f'{WORK}/spot_led/model.mtl', 'w') as o:
    o.write('newmtl diffuseur\nKa 1 1 1\nKd 1.0 0.98 0.94\nKs 0 0 0\nNs 1\n'
            'newmtl blanc\nKa 0.2 0.2 0.2\nKd 0.95 0.95 0.95\nKs 0.2 0.2 0.2\nNs 20\n')
spots = [  # (nom, x, y, puissance)
    ('Chambre', 160, 520, 0.5), ('Chambre', 330, 520, 0.5),
    ("Salle d'eau", 600, 560, 0.45), ("Salle d'eau", 730, 590, 0.45),
    ('WC', 878, 560, 0.4),
    ('Entrée', 640, 435, 0.35),
]
spot_xml = ''
for name, x, y, p in spots:
    spot_xml += (f"  <light name='Spot LED {name.replace(chr(39), "&apos;")} (ajouté pour l&apos;éclairage)' model='spot_led/model.obj' icon='icon.png' "
                 f"x='{x}' y='{y}' elevation='247.5' width='9' depth='9' height='2.5' angle='0' movable='true' resizable='true' power='{p}'>\n"
                 f"    <lightSource x='0.5' y='0.5' z='-0.6' color='FFFFE6C4' diameter='0.6'/>\n  </light>\n")

# 6) Points de vue enregistrés par pièce (x, y, z = œil ; cible tx, ty, tz) en cm
views = [
    ('Séjour 1 – vue depuis la cuisine',     815, 268, 160, 300, 120, 95, 1.30),
    ('Séjour 2 – canapé et étagère',         575, 330, 150, 372, 60, 95, 1.15),
    ('Séjour 3 – depuis la baie vitrée',     235, 300, 160, 800, 90, 100, 1.30),
    ('Cuisine 1 – plan de travail',          640, 260, 165, 840, 70, 100, 1.20),
    ('Cuisine 2 – coin repas',               880, 250, 165, 560, 170, 75, 1.20),
    ('Entrée 1 – depuis la porte',           905, 440, 160, 560, 400, 110, 1.25),
    ('Entrée 2 – vers la porte',             560, 445, 160, 930, 420, 110, 1.15),
    ('Chambre 1 – depuis la porte',          490, 420, 160, 180, 620, 70, 1.30),
    ('Chambre 2 – lit et fenêtre',           400, 660, 155, 40, 470, 95, 1.30),
    ('Chambre 4 – reflet dans le miroir',    230, 470, 160, 71, 650, 110, 1.10),
    ('Chambre 3 – coin bureau',             330, 470, 150, 60, 420, 90, 1.20),
    ("Salle d'eau 1 – douche et vasque",     760, 505, 165, 580, 640, 90, 1.40),
    ("Salle d'eau 2 – meuble vasque",        640, 520, 160, 660, 690, 100, 1.30),
    ('WC',                                   880, 495, 165, 880, 660, 60, 1.30),
    ('Balcon',                               160, 60, 155, -60, 320, 80, 1.30),
]
def cam_xml(attr, name, x, y, z, tx, ty, tz, fov):
    dx, dy = tx-x, ty-y
    yaw = math.atan2(-dx, dy)
    pitch = math.atan2(z-tz, math.hypot(dx, dy))
    n = f" name='{name.replace(chr(39), '&apos;')}'" if name else ''
    return (f"  <camera attribute='{attr}'{n} lens='PINHOLE' x='{x}' y='{y}' z='{z}' "
            f"yaw='{yaw:.6f}' pitch='{pitch:.6f}' fieldOfView='{fov}' time='{TIME}'/>\n")
stored = ''.join(cam_xml('storedCameras', *v_) for v_ in views)

# observer camera = first view, home opens in virtual-visit mode
first = views[0]
obs = cam_xml('observerCamera', None, *first[1:]).replace('<camera ', '<observerCamera ').strip()
xml = re.sub(r"<observerCamera [^>]*/>", obs, xml)
xml = xml.replace("camera='topCamera'", "camera='observerCamera'")
xml = re.sub(r"(<camera attribute='topCamera'[^>]*time=')\d+'", r"\g<1>" + TIME + "'", xml)
xml = xml.replace('</home>', compass + spot_xml + stored + '</home>')

open(f'{WORK}/Home.xml', 'w', encoding='utf-8').write(xml)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as z:
    z.write(f'{WORK}/Home.xml', 'Home.xml')  # Home.xml first
    for root, _, files in os.walk(WORK):
        for fn in sorted(files):
            p = os.path.join(root, fn); rel = os.path.relpath(p, WORK)
            if rel != 'Home.xml': z.write(p, rel)
print('written', OUT, os.path.getsize(OUT))
