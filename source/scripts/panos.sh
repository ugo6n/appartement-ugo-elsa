#!/bin/bash
cd /home/claude
C='"samples":28,"res":[3072,1536],"sun_az":192,"sun_el":12,"sun":4,"win":300,"exposure":0.6,"bulb":40'
render() { python3 scripts/render.py -- "{\"pano\":true,\"cam\":[$2,$3,$4],\"target\":[0,0,0],$C,\"out\":\"/home/claude/out/pano/$1.jpg\"}" > /tmp/pano_$1.log 2>&1; echo "$(date +%H:%M) $1 done" >> /home/claude/out/pano/progress.txt; }
render sejour 420 220 155
render repas 700 180 155
render entree 870 430 155
render chambre 385 460 155
render sde 720 560 155
render wc 878 560 150
render balcon 60 190 155
echo ALLDONE >> /home/claude/out/pano/progress.txt
