# Tesla’s Toy Boat — Royal Blue • Mobile-friendly + D-pad/Joystick + Haptics + Lamp Beam
# HUD pinned bottom-right inside the pond.
# Run: streamlit run tesla_toy_boat_streamlit.py

import json
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Tesla’s Toy Boat", page_icon="⛵️", layout="wide")

# Sidebar tuning
st.sidebar.header("⛵️ Game Settings")
buoy_goal   = st.sidebar.slider("Buoy goal (win condition)", 5, 25, 10, 1)
buoy_count  = st.sidebar.slider("Total buoys spawned", buoy_goal, 40, max(14, buoy_goal), 1)
reeds_count = st.sidebar.slider("Reeds (hazards)", 0, 40, 18, 1)
max_speed   = st.sidebar.slider("Max boat speed (pixels/s)", 120, 360, 240, 10)
drag        = st.sidebar.slider("Water drag (higher = slows faster)", 0.2, 1.2, 0.6, 0.05)
control_mode= st.sidebar.selectbox("Control mode (mobile)", ["D-pad", "Joystick"])

cfg = dict(
    buoy_goal=int(buoy_goal),
    buoy_count=int(buoy_count),
    reeds_count=int(reeds_count),
    max_speed=float(max_speed),
    drag=float(drag),
    control=("joystick" if control_mode == "Joystick" else "dpad"),
)

