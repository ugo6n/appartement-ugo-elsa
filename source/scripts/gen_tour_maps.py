"""360 tour page, Google-Maps-like UI. Usage: python3 gen_tour_maps.py out.html [rating]"""
import math, json, sys
OUTF = sys.argv[1]
RATING = len(sys.argv) > 2 and sys.argv[2] == 'rating'
pts = {'sejour': (420, 220, 'Séjour'), 'repas': (700, 180, 'Cuisine'), 'entree': (870, 430, 'Entrée'),
       'chambre': (385, 460, 'Chambre'), 'sde': (720, 560, "Salle d'eau"), 'wc': (878, 560, 'WC'), 'balcon': (60, 190, 'Balcon')}
icons = {  # material-style outline icons (24px)
 'sejour': '<path d="M4 18v-6a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v6"/><path d="M2 18h20M6 10V7a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v3M6 18v2M18 18v2"/>',
 'repas': '<path d="M7 3v8M5 3v4a2 2 0 0 0 4 0V3M7 11v10"/><path d="M17 21V3c-2 1-3 3-3 6v4h3"/>',
 'entree': '<path d="M5 21V4a1 1 0 0 1 1-1h12a1 1 0 0 1 1 1v17M3 21h18"/><circle cx="15" cy="12" r="1"/>',
 'chambre': '<path d="M3 18V7M21 18v-5a3 3 0 0 0-3-3h-8v5M3 15h18M3 18h18"/><circle cx="7" cy="12" r="1.6"/>',
 'sde': '<path d="M4 12h16v3a5 5 0 0 1-5 5H9a5 5 0 0 1-5-5v-3z"/><path d="M6 12V5a2 2 0 0 1 3.5-1.3M8 20l-1 2M16 20l1 2"/>',
 'wc': '<path d="M7 3h6v7H7zM5 10h14a6 6 0 0 1-6 6h-2a6 6 0 0 1-6-6z"/><path d="M9 16l-1 5h8l-1-5"/>',
 'balcon': '<path d="M12 3a4 4 0 0 1 4 4M12 3v2"/><circle cx="12" cy="9" r="0"/><path d="M3 21h18M5 21v-7M19 21v-7M3 14h18M9 14v7M14 14v7"/><circle cx="12" cy="7" r="2.5"/>',
}
order = ['sejour', 'repas', 'entree', 'chambre', 'sde', 'wc', 'balcon']
links = [('sejour', 'repas', None), ('sejour', 'balcon', (198, 205)), ('repas', 'entree', None), ('entree', 'sejour', None),
         ('entree', 'chambre', (512, 436)), ('entree', 'sde', (743, 486)), ('entree', 'wc', (880, 486))]
EYE = 155
def hs(a, b, via):
    x0, y0, _ = pts[a]; tx, ty = via if via else pts[b][:2]
    dx, dy = tx - x0, ty - y0
    yaw = math.degrees(math.atan2(dx, -dy)); dist = math.hypot(dx, dy)
    pitch = (-8 if dist > 250 else -16) if via else -min(24, max(9, math.degrees(math.atan2(EYE - 30, dist))))
    return {'pitch': round(pitch, 1), 'yaw': round(yaw, 1), 'type': 'info',
            'cssClass': 'hs', 'createTooltipFunc': '@@HS@@', 'createTooltipArgs': b,
            'clickHandlerFunc': '@@WALK@@', 'clickHandlerArgs': {'k': b, 'yaw': round(yaw, 1), 'pitch': round(pitch, 1)}}
start_yaw = {'sejour': -30, 'repas': 28, 'entree': -78, 'chambre': -115, 'sde': -115, 'wc': 180, 'balcon': -90}
scenes = {k: {'title': pts[k][2], 'type': 'equirectangular', 'panorama': f'{k}.jpg', 'yaw': start_yaw[k],
              'pitch': -4, 'hfov': 100, 'hotSpots': []} for k in order}
for a, b, via in links:
    scenes[a]['hotSpots'].append(hs(a, b, via)); scenes[b]['hotSpots'].append(hs(b, a, via))
scenes['sejour']['hotSpots'].append(dict(hs('sejour', 'sde', (743, 486)), pitch=1))
scenes['sejour']['hotSpots'].append(hs('sejour', 'chambre', (512, 436)))
cfg = json.dumps({'default': {'firstScene': 'entree', 'sceneFadeDuration': 900, 'autoLoad': True, 'showControls': False,
                              'hfov': 100, 'minHfov': 45, 'maxHfov': 120, 'friction': 0.12}, 'scenes': scenes}, ensure_ascii=False)
