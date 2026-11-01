# Visite 360° – Appartement de Ugo et Elsa

Site statique publié avec GitHub Pages depuis la branche `main`, à la racine :
**https://lucas13032007.github.io/appartement-ugo-elsa/**

Le propriétaire (Ugo) parle français : répondre en français, simplement, sans jargon.
Tout push sur `main` met le site à jour en 1–2 minutes.

---

## Ce qui a été fait (historique)

1. **Point de départ** : un plan Sweet Home 3D de l'appartement (`source/Appartement-303_original.sh3d`).
2. **Amélioration du fichier Sweet Home 3D** (`source/Appartement-303_eclairage-HD.sh3d`) :
   lumières, miroirs, parquet chêne clair, et de nombreux meubles remodélisés d'après les références réelles
   (canapé OMHU Teddy émeraude, chaises Sklum Jolie, table IKEA SKÄLSTA, cuisine Cuisinella finition « Venus »,
   four Rosières, plaque EssentielB, lave-vaisselle Beko, lave-linge Bosch, frigo LISTO, suspension Sklum Bezany,
   bureau IKEA LAGKAPTEN/ALEX, chaise IKEA LOBERGET, chevets Kartell Componibili verts, arbre à chat Leeby,
   poubelle SONGMICS, vidéoprojecteur XGIMI, console, etc.). Portes SDE/WC, litière, peluche, objets d'étagère retirés.