HTML = r"""
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no" />
<title>Tesla’s Toy Boat</title>
<style>
  :root { --royal:#4169e1; --sea:#87cefa; --sea2:#4682b4; }
  html,body{margin:0;height:100%;background:linear-gradient(180deg,var(--sea),var(--sea2));font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif}
  .wrap{display:flex;flex-direction:column;min-height:620px}
  header{display:flex;justify-content:space-between;align-items:center;gap:.6rem;padding:.6rem 1rem;background:linear-gradient(90deg,#fff8,var(--royal) 70%,#fff8);border-bottom:2px solid #0002}
  header h1{font-size:1.15rem;margin:0;color:var(--royal)}
  .pill{font-size:.9rem;padding:.2rem .6rem;border-radius:999px;background:#00000010;border:1px solid #0002}

  #pond{border:4px solid #ffffffaa;border-radius:16px;position:relative;overflow:hidden;min-height:420px;max-width:1200px;margin:.25rem auto 6.5rem auto}
  canvas{display:block;width:100%;height:100%}
  .hint{color:#000a;text-align:center;padding:.4rem 0}

  /* HUD bottom-right inside pond */
  .hud{
    position:absolute; right:.75rem; bottom:.75rem; z-index:2;
    background:#ffffffee; border:2px solid #0002; border-radius:12px; padding:.4rem .6rem;
    display:flex; gap:.7rem; align-items:center; box-shadow:0 4px 0 #0001; font-weight:700;
    pointer-events:none;
  }
  .hud div{white-space:nowrap}

  /* Lamp ON state */
  .btn.active{
    transform:translateY(1px);
    box-shadow:0 3px 0 #0001;
    background:linear-gradient(180deg,#fff,#e8f0ff);
    border-color:#4169e1aa;
  }

  /* Control Dock */
  .dock{
    position:fixed; left:0; right:0; bottom:0;
    display:flex; justify-content:space-between; align-items:center;
    gap:.75rem; padding:.75rem 1rem; background:linear-gradient(180deg, #ffffffcc, #ffffffee);
    border-top:2px solid #0002; backdrop-filter:saturate(1.1) blur(6px);
  }
  .btn{
    display:flex; align-items:center; justify-content:center;
    width:64px; height:64px; border-radius:16px; font-weight:800; font-size:22px;
    border:2px solid #0003; background:linear-gradient(180deg,#fff,#f0f5ff); color:var(--royal);
    box-shadow:0 4px 0 #0001; touch-action:none; user-select:none; -webkit-user-select:none;
  }
  .btn:active{ transform:translateY(1px); box-shadow:0 3px 0 #0001; }
  .widebtn{ width:160px; height:64px; font-size:18px; border-radius:16px; }
  .row{display:flex; gap:.4rem}
  .col{display:flex; flex-direction:column; gap:.5rem; align-items:center; justify-content:center; min-width:160px}
  .pad{display:grid; grid-template-columns:repeat(3,64px); grid-template-rows:repeat(3,64px); gap:.4rem}
  .ghost{opacity:0}

  /* Joystick */
  .stickpad{ position:relative; width:180px; height:180px; border-radius:50%;
    background:radial-gradient(circle at 50% 50%, #f6f8ff, #e9efff);
    border:2px solid #0002; box-shadow:inset 0 6px 12px #0000000e, 0 4px 0 #0001; touch-action:none; }
  .stick{ position:absolute; left:50%; top:50%; width:84px; height:84px; margin:-42px 0 0 -42px; border-radius:50%;
    background:linear-gradient(180deg,#fff,#f0f5ff); border:2px solid #0003; box-shadow:0 4px 0 #0001;
    display:flex; align-items:center; justify-content:center; font-weight:800; color:var(--royal) }
  .modeToggle{min-width:160px}

  @media (max-width:480px){
    .btn{ width:56px; height:56px; font-size:20px; border-radius:14px; }
    .widebtn{ width:138px; height:56px; }
    .pad{ grid-template-columns:repeat(3,56px); grid-template-rows:repeat(3,56px); }
    .stickpad{ width:160px; height:160px }
    .stick{ width:76px; height:76px; margin:-38px 0 0 -38px }
  }
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>Tesla’s Toy Boat</h1>
    <div class="row">
      <span class="pill">Arrow keys or touch</span>
      <button class="btn widebtn modeToggle" id="mode">Switch to Joystick</button>
    </div>
  </header>

  <div id="pond">
    <canvas id="game" width="1280" height="720" aria-label="Pond"></canvas>
    <div class="hud" id="hud">
      <div>Score: <span id="score">0</span>/<span id="goal">10</span></div>
      <div>Speed: <span id="spd">0.0</span> m/s</div>
    </div>
  </div>

  <div class="hint">Collect buoys • Avoid reeds • Tap Lamp for ✨</div>

  <!-- Control Dock -->
  <div class="dock">
    <!-- Left: D-pad or Joystick (switchable) -->
    <div id="leftDock"></div>

    <!-- Right: actions -->
    <div class="col">
      <button class="btn widebtn" id="lamp" data-key="KeyT">💡 Lamp</button>
      <div class="row">
        <button class="btn" id="mute" title="Mute/Unmute">🔈</button>
        <button class="btn widebtn" id="reset">⟳ Restart</button>
      </div>
    </div>
  </div>
</div>

<script id="cfg" type="application/json">__CFG_JSON__</script>
<script>
(() => {
  // --- Config + Audio/Haptics ---
  const cfg = JSON.parse(document.getElementById('cfg').textContent || "{}");
  let audioCtx, muted=false;
  const AC = window.AudioContext || window.webkitAudioContext;
  function ensureAudio(){ if(!audioCtx && AC){ audioCtx=new AC(); } if(audioCtx && audioCtx.state==='suspended') audioCtx.resume(); }
  function beep(freq=660, dur=100, type='sine', gain=0.05){
    if(muted || !audioCtx) return;
    const o=audioCtx.createOscillator(), g=audioCtx.createGain();
    o.type=type; o.frequency.value=freq; g.gain.value=gain; o.connect(g); g.connect(audioCtx.destination);
    o.start(); setTimeout(()=>o.stop(), dur);
  }
  function vibrate(ms=20){ if(navigator.vibrate) try{ navigator.vibrate(ms); }catch{} }
  const muteBtn=document.getElementById('mute');
  muteBtn.addEventListener('click', ()=>{ ensureAudio(); muted=!muted; muteBtn.textContent=muted?'🔇':'🔈'; });

  // --- Canvas & sizing ---
  const canvas=document.getElementById('game'), ctx=canvas.getContext('2d');
  const W=canvas.width, H=canvas.height;
  const rand=(a,b)=>a+Math.random()*(b-a);
  function fit(){ const r=W/H; const box=document.getElementById('pond').getBoundingClientRect(); let w=box.width,h=box.height; if(w/h>r)w=h*r; else h=w/r; canvas.style.width=w+'px'; canvas.style.height=h+'px'; }
  addEventListener('resize', fit); fit();

  // --- State ---
  function spawn(){ return {
    boat:{ x:W*0.15, y:H*0.5, v:0, a:0, r:0, lamp:false },
    buoys:Array.from({length: cfg.buoy_count || 14}, ()=>({x:rand(W*0.25,W*0.9),y:rand(H*0.1,H*0.9),r:16,hue:rand(0,360)})),
    reeds:Array.from({length: cfg.reeds_count || 18}, ()=>({x:rand(W*0.2,W*0.95),y:rand(H*0.1,H*0.9),r:24})),
    score:0, won:false, goal:cfg.buoy_goal || 10, max_speed:cfg.max_speed || 240, drag:cfg.drag || 0.6
  }; }
  let state=spawn();

  // --- Input: keyboard + virtual ---
  const keys={}; addEventListener('keydown',e=>{ keys[e.code]=true; ensureAudio(); }); addEventListener('keyup',e=>{ keys[e.code]=false; });

  // D-pad builder
  function buildDpad(){
    const pad=document.createElement('div');
    pad.className='pad';
    pad.innerHTML = `
      <div class="ghost"></div>
      <button class="btn" data-key="ArrowUp" aria-label="Up">▲</button>
      <div class="ghost"></div>
      <button class="btn" data-key="ArrowLeft" aria-label="Left">◀</button>
      <div class="ghost"></div>
      <button class="btn" data-key="ArrowRight" aria-label="Right">▶</button>
      <div class="ghost"></div>
      <button class="btn" data-key="ArrowDown" aria-label="Down">▼</button>
      <div class="ghost"></div>`;
    pad.querySelectorAll('.btn[data-key]').forEach(el=>{
      const code=el.getAttribute('data-key');
      const press=e=>{ e.preventDefault(); ensureAudio(); keys[code]=true; };
      const release=e=>{ e.preventDefault(); keys[code]=false; };
      el.addEventListener('touchstart', press, {passive:false});
      el.addEventListener('touchend',   release, {passive:false});
      el.addEventListener('touchcancel',release, {passive:false});
      el.addEventListener('mousedown',  press);
      el.addEventListener('mouseup',    release);
      el.addEventListener('mouseleave', release);
    });
    return pad;
  }

  // Joystick builder
  let joy={x:0,y:0,active:false};
  function buildStick(){
    const pad=document.createElement('div'); pad.className='stickpad';
    const knob=document.createElement('div'); knob.className='stick'; knob.textContent='⛵️'; pad.appendChild(knob);
    const rect=()=>pad.getBoundingClientRect();
    function setFrom(evt){
      const r=rect(); const t=(evt.touches&&evt.touches[0])||evt;
      const cx=r.left+r.width/2, cy=r.top+r.height/2;
      let dx=t.clientX-cx, dy=t.clientY-cy; const max=r.width*0.42, m=Math.hypot(dx,dy);
      if(m>max){ dx*=max/m; dy*=max/m; }
      knob.style.transform=`translate(${dx}px,${dy}px)`; joy.x=dx/max; joy.y=dy/max; joy.active=true; ensureAudio();
    }
    function reset(){ knob.style.transform='translate(0,0)'; joy={x:0,y:0,active:false}; }
    pad.addEventListener('touchstart',e=>{ e.preventDefault(); setFrom(e); },{passive:false});
    pad.addEventListener('touchmove', e=>{ e.preventDefault(); setFrom(e); },{passive:false});
    pad.addEventListener('touchend',  e=>{ e.preventDefault(); reset(); },{passive:false});
    pad.addEventListener('mousedown', e=>{ e.preventDefault(); setFrom(e); });
    pad.addEventListener('mousemove', e=>{ if(e.buttons) setFrom(e); });
    pad.addEventListener('mouseup',   e=>{ reset(); });
    pad.addEventListener('mouseleave',e=>{ reset(); });
    return pad;
  }

  // Build left dock + toggle button
  const leftDock=document.getElementById('leftDock');
  let mode=(cfg.control || 'dpad'); // 'dpad' | 'joystick'
  const modeBtn=document.getElementById('mode');
  function renderLeft(){
    leftDock.innerHTML='';
    if(mode==='dpad'){ leftDock.appendChild(buildDpad()); modeBtn.textContent='Switch to Joystick'; }
    else{ leftDock.appendChild(buildStick()); modeBtn.textContent='Switch to D-pad'; }
  }
  modeBtn.addEventListener('click', ()=>{ mode=(mode==='dpad'?'joystick':'dpad'); renderLeft(); ensureAudio(); beep(440,80,'triangle',0.02); });
  renderLeft();

  // --- Lamp: tap toggle + press&hold (mobile) + keyboard 'T' ---
  const lampBtn=document.getElementById('lamp'); let lampHeld=false, touchStartTime=0, lastTouchTime=0;
  function refreshLampButton(){ const on = lampHeld || !!keys['KeyT']; lampBtn.classList.toggle('active', on); lampBtn.textContent = on ? '💡 Lamp ON' : '💡 Lamp'; }
  function setLampHeld(v){ lampHeld=v; refreshLampButton(); }

  // Mouse click toggles
  lampBtn.addEventListener('click', e=>{
    // Suppress the synthetic click right after a touch
    if (Date.now() - lastTouchTime < 350) return;
    e.preventDefault(); keys['KeyT'] = !keys['KeyT']; refreshLampButton(); ensureAudio(); beep(keys['KeyT']?760:520,80,'sine',0.03);
  });

  // Touch: hold = ON while held; quick tap (<250ms) = toggle
  lampBtn.addEventListener('touchstart', e=>{ e.preventDefault(); touchStartTime=Date.now(); setLampHeld(true); ensureAudio(); }, {passive:false});
  lampBtn.addEventListener('touchend', e=>{
    e.preventDefault();
    const dt = Date.now() - touchStartTime;
    setLampHeld(false);
    if (dt < 250){ keys['KeyT'] = !keys['KeyT']; ensureAudio(); beep(keys['KeyT']?760:520,80,'sine',0.03); }
    lastTouchTime = Date.now();
  }, {passive:false});
  lampBtn.addEventListener('touchcancel', e=>{ e.preventDefault(); setLampHeld(false); lastTouchTime = Date.now(); }, {passive:false});

  document.getElementById('reset').addEventListener('click', ()=>{ state=spawn(); vibrate(25); beep(380,80,'square',0.035); refreshLampButton(); });

  // --- Update/Draw/Loop ---
  function update(dt){
    const b=state.boat;
    // joystick or keys
    let thrust=0, brake=0, steer=0;
    if (mode==='joystick' && joy.active){ thrust = 100 * Math.max(0,-joy.y); steer = joy.x; }
    else { thrust=keys['ArrowUp']?100:0; brake=keys['ArrowDown']?60:0; steer=(keys['ArrowLeft']?-1:0)+(keys['ArrowRight']?1:0); }

    const turn=steer*(0.9-Math.min(0.6,b.v/200));
    b.a=thrust - brake - b.v*state.drag;
    b.v=Math.max(0, Math.min(state.max_speed, b.v + b.a*dt));
    b.r+=turn*dt; b.x+=Math.cos(b.r)*b.v*dt; b.y+=Math.sin(b.r)*b.v*dt;

    const bounce=0.4;
    if(b.x<30){b.x=30;b.r=Math.PI-b.r;b.v*=bounce;} if(b.x>W-30){b.x=W-30;b.r=Math.PI-b.r;b.v*=bounce;}
    if(b.y<30){b.y=30;b.r=-b.r;b.v*=bounce;}        if(b.y>H-30){b.y=H-30;b.r=-b.r;b.v*=bounce;}

    b.lamp = !!keys['KeyT'] || lampHeld;

    for(const r of state.reeds){ if(Math.hypot(b.x-r.x,b.y-r.y)<r.r+18) b.v*=0.965; }

    for(let i=state.buoys.length-1;i>=0;i--){
      const buoy=state.buoys[i];
      if(Math.hypot(b.x-buoy.x,b.y-buoy.y) < buoy.r+16){
        state.buoys.splice(i,1); state.score++;
        vibrate(18); ensureAudio(); beep(740,70,'sine',0.035); setTimeout(()=>beep(880,80,'triangle',0.03),80);
        if(state.score>=state.goal){ state.won=true; vibrate(80); setTimeout(()=>vibrate(80),120); }
      }
    }

    // HUD
    document.getElementById('score').textContent=Math.min(state.score,state.goal);
    document.getElementById('goal').textContent=state.goal;
    document.getElementById('spd').textContent=(b.v/30).toFixed(1);
  }

  function draw(){
    const b=state.boat; ctx.clearRect(0,0,W,H);

    // ripples
    for(let i=0;i<5;i++){ ctx.fillStyle=`rgba(255,255,255,${0.06-i*0.01})`; ctx.beginPath(); ctx.ellipse(b.x,b.y,80+i*28,40+i*18,b.r,0,Math.PI*2); ctx.fill(); }

    // buoys
    for(const buoy of state.buoys){ ctx.fillStyle=`hsl(${buoy.hue},90%,55%)`; ctx.beginPath(); ctx.arc(buoy.x,buoy.y,buoy.r,0,Math.PI*2); ctx.fill(); ctx.fillStyle="#fff"; ctx.beginPath(); ctx.arc(buoy.x,buoy.y,buoy.r*0.55,0,Math.PI*2); ctx.fill(); }

    // reeds
    for(const r of state.reeds){ ctx.strokeStyle="#0b7e2a"; ctx.lineWidth=3; ctx.beginPath(); ctx.moveTo(r.x,r.y+r.r-6); ctx.quadraticCurveTo(r.x+6,r.y-r.r*0.6,r.x,r.y-r.r-6); ctx.stroke(); }

    // boat
    ctx.save(); ctx.translate(b.x,b.y); ctx.rotate(b.r);
    const hullGrad=ctx.createLinearGradient(-28,0,28,0); hullGrad.addColorStop(0,"#111"); hullGrad.addColorStop(1,"#444");
    ctx.fillStyle=hullGrad; ctx.strokeStyle="#ffffffcc"; ctx.lineWidth=3;
    ctx.beginPath(); ctx.moveTo(28,0); ctx.quadraticCurveTo(14,12,-18,14);
    ctx.quadraticCurveTo(-24,0,-18,-14); ctx.quadraticCurveTo(14,-12,28,0);
    ctx.closePath(); ctx.fill(); ctx.stroke();

    // royal blue stripe + lamp
    ctx.fillStyle="#4169e1"; ctx.fillRect(-10,-3,20,6);
    if(b.lamp){
      const g=ctx.createRadialGradient(18,0,0,18,0,70); g.addColorStop(0,"rgba(65,105,225,.95)"); g.addColorStop(1,"rgba(65,105,225,0)");
      ctx.fillStyle=g; ctx.beginPath(); ctx.arc(18,0,70,0,Math.PI*2); ctx.fill();
      ctx.save(); ctx.globalAlpha=0.35; ctx.beginPath(); ctx.moveTo(18,0); ctx.lineTo(180,-40); ctx.lineTo(180,40); ctx.closePath();
      const bg=ctx.createLinearGradient(18,0,180,0); bg.addColorStop(0,"rgba(65,105,225,0.65)"); bg.addColorStop(1,"rgba(65,105,225,0)");
      ctx.fillStyle=bg; ctx.fill(); ctx.restore();
    }
    ctx.fillStyle=b.lamp?"#4169e1":"#ccc"; ctx.beginPath(); ctx.arc(18,0,6,0,Math.PI*2); ctx.fill();
    ctx.restore();

    // win banner — just "Victory"
    if(state.won){
      ctx.fillStyle="rgba(255,255,255,.86)"; ctx.fillRect(W*0.2,H*0.4,W*0.6,110);
      ctx.strokeStyle="#0002"; ctx.lineWidth=6; ctx.strokeRect(W*0.2,H*0.4,W*0.6,110);
      ctx.fillStyle="#111"; ctx.font="bold 30px system-ui"; ctx.fillText("Victory", W*0.45, H*0.4+60);
    }
  }

  // First frame (in case rAF is throttled)
  draw();

  // Loop
  let last=performance.now();
  function tick(t){ const dt=Math.min(0.032,(t-last)/1000); last=t; update(dt); draw(); requestAnimationFrame(tick); }
  requestAnimationFrame(tick);
})();
</script>
</body>
</html>
"""

components.html(HTML.replace("__CFG_JSON__", json.dumps(cfg)), height=800, scrolling=False)