cfg = cfg.replace('"@@HS@@"', 'makeHotspot').replace('"@@WALK@@"', 'walkTo')
names = json.dumps({k: pts[k][2] for k in order}, ensure_ascii=False)
coords = json.dumps({k: pts[k][:2] for k in order})
icj = json.dumps(icons)
rooms = ['217,21 923,21 923,277 710,277 710,349 923,349 923,481 516,481 516,392 512,392 512,383 217,383',
         '37,392 508,392 508,681 37,681', '516,490 826,490 826,681 516,681', '833,490 923,490 923,681 833,681',
         '-74,26 179,26 179,354 -74,354']
plan_polys = ''.join(f'<polygon points="{r}"/>' for r in rooms)
css = open('/home/claude/tour/package/build/pannellum.css').read()
js = open('/home/claude/tour/package/build/pannellum.js').read()

rating_html = r'''
    <div class="rate" id="rate">
      <div class="rate-head">
        <div class="avg"><span id="avg">–</span></div>
        <div>
          <div class="stars small" id="avgStars"></div>
          <div class="count" id="count">Aucun avis pour l'instant</div>
        </div>
      </div>
      <div class="rate-ask" id="ask">Votre note</div>
      <div class="stars big" id="myStars" role="radiogroup" aria-label="Votre note"></div>
      <div class="rate-msg" id="rateMsg"></div>
    </div>''' if RATING else ''