3. **Scène Blender** (`source/Appartement-303.blend`) reconstruite à partir du fichier Sweet Home 3D :
   lumière réaliste (soleil, ciel, suspensions, spots, LED sous meubles), environnement extérieur depuis le balcon,
   15 caméras. Corrections de nombreuses « bandes noires » (faces superposées entre murs, haut de placard, cadres d'affiches).
4. **7 vues 360°** rendues avec Blender Cycles (2560×1280) + une **vue du dessus** orthographique (`plan_top.jpg`).
5. **Site de visite** (`index.html`) : visionneuse Pannellum intégrée, design façon Google Maps.

## Fichiers

| Fichier | Rôle |
|---|---|
| `index.html` | Toute la page (HTML + CSS + JS + Pannellum 2.5.7 intégré en ligne). **C'est la référence** : le modifier directement. `source/scripts/gen_tour_maps.py` l'a généré à l'origine et reçoit les mêmes modifications, mais il contient encore d'anciens morceaux (ex. `badge`, `rate`) : ne pas écraser `index.html` avec sa sortie sans comparer. |
| `sejour.jpg`, `repas.jpg`, `entree.jpg`, `chambre.jpg`, `sde.jpg`, `wc.jpg`, `balcon.jpg` | Vues 360° équirectangulaires. Doivent rester **à la racine** (l'upload de dossiers via le web GitHub ne marchait pas). |
| `plan_top.jpg` | Vue du dessus utilisée par le mini-plan (image placée en `x=-90 y=3 1040×704`, unités = cm du plan ; viewBox `-74 15 1007 680`, découpée à la forme de l'appartement par le clipPath `pshape`). |
| `source/Appartement-303.blend` | Scène Blender complète (Blender 5.2, textures empaquetées). |
| `source/*.sh3d` | Fichiers Sweet Home 3D (original et amélioré). |
| `source/scripts/` | Scripts Python Blender (`bpy`) qui ont tout produit — chemins absolus `/home/claude/...` à adapter. |
| `source/pannellum/` | Viewer 360 (js/css) inliné dans `index.html`. |

### Coordonnées
Plan Sweet Home 3D en cm, x vers la droite, y vers le bas (le « nord » du site = haut du plan).
Points de vue des pièces (x, y, hauteur des yeux 155 cm) :
séjour (420,220) · cuisine/repas (700,180) · entrée (870,430) · chambre (385,460) · salle d'eau (720,560) · WC (878,560, h150) · balcon (60,190).
Dans Blender : X = x/100, Y = −y/100, Z = z/100 (mètres).

## Interface actuelle (préférences d'Ugo — à respecter)
- DA : coins arrondis, ombres douces, police Google Sans / Roboto. **Tout ce qui flotte sur la vue** (barre, étiquettes, ronds de passage, messages) est en **verre sombre semi-transparent** à texte blanc ; la fiche infos reste blanche pour la lecture.
- **Barre de commandes** verticale en bas à droite : boussole, carte, ⓘ. Nom de la pièce = petite étiquette à part, en bas à gauche.
- Interface **minimale** : pas de titre, pas de barre de boutons en haut, pas de système de note (refusé).
- Passages entre pièces : **petit rond sombre + flèche blanche + nom en petit**. Pas plus grands au repos (léger grossissement au survol de la souris seulement), pas d'animation qui clignote.
- **Aide aux passages** : si aucun rond n'est dans le champ, une pastille en bas au centre (« ‹ Entrée ») tourne la vue vers le plus proche.
- Pas de ligne bleue au sol (essayée puis abandonnée : elle passe sur les meubles).
- **Liens entre pièces** : l'entrée et le séjour se relient directement ; le séjour mène aussi à la chambre et à la salle d'eau.
- **Boussole** façon Waze : petite flèche rouge qui tourne avec la vue, sans lettres. Clic = retour au nord, et seulement alors triangle rouge + N. Nouveau clic sur le N = retour à l'angle précédent.
- **Provenance des produits** : toutes petites étiquettes (`PRODUCTS` dans `index.html`) visibles seulement quand on regarde vers le produit. Les marques données par Ugo le 2026-11-01 priment sur les références de l'historique ci-dessus (ex. arbre à chat Animalis, luminaire du séjour Leroy Merlin, chevets Sklum).
- **Mobile d'abord** : penser et tester l'interface sur iPhone en premier.
- **Démarrage** : la visite commence à l'entrée, carte fermée. Message d'accueil = pastille blanche en haut, qui disparaît au premier toucher.
- **Mini-plan fermé par défaut**, ouvert par le bouton carte à gauche de la barre : vraie vue du dessus découpée à la forme de l'appartement sur fond gris clair, cadre en verre sombre, **point bleu + cône de vue** ; clic sur une pièce pour y aller.
- **Transitions** : la vue tourne vers la porte + léger zoom puis fondu ; aucun écran de chargement (toutes les vues préchargées).
- **Arrivée dans une pièce** : toujours face à son sujet, jamais devant un mur (angle fixe par pièce, champ `yaw` de chaque scène).
- **Aucune bande noire** ni artefact sur les images : Ugo y est très attentif.
- Pas de mention de Claude sur le site.

## Fiche infos (bouton ⓘ)
Appartement T2 · **18 rue des Folies, 35700 Rennes** · 48,4 m² habitables · balcon 7,3 m² exposé ouest (soleil du soir) ·
3e étage avec ascenseur · construction 2026 (neuf) · chauffage électrique, radiateurs (Ugo a aussi dit « collectif » — à confirmer) ·
**DPE B** (GES inconnu) · place de parking n° 46 · local / box à vélos · location (le statut n'est volontairement pas affiché).
Bouton « Voir sur la carte de Rennes » → Google Maps (une carte intégrée n'était pas possible sur l'ancien hébergement ; sur GitHub Pages
un iframe Google Maps / OpenStreetMap est maintenant faisable).

## Prochaine étape prévue
**Améliorer l'UX/UI du site** selon les retours d'Ugo (il donnera les consignes au fur et à mesure, souvent avec des captures d'écran iPhone).
Tester d'abord sur mobile (iPhone, viewport ~390×844), puis sur ordinateur.
Ugo veut que les changements demandés soient publiés directement, sans lui faire déposer de fichiers.

## Refaire des images (si un meuble change)
- `pip install bpy` (Blender 5.x en module Python) fonctionne dans l'environnement cloud.
- Les rendus se font avec `source/scripts/render.py` (options JSON : `pano`, `ortho`, `cam`, `samples`, `res`, `exposure`, `hide`, …)
  sur une scène construite par `source/scripts/build.py` à partir du dossier Sweet Home 3D décompressé.
- Plus simple : ouvrir `source/Appartement-303.blend`, régler une caméra en panoramique équirectangulaire à la position de la pièce, rendre en Cycles.
- Compter ~6 min par vue 360° sur 2 CPU.
