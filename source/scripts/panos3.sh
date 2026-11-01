#!/bin/bash
cd /home/claude
while pgrep -f "scripts/panos2.sh" > /dev/null; do sleep 10; done
C='"samples":20,"res":[2560,1280],"sun_az":192,"sun_el":12,"sun":4,"win":300,"exposure":0.6,"bulb":40'
render() { python3 scripts/render.py -- "{\"pano\":true,\"cam\":[$2,$3,$4],\"target\":[0,0,0],$C,\"out\":\"/home/claude/out/pano/$1.jpg\"}" > /tmp/pano_$1.log 2>&1; echo "$(date +%H:%M) $1 redone" >> /home/claude/out/pano/progress.txt; }
render sejour 420 220 155
render repas 700 180 155
render entree 870 430 155
render chambre 385 460 155
echo ALLREDONE >> /home/claude/out/pano/progress.txt