html = r'''<!DOCTYPE html>
<html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, viewport-fit=cover">
<title>Appartement de Ugo et Elsa · Visite 360°</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
<style>''' + css + r'''</style>
<style>
:root{--font:"Google Sans","Product Sans",Roboto,-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif;
  --ink:#1f1f1f;--ink2:#444746;--muted:#5f6368;--blue:#0b57d0;--teal:#0e6b75;--chip-sh:0 1px 3px rgba(60,64,67,.3),0 4px 8px 3px rgba(60,64,67,.15);
  --sh:0 1px 2px rgba(60,64,67,.3),0 2px 6px 2px rgba(60,64,67,.15)}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html,body{margin:0;height:100%;background:#202124;font-family:var(--font);color:var(--ink);overflow:hidden;-webkit-font-smoothing:antialiased}
#pano{position:fixed;inset:0}
.pnlm-panorama-info,.pnlm-about-msg{display:none!important}
.pnlm-load-box{display:none!important;background:#fff!important;color:var(--ink)!important;border-radius:16px;box-shadow:var(--sh);font-family:var(--font)!important}
.pnlm-load-box p{display:none}.pnlm-lbar{border-color:#dadce0!important}.pnlm-lbar-fill{background:var(--blue)!important}
button{font-family:var(--font)}
@media (min-width:900px){.chips{max-width:none!important;justify-content:center}}

/* top bar (search-box style) */
.top{position:fixed;left:0;right:0;top:0;z-index:10;padding:calc(10px + env(safe-area-inset-top)) 12px 0;pointer-events:none}
.bar{pointer-events:auto;height:56px;background:#fff;border-radius:28px;box-shadow:var(--chip-sh);display:flex;align-items:center;gap:12px;padding:0 8px 0 18px;max-width:720px;margin:0 auto}
.bar .pin{width:26px;height:26px;flex:none}
.bar .t{flex:1;min-width:0;font-size:17px;font-weight:400;color:var(--ink);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.bar .t b{font-weight:500}
.bar .badge{flex:none;display:flex;align-items:center;gap:4px;height:36px;padding:0 12px;border-radius:18px;background:#f1f3f4;font-size:14px;font-weight:500;color:var(--ink);border:0;cursor:pointer}
.bar .badge svg{width:16px;height:16px;fill:#fbbc04}
.chips{pointer-events:auto;display:flex;gap:8px;overflow-x:auto;padding:2px 2px 12px;scrollbar-width:none;max-width:720px;margin:0 auto}
.chips::-webkit-scrollbar{display:none}
.chip{flex:none;display:flex;align-items:center;gap:8px;height:40px;padding:0 16px 0 12px;background:#fff;border:0;border-radius:20px;box-shadow:var(--chip-sh);
  font-size:15px;font-weight:500;color:var(--ink2);cursor:pointer;transition:background .15s}
.chip svg{width:20px;height:20px;fill:none;stroke:currentColor;stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round}
.chip.on{background:#c2e7ff;color:#001d35}
.chip:active{background:#e8eaed}

/* right floating buttons */
.fabs{position:fixed;right:12px;z-index:9;display:flex;flex-direction:column;gap:14px;align-items:flex-end;transition:bottom .3s}
.fab{width:56px;height:56px;border-radius:16px;background:#fff;border:0;box-shadow:var(--chip-sh);display:flex;align-items:center;justify-content:center;cursor:pointer;color:var(--ink)}
.fab svg{width:26px;height:26px}
.fab.round{width:48px;height:48px;border-radius:50%}
.fab.teal{background:#c4eaf0;color:#00363d}
.fab:active{filter:brightness(.95)}
#compass svg{transition:transform .08s linear}

.compass{position:fixed;right:12px;bottom:calc(var(--planh) + 26px + env(safe-area-inset-bottom));z-index:9;width:56px;height:56px;border-radius:50%;border:0;padding:3px;background:#fff;box-shadow:var(--chip-sh);cursor:pointer}
.compass svg{width:100%;height:100%;display:block;transition:transform .06s linear}
.compass:active{transform:scale(.94)}
:root{--planh:130px}
/* mini plan card (top view) */
.plan{position:fixed;right:12px;bottom:calc(16px + env(safe-area-inset-bottom));z-index:9;background:#fff;border-radius:16px;box-shadow:var(--chip-sh);
  display:flex;flex-wrap:wrap;align-items:center;gap:6px;padding:8px;width:min(360px,calc(100vw - 24px))}
.pframe{order:1;flex:0 0 100%;box-sizing:border-box;padding:8px;background:#f1f3f4;border-radius:10px}
.plan .pline{fill:none;stroke:#bdc1c6;stroke-width:3;stroke-linejoin:round;pointer-events:none}
.plan svg{display:block;width:100%;height:auto}
.plan .zone{fill:transparent;cursor:pointer}
.plan .zone:hover{fill:rgba(26,115,232,.10)}
.plan .halo{fill:url(#coneg);pointer-events:none}
.plan .me{fill:#1a73e8;stroke:#fff;stroke-width:7;pointer-events:none}
.plan .me-ring{fill:rgba(26,115,232,.2);pointer-events:none}
.pinfo,.pmap{position:relative;flex:none;width:32px;height:32px;padding:0;border-radius:50%;border:0;background:#f1f3f4;display:flex;align-items:center;justify-content:center;cursor:pointer}
.pinfo svg,.pmap svg{width:16px;height:16px;fill:none;stroke:#0b57d0;stroke-width:2.6;stroke-linecap:round}
.pinfo::after,.pmap::after{content:"";position:absolute;inset:-6px -3px}
.pmap .ic-map{display:none;stroke-width:2;stroke-linejoin:round}
.pinfo:hover,.pmap:hover{background:#e8eaed}
.pinfo:active,.pmap:active{transform:scale(.94)}
.pgroup{display:contents}
.plabel{order:-1;margin-right:auto;height:32px;padding:0 6px;display:flex;align-items:center;font-size:14px;font-weight:500;color:var(--ink)}
@media (max-width:600px){.plan{width:min(260px,calc(100vw - 24px))}.pframe{padding:6px}.compass{width:48px;height:48px;padding:2px}}
.plan.closed{display:flex;align-items:center;gap:8px;width:auto;padding:0;background:none;box-shadow:none;overflow:visible}
.plan.closed .pframe{display:none}
.plan.closed .plabel{margin:0;height:40px;padding:0 2px 0 16px;cursor:pointer}
.plan.closed .pinfo,.plan.closed .pmap{width:40px;height:40px;background:#fff}
.plan.closed .pinfo{box-shadow:var(--chip-sh)}
.plan.closed .pgroup{display:flex;align-items:center;background:#fff;border-radius:20px;box-shadow:var(--chip-sh)}
.plan.closed .pmap{background:none}
.plan.closed .pmap .ic-hide{display:none}
.plan.closed .pmap .ic-map{display:block}
/* info chip + panel */
.chip.info{color:#0b57d0}
.chip.info svg{stroke:#0b57d0}
.scrim{position:fixed;inset:0;z-index:20;background:rgba(32,33,36,.32);opacity:0;pointer-events:none;transition:opacity .25s}
.scrim.on{opacity:1;pointer-events:auto}
.info{position:fixed;z-index:21;left:0;right:0;bottom:0;max-height:86vh;overflow-y:auto;background:#fff;border-radius:28px 28px 0 0;
  box-shadow:0 -2px 12px rgba(60,64,67,.25);padding:8px 20px calc(20px + env(safe-area-inset-bottom));transform:translateY(105%);transition:transform .32s cubic-bezier(.2,.8,.2,1)}
.info.on{transform:none}
.info .grab{width:36px;height:4px;border-radius:2px;background:#c4c7c5;margin:2px auto 14px}
.ihead{display:flex;align-items:flex-start;gap:12px}
.ihead>div{flex:1}
.info h2{margin:0;font-size:26px;font-weight:400;color:var(--ink)}
.isub{margin-top:4px;font-size:14px;color:var(--muted)}
.close{width:40px;height:40px;border-radius:50%;border:0;background:#f1f3f4;display:flex;align-items:center;justify-content:center;cursor:pointer;flex:none}
.close svg{width:20px;height:20px;fill:none;stroke:#444746;stroke-width:2;stroke-linecap:round}
.addr{display:flex;gap:14px;align-items:flex-start;margin-top:18px;padding:14px 0;border-top:1px solid #e3e3e3;border-bottom:1px solid #e3e3e3;font-size:15px;color:var(--ink);line-height:1.4}
.addr svg{width:24px;height:24px;flex:none}
.addr b{font-weight:500}
.mapbtn{display:flex;align-items:center;justify-content:center;gap:8px;height:44px;margin:14px 0 2px;border-radius:22px;background:#0b57d0;color:#fff;text-decoration:none;font-size:15px;font-weight:500}
.mapbtn svg{width:20px;height:20px;fill:none;stroke:#fff;stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round}
.chip.map{color:#0b57d0;text-decoration:none}.chip.map svg{stroke:#0b57d0}
.dpe{padding:16px 0;border-bottom:1px solid #e3e3e3}
.dpe-t{font-size:13px;color:var(--muted);margin-bottom:10px}
.dpe-scale{display:flex;gap:4px}
.dpe-scale span{flex:1;height:30px;border-radius:6px;display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:14px;opacity:.38}
.dpe-scale span.on{opacity:1;transform:scaleY(1.22);box-shadow:0 2px 6px rgba(0,0,0,.25)}
.dpe-n{margin-top:10px;font-size:14px;color:var(--ink)}
.dpe-n b{font-weight:700;color:#3d8b40}
.rows{list-style:none;margin:0;padding:6px 0 0}
.rows li{display:flex;gap:16px;align-items:flex-start;padding:12px 0;border-bottom:1px solid #f1f3f4}
.rows li:last-child{border-bottom:0}
.rows svg{width:22px;height:22px;flex:none;fill:none;stroke:#5f6368;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round;margin-top:2px}
.rows span{display:block;font-size:13px;color:var(--muted)}
.rows b{display:block;font-size:15px;font-weight:400;color:var(--ink);margin-top:1px;line-height:1.35}
@media (min-width:760px){.info{left:12px;right:auto;top:12px;bottom:12px;width:400px;max-height:none;border-radius:24px;transform:translateX(-110%)}
  .info.on{transform:none}.info .grab{display:none}}

/* hotspots : compact white dots with small label */
.hs{width:0;height:0}
.hs .wrap{position:absolute;transform:translate(-50%,-50%);display:flex;flex-direction:column;align-items:center;gap:4px;cursor:pointer}
.hs .wrap .ic{width:34px;height:34px;border-radius:50%;background:#fff;box-shadow:var(--chip-sh);display:flex;align-items:center;justify-content:center;transition:transform .15s ease-out}
.hs .wrap .ic svg{width:18px;height:18px}
@media (hover:hover){.hs .wrap:hover .ic{transform:scale(1.18)}}
.hs .wrap .lb{font:500 12px var(--font);color:#fff;text-shadow:0 1px 3px rgba(0,0,0,.7);white-space:nowrap}
.hs .wrap:active .ic{background:#e8f0fe}
.toast{position:fixed;left:50%;top:calc(16px + env(safe-area-inset-top));transform:translateX(-50%);z-index:13;display:flex;align-items:center;gap:8px;height:40px;padding:0 16px 0 12px;background:#fff;color:var(--ink);border-radius:20px;font-size:14px;font-weight:500;white-space:nowrap;
  box-shadow:var(--chip-sh);transition:opacity .4s;pointer-events:none}
.toast svg{width:20px;height:20px;flex:none;fill:none;stroke:#1a73e8;stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round}

</style></head>
<body>
<div id="pano"></div>

<div class="top">
  <div class="chips" id="chips" hidden></div>
</div>

<button class="compass" id="compass" type="button" aria-label="Boussole : revenir au nord">
  <svg viewBox="0 0 100 100" id="dial">
    <circle cx="50" cy="50" r="47" fill="#fff"/>
    <circle cx="50" cy="50" r="44" fill="none" stroke="#dadce0" stroke-width="3" pathLength="360" stroke-dasharray="1.1 13.9" stroke-dashoffset=".55"/>
    <circle cx="50" cy="50" r="43.5" fill="none" stroke="#80868b" stroke-width="4" pathLength="360" stroke-dasharray="1.8 88.2" stroke-dashoffset=".9"/>
    <path d="M50 2.5 L54 9 H46 Z" fill="#ea4335"/>
    <g font-family="Google Sans, Roboto, Arial" font-weight="600" font-size="16" text-anchor="middle" dominant-baseline="central">
      <text x="50" y="19" fill="#ea4335">N</text><text x="81" y="50" fill="#5f6368">E</text>
      <text x="50" y="81" fill="#5f6368">S</text><text x="19" y="50" fill="#5f6368">O</text></g>
    <path d="M50 28 L50 50 L44.5 50 Z" fill="#f28b82"/><path d="M50 28 L50 50 L55.5 50 Z" fill="#d93025"/>
    <path d="M50 72 L50 50 L44.5 50 Z" fill="#dadce0"/><path d="M50 72 L50 50 L55.5 50 Z" fill="#9aa0a6"/>
    <circle cx="50" cy="50" r="3" fill="#fff" stroke="#5f6368" stroke-width="1.4"/>
  </svg>
</button>

<div class="plan closed" id="plan">
  <div class="pframe"><svg viewBox="-74 15 1007 680" id="plansvg">
    <defs><radialGradient id="coneg" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#1a73e8" stop-opacity=".55"/><stop offset="1" stop-color="#1a73e8" stop-opacity="0"/></radialGradient><clipPath id="pshape"><polygon points="-74,27 178,27 178,15 933,15 933,695 27,695 27,353 -74,353"/></clipPath></defs>
    <g clip-path="url(#pshape)">
    <image href="plan_top.jpg" x="-90" y="3" width="1040" height="704" preserveAspectRatio="none"/>
    <g id="zones"></g>
    <path class="halo" id="cone" d=""/>
    <circle class="me-ring" id="meRing" r="34" cx="0" cy="0"/>
    <circle class="me" id="me" r="19" cx="0" cy="0"/>
    </g>
    <polygon class="pline" points="-74,27 178,27 178,15 933,15 933,695 27,695 27,353 -74,353"/>
  </svg></div>
  <button class="pinfo" id="infoBtn" type="button" aria-label="Informations"><svg viewBox="0 0 24 24"><circle cx="12" cy="5.5" r="2" fill="#0b57d0" stroke="none"/><path d="M12 11v8"/></svg></button>
  <div class="pgroup"><div class="plabel" id="plabel">Entrée</div><button class="pmap" id="mapBtn" type="button" aria-label="Afficher la carte" title="Afficher la carte" aria-expanded="false"><svg class="ic-hide" viewBox="0 0 24 24"><path d="m6 9 6 6 6-6"/></svg><svg class="ic-map" viewBox="0 0 24 24"><path d="M9 4 3 6v14l6-2 6 2 6-2V4l-6 2-6-2z"/><path d="M9 4v14M15 6v14"/></svg></button></div>
</div>

<div class="scrim" id="scrim"></div>
<aside class="info" id="info" aria-hidden="true">
  <div class="grab"></div>
  <div class="ihead">
    <div>
      <h2>Appartement T2</h2>
      <div class="isub">48,4 m² · 2 pièces · balcon 7,3 m² · Location</div>
    </div>
    <button class="close" id="closeInfo" type="button" aria-label="Fermer"><svg viewBox="0 0 24 24"><path d="M6 6l12 12M18 6 6 18"/></svg></button>
  </div>
  <div class="addr"><svg viewBox="0 0 24 24"><path fill="#ea4335" stroke="none" d="M12 2a7 7 0 0 0-7 7c0 5.2 7 13 7 13s7-7.8 7-13a7 7 0 0 0-7-7z"/><circle cx="12" cy="9" r="2.6" fill="#fff" stroke="none"/></svg>
    <div style="flex:1"><b>18 rue des Folies</b><br>35700 Rennes</div></div>
  <a class="mapbtn" href="https://www.google.com/maps/search/?api=1&amp;query=18+rue+des+Folies+35700+Rennes" target="_blank" rel="noopener"><svg viewBox="0 0 24 24"><path d="M9 4 3 6v14l6-2 6 2 6-2V4l-6 2-6-2z"/><path d="M9 4v14M15 6v14"/></svg>Voir sur la carte de Rennes</a>
  <div class="dpe">
    <div class="dpe-t">Diagnostic de performance énergétique</div>
    <div class="dpe-scale">
      <span style="background:#009c6d">A</span><span class="on" style="background:#52b153">B</span><span style="background:#a5cc74">C</span><span style="background:#f4e70f">D</span><span style="background:#f0b40f">E</span><span style="background:#eb8235">F</span><span style="background:#d7221f">G</span>
    </div>
    <div class="dpe-n">Classe énergie <b>B</b></div>
  </div>
  <ul class="rows">
    <li><svg viewBox="0 0 24 24"><path d="M3 3h18v18H3zM3 9h18M9 21V9"/></svg><div><span>Surface habitable</span><b>48,4 m²</b></div></li>
    <li><svg viewBox="0 0 24 24"><path d="M3 21h18M5 21v-7M19 21v-7M3 14h18M9 14v7M14 14v7"/></svg><div><span>Balcon</span><b>7,3 m² · exposé ouest, soleil du soir</b></div></li>
    <li><svg viewBox="0 0 24 24"><path d="M3 18V7M21 18v-5a3 3 0 0 0-3-3h-8v5M3 15h18M3 18h18"/></svg><div><span>Pièces</span><b>Séjour avec cuisine ouverte, 1 chambre, salle d'eau, WC séparé</b></div></li>
    <li><svg viewBox="0 0 24 24"><path d="M6 21V3h12v18M10 7h4M10 11h4M10 15h4"/></svg><div><span>Étage</span><b>3e étage avec ascenseur</b></div></li>
    <li><svg viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/></svg><div><span>Construction</span><b>2026 · neuf</b></div></li>
    <li><svg viewBox="0 0 24 24"><path d="M13 2 4 14h7l-1 8 9-12h-7z"/></svg><div><span>Chauffage</span><b>Électrique · radiateurs</b></div></li>
    <li><svg viewBox="0 0 24 24"><rect x="4" y="3" width="16" height="18" rx="3"/><path d="M9 17V7h4a3 3 0 0 1 0 6H9"/></svg><div><span>Stationnement</span><b>Place de parking n° 46</b></div></li>
    <li><svg viewBox="0 0 24 24"><circle cx="6" cy="16" r="3.5"/><circle cx="18" cy="16" r="3.5"/><path d="M6 16l4-7h5l3 7M9 9h3"/></svg><div><span>Vélos</span><b>Local / box à vélos</b></div></li>
  </ul>
</aside>

<div class="toast" id="toast"><svg viewBox="0 0 24 24"><path d="M3 12h18M8 7l-5 5 5 5M16 7l5 5-5 5"/></svg>Faites glisser pour regarder autour</div>

<script>''' + js + r'''</script>
<script>
var NAMES = ''' + names + r''', XY = ''' + coords + r''', ICONS = ''' + icj + r''';
var ORDER = Object.keys(NAMES);
function icon(k, color) { return '<svg viewBox="0 0 24 24" fill="none" stroke="' + (color || 'currentColor') + '" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">' + ICONS[k] + '</svg>'; }
var ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="#1a73e8" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 19V5"/><path d="m5 12 7-7 7 7"/></svg>';
var busy = false;
function walkTo(ev, a) {
  if (busy) return; busy = true;
  viewer.lookAt(Math.max(a.pitch * 0.4, -6), a.yaw, 58, 550, function () {
    viewer.loadScene(a.k);
    setTimeout(function () { busy = false; }, 1000);
  });
}
// preload every panorama so switching rooms never shows a loading screen
['sejour','repas','entree','chambre','sde','wc','balcon'].forEach(function (k) { var im = new Image(); im.src = k + '.jpg'; });
function makeHotspot(div, k) {
  var w = document.createElement('div'); w.className = 'wrap';
  w.innerHTML = '<span class="ic">' + ARROW + '</span><span class="lb"></span>';
  w.lastChild.textContent = NAMES[k]; div.appendChild(w);
}
var viewer = pannellum.viewer('pano', ''' + cfg + r''');
function go(k) { if (viewer.getScene() !== k) viewer.loadScene(k); }

// chips
var chips = document.getElementById('chips');
document.getElementById('infoBtn').onclick = function (e) { e.stopPropagation(); openInfo(); };
document.getElementById('mapBtn').onclick = function (e) { e.stopPropagation(); var closed = document.getElementById('plan').classList.toggle('closed'), t = closed ? 'Afficher la carte' : 'Masquer la carte'; this.setAttribute('aria-expanded', String(!closed)); this.setAttribute('aria-label', t); this.title = t; layout(); };
document.getElementById('plabel').onclick = function () { if (document.getElementById('plan').classList.contains('closed')) document.getElementById('mapBtn').click(); };
var ZONES = ["217,21 923,21 923,277 710,277 710,349 923,349 923,481 516,481 516,392 512,392 512,383 217,383", "37,392 508,392 508,681 37,681", "516,490 826,490 826,681 516,681", "833,490 923,490 923,681 833,681", "-74,26 179,26 179,354 -74,354"];
var zg = document.getElementById('zones'), NSV = 'http://www.w3.org/2000/svg', svgEl = document.getElementById('plansvg');
ZONES.forEach(function (pts) {
  var pg = document.createElementNS(NSV, 'polygon'); pg.setAttribute('points', pts); pg.setAttribute('class', 'zone');
  pg.addEventListener('click', function (ev) {
    var pt = svgEl.createSVGPoint(); pt.x = ev.clientX; pt.y = ev.clientY;
    var q = pt.matrixTransform(svgEl.getScreenCTM().inverse()), best = null, bd = 1e9;
    ORDER.forEach(function (k) { var d = Math.hypot(XY[k][0] - q.x, XY[k][1] - q.y); if (d < bd) { bd = d; best = k; } });
    if (best) go(best);
  });
  zg.appendChild(pg);
});
function layout(){ var p=document.getElementById('plan'); document.documentElement.style.setProperty('--planh', p.offsetHeight+'px'); }
window.addEventListener('resize', layout);
// room info + nav
function mark() {
  var k = viewer.getScene();
  var p = XY[k]; ['me','meRing'].forEach(function(id){ var c=document.getElementById(id); c.setAttribute('cx', p[0]); c.setAttribute('cy', p[1]); });
  document.getElementById('plabel').textContent = NAMES[k];
  document.getElementById('coneg').setAttribute('gradientTransform', 'translate(' + p[0] + ',' + p[1] + ') scale(170)');
  try { if (location.hash !== '#' + k) history.replaceState(null, '', '#' + k); } catch (e) {}
  setTimeout(layout, 30);
}
viewer.on('scenechange', function () { setTimeout(mark, 30); });
viewer.on('load', mark);
document.getElementById('compass').onclick = function () { viewer.setYaw(0, 600); viewer.setPitch(-4, 600); };
var cone = document.getElementById('cone'), cpath = document.getElementById('dial');
(function tick() {
  var k = viewer.getScene();
  if (XY[k]) {
    var yaw = viewer.getYaw() * Math.PI / 180, half = viewer.getHfov() * Math.PI / 360, R = 170, x = XY[k][0], y = XY[k][1];
    var a1 = yaw - half, a2 = yaw + half;
    cone.setAttribute('d', 'M' + x + ',' + y + ' L' + (x + R * Math.sin(a1)) + ',' + (y - R * Math.cos(a1)) + ' A' + R + ',' + R + ' 0 0,1 ' + (x + R * Math.sin(a2)) + ',' + (y - R * Math.cos(a2)) + ' Z');
    cpath.style.transform = 'rotate(' + (-viewer.getYaw()) + 'deg)';
  }
  requestAnimationFrame(tick);
})();
function openInfo() { document.getElementById('info').classList.add('on'); document.getElementById('scrim').classList.add('on'); document.getElementById('info').setAttribute('aria-hidden', 'false'); }
function closeInfo() { document.getElementById('info').classList.remove('on'); document.getElementById('scrim').classList.remove('on'); document.getElementById('info').setAttribute('aria-hidden', 'true'); }
document.getElementById('closeInfo').onclick = closeInfo; document.getElementById('scrim').onclick = closeInfo;
document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeInfo(); });
var var_h0 = 0;
var h0 = (location.hash || '').slice(1); if (NAMES[h0] && h0 !== 'entree') go(h0);
window.addEventListener('hashchange', function () { var h = location.hash.slice(1); if (NAMES[h]) go(h); });
var toast = document.getElementById('toast');
function hideToast() { toast.style.opacity = 0; }
setTimeout(hideToast, 3500);
window.addEventListener('pointerdown', hideToast, {once: true, capture: true});
setTimeout(layout, 50);
''' + (r'''
// ---------- rating (shared, one vote per signed-in person) ----------
var STAR = '<svg viewBox="0 0 24 24"><path d="M12 17.3 18.2 21l-1.6-7 5.4-4.7-7.2-.6L12 2 9.2 8.7 2 9.3l5.4 4.7L5.8 21z"/></svg>';
var avgStars = document.getElementById('avgStars'), my = document.getElementById('myStars'), msg = document.getElementById('rateMsg');
for (var i = 0; i < 5; i++) avgStars.insertAdjacentHTML('beforeend', STAR);
var mine = 0, db = null, uid = null;
for (var s = 1; s <= 5; s++) (function (s) {
  var b = document.createElement('button'); b.type = 'button'; b.setAttribute('aria-label', s + ' étoile' + (s > 1 ? 's' : ''));
  b.innerHTML = STAR; b.onclick = function () { vote(s); }; my.appendChild(b);
})(s);
function paintMine(n) { my.querySelectorAll('svg').forEach(function (g, i) { g.classList.toggle('f', i < n); }); }
function paintAvg(list) {
  var n = list.length, sum = list.reduce(function (a, b) { return a + b; }, 0), avg = n ? sum / n : 0;
  var txt = n ? avg.toFixed(1).replace('.', ',') : '–';
  document.getElementById('avg').textContent = txt; document.getElementById('badgeTxt').textContent = n ? txt : 'Noter';
  document.getElementById('count').textContent = n ? (n + ' avis') : "Aucun avis pour l'instant";
  avgStars.querySelectorAll('svg').forEach(function (g, i) { g.classList.toggle('f', i < Math.round(avg)); });
}
document.getElementById('badge').onclick = function () { collapsed = false; layout(); document.getElementById('rate').scrollIntoView({behavior: 'smooth'}); };
function vote(n) {
  if (!db || !uid) { msg.textContent = 'Connectez-vous à Claude pour noter l’appartement.'; return; }
  var prev = mine; mine = n; paintMine(n); msg.textContent = 'Enregistrement…';
  db.doc('votes/' + uid).set({stars: n, at: Date.now()}).then(function () { msg.textContent = 'Merci pour votre note !'; })
    .catch(function () { mine = prev; paintMine(prev); msg.textContent = 'Impossible d’enregistrer votre note.'; });
}
paintAvg([]);
(async function () {
  try {
    if (!window.claude || !claude.use) throw 0;
    var user = await claude.use('user'); db = await claude.use('db');
    if (!db || !user) { msg.textContent = 'Connectez-vous à Claude pour voir et donner une note.'; return; }
    uid = await user.id();
    var t = setTimeout(function () { msg.textContent = 'Les notes ne se chargent pas pour le moment.'; }, 10000);
    db.collection('votes').onSnapshot(function (snap) {
      clearTimeout(t);
      var list = []; (snap.docs || snap).forEach(function (d) { var v = (d.data ? d.data() : d).stars; if (v >= 1 && v <= 5) list.push(v);
        if ((d.id || '') === uid) { mine = v; paintMine(v); } });
      paintAvg(list);
    }, function () { clearTimeout(t); msg.textContent = 'Les notes ne sont pas disponibles.'; });
  } catch (e) { msg.textContent = 'Connectez-vous à Claude pour voir et donner une note.'; }
})();
''' if RATING else '') + r'''
</script></body></html>'''
open(OUTF, 'w').write(html)
print('ok', len(html))
