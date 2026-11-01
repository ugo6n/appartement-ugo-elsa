#!/bin/bash
cd /home/claude
render() {
  if [ -f /home/claude/out/pano_final/$1.jpg ]; then return; fi
  python3 scripts/render.py -- "{\"pano\":true,\"cam\":[$2,$3,$4],\"target\":[0,0,0],\"samples\":20,\"res\":[2560,1280],\"sun_az\":192,\"sun_el\":12,\"sun\":4,\"win\":300,\"bulb\":40,\"exposure\":$5,\"sde_fill\":22,\"wc_fill\":8,\"spot\":30,\"out\":\"/home/claude/out/pano_final/$1.jpg\"}" > /tmp/pano_$1.log 2>&1
  echo "$(date +%H:%M) $1 done" >> /home/claude/out/pano_final/progress.txt
}
render sejour 420 220 155 0.6
render repas 700 180 155 0.6
render entree 870 430 155 0.5
render chambre 385 460 155 0.6
render sde 720 560 155 0.0
render wc 878 560 150 -0.2
render balcon 60 190 155 -0.4
echo ALLDONE >> /home/claude/out/pano_final/progress.txt
