# Visite 360° – Appartement de Ugo et Elsa

Site statique publié avec GitHub Pages : https://lucas13032007.github.io/appartement-ugo-elsa/

## Contenu
- `index.html` : toute la page (HTML + CSS + JS, visionneuse Pannellum 2.5.7 intégrée).
- `sejour.jpg`, `repas.jpg`, `entree.jpg`, `chambre.jpg`, `sde.jpg`, `wc.jpg`, `balcon.jpg` : vues 360° équirectangulaires (2560×1280), rendues avec Blender Cycles.
- `plan_top.jpg` : vue du dessus de l'appartement (mini-plan en bas à droite).
- Tous les fichiers sont à la racine (pas de sous-dossier) : c'est volontaire.

## Interface (préférences d'Ugo)
- Direction artistique façon Google Maps : blanc, coins arrondis, ombres douces, police Google Sans / Roboto.
- Interface minimale : pas de barre de titre, pas de boutons de pièces en haut, pas de note.
- Points de passage entre pièces : petit rond blanc avec flèche bleue + nom en petit (ne pas les grossir).
- Boussole Google Maps (N rouge, E, S, O) au-dessus du mini-plan ; le nord = haut du plan.
- Mini-plan = vue du dessus avec point bleu + cône de vue ; clic sur une pièce pour y aller ; bouton ⓘ ouvre la fiche.
- Transitions : la vue tourne vers la porte, zoom léger, fondu ; aucune image de chargement visible.
- Zéro bande noire / artefact sur les images.

## Fiche infos (bouton ⓘ)
18 rue des Folies, 35700 Rennes · T2 · 48,4 m² · balcon 7,3 m² exposé ouest (soleil du soir) ·
3e étage avec ascenseur · construction 2026 · chauffage électrique, radiateurs · DPE B (GES inconnu) ·
place de parking n° 46 · local à vélos. Bouton « Voir sur la carte de Rennes » → Google Maps.

## Limites
Les vues 360° et la vue du dessus viennent d'une scène Blender (fichier `Appartement-303.blend`, hors dépôt).
Changer un meuble demande de refaire le rendu dans Blender puis de remplacer le `.jpg` concerné.
