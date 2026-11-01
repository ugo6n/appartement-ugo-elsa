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
for a, b, yaw, pitch in [('entree', 'repas', -59, -10), ('entree', 'sejour', -74, -14.1), ('repas', 'entree', 176, -14)]:
    h = next(h for h in scenes[a]['hotSpots'] if h['createTooltipArgs'] == b)
    h.update(yaw=yaw, pitch=pitch); h['clickHandlerArgs'].update(yaw=yaw, pitch=pitch)
scenes['sejour']['hotSpots'].append(dict(hs('sejour', 'sde', (743, 486)), pitch=4))
scenes['sejour']['hotSpots'].append(hs('sejour', 'chambre', (512, 436)))
cfg = json.dumps({'default': {'firstScene': 'entree', 'sceneFadeDuration': 700, 'autoLoad': True, 'showControls': False,
                              'hfov': 100, 'minHfov': 45, 'maxHfov': 120, 'friction': 0.12}, 'scenes': scenes}, ensure_ascii=False)
cfg = cfg.replace('"@@HS@@"', 'makeHotspot').replace('"@@WALK@@"', 'walkTo').replace('"firstScene": "entree"', '"firstScene": START')
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
<meta name="theme-color" content="#e8e2d6">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<title>Appartement de Ugo et Elsa</title>
<link rel="apple-touch-icon" sizes="180x180" href="icone.png">
<link rel="icon" type="image/png" href="favicon.png">
<meta name="apple-mobile-web-app-title" content="Appartement">
<meta property="og:type" content="website">
<meta property="og:title" content="Appartement de Ugo et Elsa">
<meta property="og:image" content="https://ugo6n.github.io/appartement-ugo-elsa/apercu.jpg?v=2">
<meta property="og:image:secure_url" content="https://ugo6n.github.io/appartement-ugo-elsa/apercu.jpg?v=2">
<meta property="og:image:type" content="image/jpeg">
<meta property="og:image:alt" content="La cuisine et la table de l'appartement">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="https://ugo6n.github.io/appartement-ugo-elsa/apercu.jpg?v=2">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
<style>''' + css + r'''.hs .wrap{animation:hsIn .35s ease-out .25s backwards;transition:opacity .18s}
.moving .hs .wrap{opacity:0}
.hs .wrap:active .ic{transform:scale(.92)}
@keyframes hsIn{from{opacity:0;transform:translate(-50%,-50%) scale(.82)}to{opacity:1;transform:translate(-50%,-50%) scale(1)}}
.plan{transform-origin:100% 100%;transition:opacity .22s ease,transform .26s cubic-bezier(.2,.8,.2,1),visibility .22s}
.rail button svg{transition:transform .15s}
.rail .psound .ic-on,.rail .psound[aria-pressed="true"] .ic-off{display:none}
.rail .psound[aria-pressed="true"] .ic-on{display:block}
.rail .psound:active svg,.rail .pmap:active svg,.rail .ptags:active svg,.rail .pshare:active svg,.rail .pinfo:active svg{transform:scale(.88)}
.compass.north .n-state{animation:nIn .22s ease-out}
@keyframes nIn{from{opacity:0;transform:scale(.7)}to{opacity:1;transform:scale(1)}}
.guide{animation:guideIn .24s ease-out;transition:opacity .15s,background .15s}
.moving .guide{opacity:0}
@keyframes guideIn{from{opacity:0;transform:translateX(-50%) translateY(8px)}to{opacity:1;transform:translateX(-50%) translateY(0)}}
.toast{animation:toastIn .3s ease-out .3s backwards}
@keyframes toastIn{from{opacity:0;transform:translateX(-50%) translateY(-8px)}to{opacity:1;transform:translateX(-50%) translateY(0)}}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
</style>
<style>
:root{--font:"Google Sans","Product Sans",Roboto,-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif;
  --ink:#1f1f1f;--ink2:#444746;--muted:#5f6368;--blue:#0b57d0;--teal:#0e6b75;--chip-sh:0 1px 3px rgba(60,64,67,.3),0 4px 8px 3px rgba(60,64,67,.15);
  --sh:0 1px 2px rgba(60,64,67,.3),0 2px 6px 2px rgba(60,64,67,.15)}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html,body{margin:0;height:100%;background:#e8e2d6;font-family:var(--font);color:var(--ink);overflow:hidden;-webkit-font-smoothing:antialiased}
#pano{position:absolute;top:0;left:0;width:100%;height:100vh;height:100lvh}
@media (hover:none){html,body{overflow:visible;overscroll-behavior:none;touch-action:none}body{height:calc(100vh + 200px);height:calc(100lvh + 200px)}#pano{height:calc(100vh + 200px);height:calc(100lvh + 200px)}.info{touch-action:pan-y}}
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

.rail{position:fixed;right:12px;bottom:calc(16px + env(safe-area-inset-bottom));z-index:9;display:flex;flex-direction:column;gap:8px;width:44px}
.rail button{position:relative;flex:none;width:44px;height:44px;padding:0;border:0;border-radius:50%;box-shadow:0 2px 10px rgba(0,0,0,.25);display:flex;align-items:center;justify-content:center;cursor:pointer;transition:opacity .2s,transform .24s cubic-bezier(.2,.8,.2,1),visibility .24s,filter .15s}
.rail .compass{background:#ea4335}.rail .pmap{background:#1a73e8}.rail .ptags{background:#f59e0b}.rail .psound{background:#8b5cf6}.rail .pshare{background:#16a34a}.rail .pinfo{background:#ec4899}
.rail .pburger{display:none;background:var(--glass);-webkit-backdrop-filter:blur(14px) saturate(140%);backdrop-filter:blur(14px) saturate(140%)}
.pburger .ic-close,.rail.open .pburger .ic-menu{display:none}
.rail.open .pburger .ic-close{display:block}
.rail button:hover{filter:brightness(1.08)}
.rail button:active{filter:brightness(.9)}
.rail .pmap[aria-expanded="true"],.rail .ptags[aria-pressed="true"],.rail .psound[aria-pressed="true"]{box-shadow:inset 0 0 0 2.5px #fff,0 2px 10px rgba(0,0,0,.25)}
@media (max-width:600px),(hover:none){
  .rail .pburger{display:flex}
  .rail:not(.open) button:not(.pburger){visibility:hidden;opacity:0;transform:translateY(24px) scale(.7);pointer-events:none}
  .rail.open button:nth-child(5){transition-delay:.03s}.rail.open button:nth-child(4){transition-delay:.06s}.rail.open button:nth-child(3){transition-delay:.09s}.rail.open button:nth-child(2){transition-delay:.12s}.rail.open button:nth-child(1){transition-delay:.15s}
}
.rail button svg{display:block;width:20px;height:20px;fill:none;stroke:#fff;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
.rail .pinfo svg{stroke-width:2.6}
.rail .compass #dial{width:26px;height:26px}
.rail .compass .n-state{width:32px;height:32px}
.compass .n-state{display:none}
.compass.north #dial{display:none}
.compass.north .n-state{display:block}
:root{--planh:130px;--glass:rgba(32,33,36,.62)}
/* mini plan card (top view) */
.plan{position:fixed;right:64px;bottom:calc(16px + env(safe-area-inset-bottom));z-index:9;border-radius:16px;background:var(--glass);-webkit-backdrop-filter:blur(14px) saturate(140%);backdrop-filter:blur(14px) saturate(140%);box-shadow:0 2px 10px rgba(0,0,0,.25);
  padding:6px;width:min(360px,calc(100vw - 88px))}
.pframe{box-sizing:border-box;padding:8px;background:#f1f3f4;border-radius:11px}
.plan .pline{fill:none;stroke:#bdc1c6;stroke-width:3;stroke-linejoin:round;pointer-events:none}
.plan svg{display:block;width:100%;height:auto}
.plan .zone{fill:transparent;cursor:pointer}
.plan .zone:hover{fill:rgba(26,115,232,.10)}
.plan .halo{fill:url(#coneg);pointer-events:none}
.plan .me{fill:#1a73e8;stroke:#fff;stroke-width:7;pointer-events:none}
.plan .me-ring{fill:rgba(26,115,232,.2);pointer-events:none}
.guide{position:fixed;left:50%;bottom:calc(16px + env(safe-area-inset-bottom));transform:translateX(-50%);z-index:9;display:flex;align-items:center;gap:4px;height:36px;padding:0 14px 0 8px;border:0;border-radius:18px;color:#fff;font:500 13px var(--font);white-space:nowrap;cursor:pointer;background:var(--glass);-webkit-backdrop-filter:blur(14px) saturate(140%);backdrop-filter:blur(14px) saturate(140%);box-shadow:0 2px 10px rgba(0,0,0,.25)}
.guide[hidden],.plan:not(.closed)~.guide{display:none}
.guide.right{flex-direction:row-reverse;padding:0 8px 0 14px}
.guide svg{width:18px;height:18px;fill:none;stroke:#fff;stroke-width:2.4;stroke-linecap:round;stroke-linejoin:round}
.guide.right svg{transform:rotate(180deg)}
.guide:active{background:rgba(32,33,36,.82)}
@media (max-width:600px){.plan{width:min(260px,calc(100vw - 88px))}.pframe{padding:6px}}
.plan.closed{visibility:hidden;opacity:0;transform:translateY(10px) scale(.96);pointer-events:none}
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
.info h2{margin:0;font-size:24px;font-weight:500;color:var(--ink)}
.isub{margin-top:4px;font-size:14px;color:var(--muted)}
.close{width:40px;height:40px;border-radius:50%;border:0;background:#f1f3f4;display:flex;align-items:center;justify-content:center;cursor:pointer;flex:none}
.close svg{width:20px;height:20px;fill:none;stroke:#444746;stroke-width:2;stroke-linecap:round}
.addr{display:flex;gap:14px;align-items:flex-start;margin-top:18px;padding:14px 0;border-top:1px solid #e3e3e3;border-bottom:1px solid #e3e3e3;font-size:15px;color:var(--ink);line-height:1.4}
.addr svg{width:24px;height:24px;flex:none}
.addr b{font-weight:500}
.mapbtn{display:flex;align-items:center;justify-content:center;gap:8px;height:44px;margin:14px 0 2px;border-radius:22px;background:#1a73e8;color:#fff;text-decoration:none;font-size:15px;font-weight:500}
.mapbtn svg{width:20px;height:20px;fill:none;stroke:#fff;stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round}
.chip.map{color:#0b57d0;text-decoration:none}.chip.map svg{stroke:#0b57d0}
.dpe{padding:16px 0;border-bottom:1px solid #e3e3e3}
.dpe-t{font-size:13px;color:var(--muted);margin-bottom:10px}
.dpe-scale{display:flex;gap:4px}
.dpe-scale span{flex:1;height:30px;border-radius:6px;display:flex;align-items:center;justify-content:center;color:#1f1f1f;font-weight:700;font-size:14px;opacity:.38}
.dpe-scale span.on{color:#fff;opacity:1;transform:scaleY(1.22);box-shadow:0 2px 6px rgba(0,0,0,.25)}
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
.pr{width:0;height:0;pointer-events:none}
.pr .tag{position:absolute;transform:translate(-50%,-50%);padding:2px 7px;border-radius:9px;background:rgba(32,33,36,.5);font:500 10.5px var(--font);color:#fff;white-space:nowrap;opacity:0;transition:opacity .25s}
.pr .tag.on{opacity:.9}
.no-tags .pr .tag{display:none}
.hs{width:0;height:0}
.hs .wrap{position:absolute;transform:translate(-50%,-50%);display:flex;flex-direction:column;align-items:center;gap:4px;cursor:pointer}
.hs .wrap .ic{width:34px;height:34px;border-radius:50%;background:rgba(32,33,36,.72);box-shadow:0 2px 8px rgba(0,0,0,.25);display:flex;align-items:center;justify-content:center;transition:transform .15s ease-out}
.hs .wrap .ic svg{width:18px;height:18px}
@media (hover:hover){.hs .wrap:hover .ic{transform:scale(1.18)}}
.hs .wrap .lb{padding:1px 7px;border-radius:9px;background:rgba(32,33,36,.55);font:500 11px var(--font);color:#fff;white-space:nowrap}
.hs .wrap:active .ic{background:rgba(32,33,36,.92)}
.toast{position:fixed;left:50%;top:calc(16px + env(safe-area-inset-top));transform:translateX(-50%);z-index:13;display:flex;align-items:center;gap:8px;height:36px;padding:0 14px 0 10px;color:#fff;border-radius:18px;font-size:13px;font-weight:500;white-space:nowrap;
  background:var(--glass);-webkit-backdrop-filter:blur(14px) saturate(140%);backdrop-filter:blur(14px) saturate(140%);box-shadow:0 2px 10px rgba(0,0,0,.25);transition:opacity .4s;pointer-events:none}
.toast svg{width:20px;height:20px;flex:none;fill:none;stroke:#8ab4f8;stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round}

</style></head>
<body class="no-tags">
<div id="pano"></div>

<div class="top">
  <div class="chips" id="chips" hidden></div>
</div>


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
</div>
<button class="guide" id="guide" type="button" hidden aria-label="Tourner vers le passage le plus proche"><svg viewBox="0 0 24 24"><path d="m15 6-6 6 6 6"/></svg><span id="guideLabel"></span></button>
<div class="rail">
  <button class="compass" id="compass" type="button" aria-label="Boussole : revenir au nord">
  <svg viewBox="0 0 100 100" id="dial">
    <path d="M50 20 L33 76 L50 66 Z" fill="#ffffff" stroke="#ffffff" stroke-width="3" stroke-linejoin="round"/><path d="M50 20 L67 76 L50 66 Z" fill="#ffd2cd" stroke="#ffd2cd" stroke-width="3" stroke-linejoin="round"/>
  </svg>
  <svg viewBox="0 0 100 100" class="n-state">
    <path d="M50 14 L63 40 H37 Z" fill="#fff" stroke="none"/>
    <text x="50" y="64" font-family="Google Sans, Roboto, Arial" font-weight="700" font-size="30" text-anchor="middle" dominant-baseline="central" fill="#fff" stroke="none">N</text>
  </svg>
</button>
  <button class="pmap" id="mapBtn" type="button" aria-label="Afficher la carte" title="Afficher la carte" aria-expanded="false"><svg viewBox="0 0 24 24"><path d="M9 4 3 6v14l6-2 6 2 6-2V4l-6 2-6-2z"/><path d="M9 4v14M15 6v14"/></svg></button>
  <button class="ptags" id="tagsBtn" type="button" aria-label="Afficher les noms des produits" title="Afficher les noms des produits" aria-pressed="false"><svg viewBox="0 0 24 24"><path d="M12 3H4v8l9.3 9.3a1.5 1.5 0 0 0 2.1 0l5.9-5.9a1.5 1.5 0 0 0 0-2.1L12 3z"/><circle cx="8" cy="7.5" r="1.3" fill="#fff" stroke="none"/></svg></button>
  <button class="psound" id="soundBtn" type="button" aria-label="Activer le son" title="Activer le son" aria-pressed="false"><svg class="ic-off" viewBox="0 0 24 24"><path d="M4 9.5v5h3.5L12 18.5v-13L7.5 9.5H4z"/><path d="m16 9.5 5 5M21 9.5l-5 5"/></svg><svg class="ic-on" viewBox="0 0 24 24"><path d="M4 9.5v5h3.5L12 18.5v-13L7.5 9.5H4z"/><path d="M15.5 9a4.2 4.2 0 0 1 0 6M18 6.5a7.8 7.8 0 0 1 0 11"/></svg></button>
  <button class="pshare" id="shareBtn" type="button" aria-label="Partager cette vue" title="Partager cette vue"><svg viewBox="0 0 24 24"><path d="M12 15V3M7.5 7.5 12 3l4.5 4.5"/><path d="M5 11v8a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-8"/></svg></button>
  <button class="pinfo" id="infoBtn" type="button" aria-label="Informations"><svg viewBox="0 0 24 24"><circle cx="12" cy="5.5" r="2" fill="#fff" stroke="none"/><path d="M12 11v8"/></svg></button>
  <button class="pburger" id="menuBtn" type="button" aria-label="Ouvrir le menu" title="Ouvrir le menu" aria-expanded="false"><svg class="ic-menu" viewBox="0 0 24 24"><path d="M4 7h16M4 12h16M4 17h16"/></svg><svg class="ic-close" viewBox="0 0 24 24"><path d="M6 6l12 12M18 6 6 18"/></svg></button>
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
  <a class="mapbtn" href="https://www.google.com/maps/search/?api=1&amp;query=18+rue+des+Folies+35700+Rennes" target="_blank" rel="noopener"><svg viewBox="0 0 24 24"><path d="M9 4 3 6v14l6-2 6 2 6-2V4l-6 2-6-2z"/><path d="M9 4v14M15 6v14"/></svg>Ouvrir sur Google Maps</a>
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
    <li><svg viewBox="0 0 24 24"><rect x="4" y="3" width="16" height="18" rx="3"/><path d="M9 17V7h4a3 3 0 0 1 0 6H9"/></svg><div><span>Stationnement</span><b>Place de parking</b></div></li>
    <li><svg viewBox="0 0 24 24"><circle cx="6" cy="16" r="3.5"/><circle cx="18" cy="16" r="3.5"/><path d="M6 16l4-7h5l3 7M9 9h3"/></svg><div><span>Vélos</span><b>Local / box à vélos</b></div></li>
  </ul>
</aside>

<div class="toast" id="toast"><svg viewBox="0 0 24 24"><path d="M3 12h18M8 7l-5 5 5 5M16 7l5 5-5 5"/></svg>Faites glisser pour regarder autour</div>

<script>''' + js + r'''</script>
<script>
var NAMES = ''' + names + r''', XY = ''' + coords + r''', ICONS = ''' + icj + r''';
var ORDER = Object.keys(NAMES);
function icon(k, color) { return '<svg viewBox="0 0 24 24" fill="none" stroke="' + (color || 'currentColor') + '" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">' + ICONS[k] + '</svg>'; }
var ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M12 19V5"/><path d="m5 12 7-7 7 7"/></svg>';
var busy = false;
var arriving = false;
function enterRoom(k) { arriving = true; document.body.classList.add('moving'); playWhoosh(); viewer.loadScene(k, undefined, undefined, 84); }
function walkTo(ev, a) {
  if (busy) return; busy = true; document.body.classList.add('moving'); playClick();
  viewer.lookAt(Math.max(a.pitch * 0.4, -6), a.yaw, 62, 650, function () {
    enterRoom(a.k);
    setTimeout(function () { busy = false; }, 1100);
  });
}
// preload every panorama so switching rooms never shows a loading screen
['sejour','repas','entree','chambre','sde','wc','balcon'].forEach(function (k) { var im = new Image(); im.src = k + '.jpg'; });
function makeHotspot(div, k) {
  var w = document.createElement('div'); w.className = 'wrap';
  w.innerHTML = '<span class="ic">' + ARROW + '</span><span class="lb"></span>';
  w.lastChild.textContent = NAMES[k]; div.appendChild(w);
}
var hp = (location.hash || '').slice(1).split('@'), hv = (hp[1] || '').split(',').map(Number), hasView = hv.length === 2 && !isNaN(hv[0]) && !isNaN(hv[1]);
var START = /^(sejour|repas|entree|chambre|sde|wc|balcon)$/.test(hp[0]) ? hp[0] : 'entree';
var viewer = pannellum.viewer('pano', ''' + cfg + r''');
function go(k) { if (viewer.getScene() !== k) enterRoom(k); }

// chips
var chips = document.getElementById('chips');
document.getElementById('infoBtn').onclick = function (e) { e.stopPropagation(); openInfo(); };
document.getElementById('mapBtn').onclick = function (e) { e.stopPropagation(); var closed = document.getElementById('plan').classList.toggle('closed'), t = closed ? 'Afficher la carte' : 'Masquer la carte'; this.setAttribute('aria-expanded', String(!closed)); this.setAttribute('aria-label', t); this.title = t; layout(); };
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
  document.getElementById('coneg').setAttribute('gradientTransform', 'translate(' + p[0] + ',' + p[1] + ') scale(170)');
  try { if (location.hash !== '#' + k) history.replaceState(null, '', '#' + k); } catch (e) {}
  setTimeout(layout, 30);
}
viewer.on('scenechange', function () { setTimeout(mark, 30); });
viewer.on('load', mark);
var compassBtn = document.getElementById('compass');
var beforeNorth = null, goingNorth = false;
compassBtn.onclick = function () {
  if (beforeNorth) { compassBtn.classList.remove('north'); goingNorth = false; viewer.setYaw(beforeNorth[0], 600); viewer.setPitch(beforeNorth[1], 600); beforeNorth = null; return; }
  beforeNorth = [viewer.getYaw(), viewer.getPitch()]; goingNorth = true;
  viewer.setYaw(0, 600); viewer.setPitch(-4, 600);
};
var cone = document.getElementById('cone'), cpath = document.getElementById('dial');
// where each piece comes from: tiny labels that only appear when looking towards the product
var PRODUCTS = {
  sejour: [['Canapé OMHU', -15.4, -30], ['Meuble IKEA', -156.9, -28], ['Vidéoprojecteur XGIMI', -46.3, -8], ['Nintendo Switch', -59.7, -30], ['Arbre à chat Animalis', 21.9, -24], ['Chaises Sklum', 60.4, -34], ['Table IKEA', 78.4, -20], ['Luminaire Leroy Merlin', -67.4, 34], ['Frigo LISTO', 47.6, -14]],
  repas: [['Cuisine Cuisinella Venus', 25.7, 13], ['Lave-vaisselle Beko', -18.5, -40], ['Lave-linge Bosch', 16, -40], ['Four Rosières', 92.6, -30], ['Plaque EssentielB', 99, -16], ['Poubelle SONGMICS', 154, -40], ['Frigo LISTO', -37.3, -20], ['Luminaire Sklum', 58.6, 20]],
  entree: [['Luminaire Sklum', -83, 33]],
  chambre: [['Chevets Sklum', -164, -24], ['Affiche Leroy Merlin', -145.3, 1], ['Miroir IKEA', -120, -10], ['Bureau IKEA', -81, -18], ['Chaise IKEA', -94.6, -20]],
  sde: [['Meuble Sklum', 105, -38]]
};
// when no passage is in view, a small pill turns the view towards the nearest one
var guideBtn = document.getElementById('guide'), guideLabel = document.getElementById('guideLabel'), guideTo = null;
guideBtn.onclick = function () { if (guideTo !== null) { viewer.setYaw(guideTo, 500); viewer.setPitch(-6, 500); } };
function updateGuide() {
  var yaw = viewer.getYaw(), half = viewer.getHfov() / 2, best = null, bd = 999;
  (viewer.getConfig().hotSpots || []).forEach(function (h) {
    if (h.cssClass !== 'hs') return;
    var d = ((h.yaw - yaw + 540) % 360) - 180;
    if (Math.abs(d) < Math.abs(bd)) { bd = d; best = h; }
  });
  var show = best && Math.abs(bd) > half * .85;
  if (guideBtn.hidden === !!show) guideBtn.hidden = !show;
  if (!show) { guideTo = null; return; }
  guideTo = best.yaw; guideBtn.classList.toggle('right', bd > 0);
  var name = NAMES[best.createTooltipArgs];
  if (guideLabel.textContent !== name) guideLabel.textContent = name;
}
document.getElementById('tagsBtn').onclick = function () { var off = document.body.classList.toggle('no-tags'), t = off ? 'Afficher les noms des produits' : 'Masquer les noms des produits'; this.setAttribute('aria-pressed', String(!off)); this.setAttribute('aria-label', t); this.title = t; };
viewer.on('load', function () { document.body.classList.remove('moving'); if (arriving) { arriving = false; viewer.setHfov(100, 1100); } });
// sound design: generated in the page, off until the visitor turns it on
var audioCtx = null, soundOn = false;
function playClick() {
  if (!soundOn || !audioCtx) return;
  var t = audioCtx.currentTime, o = audioCtx.createOscillator(), g = audioCtx.createGain();
  o.type = 'sine'; o.frequency.setValueAtTime(880, t); o.frequency.exponentialRampToValueAtTime(520, t + .05);
  g.gain.setValueAtTime(.045, t); g.gain.exponentialRampToValueAtTime(.0001, t + .07);
  o.connect(g); g.connect(audioCtx.destination); o.start(t); o.stop(t + .08);
}
function playWhoosh() {
  if (!soundOn || !audioCtx) return;
  var t = audioCtx.currentTime, n = Math.floor(audioCtx.sampleRate * .8), b = audioCtx.createBuffer(1, n, audioCtx.sampleRate), d = b.getChannelData(0), i;
  for (i = 0; i < n; i++) d[i] = Math.random() * 2 - 1;
  var s = audioCtx.createBufferSource(), f = audioCtx.createBiquadFilter(), g = audioCtx.createGain();
  s.buffer = b; f.type = 'bandpass'; f.Q.value = .8;
  f.frequency.setValueAtTime(300, t); f.frequency.exponentialRampToValueAtTime(900, t + .35); f.frequency.exponentialRampToValueAtTime(300, t + .8);
  g.gain.setValueAtTime(.0001, t); g.gain.exponentialRampToValueAtTime(.05, t + .3); g.gain.exponentialRampToValueAtTime(.0001, t + .8);
  s.connect(f); f.connect(g); g.connect(audioCtx.destination); s.start(t); s.stop(t + .8);
}
var railEl = document.querySelector('.rail'), menuBtn = document.getElementById('menuBtn');
function setMenu(open) { railEl.classList.toggle('open', open); var t = open ? 'Fermer le menu' : 'Ouvrir le menu'; menuBtn.setAttribute('aria-expanded', String(open)); menuBtn.setAttribute('aria-label', t); menuBtn.title = t; }
menuBtn.onclick = function () { setMenu(!railEl.classList.contains('open')); };
document.getElementById('pano').addEventListener('pointerdown', function () { setMenu(false); }, true);
document.getElementById('infoBtn').addEventListener('click', function () { setMenu(false); });
document.querySelector('.rail').addEventListener('click', playClick, true);
document.getElementById('soundBtn').onclick = function () {
  soundOn = !soundOn;
  var t = soundOn ? 'Couper le son' : 'Activer le son';
  this.setAttribute('aria-pressed', String(soundOn)); this.setAttribute('aria-label', t); this.title = t;
  if (soundOn) {
    if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    audioCtx.resume();
    playClick();
  }
};
function makeTag(div, a) { var t = document.createElement('div'); t.className = 'tag'; t.textContent = a.label; div.appendChild(t); a.el = t; }
viewer.on('load', function addProducts() {
  viewer.off('load', addProducts);
  Object.keys(PRODUCTS).forEach(function (k) {
    PRODUCTS[k].forEach(function (p) {
      p.args = {label: p[0]};
      viewer.addHotSpot({yaw: p[1], pitch: p[2], type: 'info', cssClass: 'pr', createTooltipFunc: makeTag, createTooltipArgs: p.args}, k);
    });
  });
});
function showTags(k) {
  var yaw = viewer.getYaw(), reach = viewer.getHfov() / 5;
  (PRODUCTS[k] || []).forEach(function (p) {
    if (!p.args || !p.args.el) return;
    var d = Math.abs(((p[1] - yaw + 540) % 360) - 180);
    p.args.el.classList.toggle('on', d < reach);
  });
}
(function tick() {
  var k = viewer.getScene();
  if (XY[k]) {
    var yaw = viewer.getYaw() * Math.PI / 180, half = viewer.getHfov() * Math.PI / 360, R = 170, x = XY[k][0], y = XY[k][1];
    var a1 = yaw - half, a2 = yaw + half;
    cone.setAttribute('d', 'M' + x + ',' + y + ' L' + (x + R * Math.sin(a1)) + ',' + (y - R * Math.cos(a1)) + ' A' + R + ',' + R + ' 0 0,1 ' + (x + R * Math.sin(a2)) + ',' + (y - R * Math.cos(a2)) + ' Z');
    cpath.style.transform = 'rotate(' + (-viewer.getYaw()) + 'deg)';
    if (goingNorth) { if (Math.abs(viewer.getYaw()) < 1) { goingNorth = false; compassBtn.classList.add('north'); } }
    else if (compassBtn.classList.contains('north') && Math.abs(viewer.getYaw()) > 2) { compassBtn.classList.remove('north'); beforeNorth = null; }
    showTags(k);
    updateGuide();
  }
  requestAnimationFrame(tick);
})();
function openInfo() { document.getElementById('info').classList.add('on'); document.getElementById('scrim').classList.add('on'); document.getElementById('info').setAttribute('aria-hidden', 'false'); }
function closeInfo() { document.getElementById('info').classList.remove('on'); document.getElementById('scrim').classList.remove('on'); document.getElementById('info').setAttribute('aria-hidden', 'true'); }
document.getElementById('closeInfo').onclick = closeInfo; document.getElementById('scrim').onclick = closeInfo;
document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeInfo(); });
var var_h0 = 0;
var viewDone = false;
if (hasView) viewer.on('load', function () { if (viewDone) return; viewDone = true; viewer.setYaw(hv[0], 0); viewer.setPitch(hv[1], 0); });
window.addEventListener('hashchange', function () { var h = location.hash.slice(1).split('@')[0]; if (NAMES[h]) go(h); });
// on phones the view is 200px taller than the screen and stays scrolled by half of it, so it runs under Safari's bars
var touchOnly = window.matchMedia('(hover:none)').matches;
function holdScroll() { if (touchOnly && window.scrollY !== 100) window.scrollTo(0, 100); }
if ('scrollRestoration' in history) history.scrollRestoration = 'manual';
window.addEventListener('scroll', holdScroll);
window.addEventListener('resize', holdScroll);
holdScroll();
viewer.on('load', holdScroll);
var toast = document.getElementById('toast');
function hideToast() { toast.style.opacity = 0; }
function linkCopied() { toast.firstChild.style.display = 'none'; toast.lastChild.textContent = 'Lien copié'; toast.style.padding = '0 14px'; toast.style.opacity = 1; setTimeout(hideToast, 2000); }
document.getElementById('shareBtn').onclick = function () {
  var url = location.href.split('#')[0].split('?')[0] + '#' + viewer.getScene() + '@' + Math.round(viewer.getYaw()) + ',' + Math.round(viewer.getPitch());
  if (navigator.share) { navigator.share({title: document.title, url: url}).catch(function () {}); return; }
  if (navigator.clipboard) navigator.clipboard.writeText(url).then(linkCopied, function () { window.prompt('Copiez ce lien :', url); });
  else window.prompt('Copiez ce lien :', url);
};
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
