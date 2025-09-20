# tesla_toy_boat_streamlit.py
# Tesla’s Toy Boat — Royal Blue • Mobile-friendly + D-pad/Joystick + Haptics + Lamp Beam
# HUD pinned bottom-right inside the pond.
# Run: streamlit run tesla_toy_boat_streamlit.py

import json
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Tesla’s Toy Boat", page_icon="⛵️", layout="wide")

# Sidebar tuning
st.sidebar.header("⛵️ Game Settings")
buoy_goal = st.sidebar.slider("Buoy goal (win condition)", 5, 25, 10, 1)
buoy_count = st.sidebar.slider("Total buoys spawned", buoy_goal, 40, max(14, buoy_goal), 1)
reeds_count = st.sidebar.slider("Reeds (hazards)", 0, 40, 18, 1)
max_speed = st.sidebar.slider("Max boat speed (pixels/s)", 120, 360, 240, 10)
drag = st.sidebar.slider("Water drag (higher = slows faster)", 0.2, 1.2, 0.6, 0.05)
control_mode = st.sidebar.selectbox("Control mode (mobile)", ["D-pad", "Joystick"])

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
<html lang='en'>
<head>
<meta charset='utf-8' />
<meta name='viewport' content='width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no' />
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

  <div class="dock">
    <div id="leftDock"></div>
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
  const cfg = JSON.parse(document.getElementById('cfg').textContent || "{}");
  const canvas = document.getElementById('game'), ctx = canvas.getContext('2d');
  const W=canvas.width, H=canvas.height; const rand=(a,b)=>a+Math.random()*(b-a);

  function fit(){ const r=W/H; const box=document.getElementById('pond').getBoundingClientRect(); let w=box.width,h=box.height; if(w/h>r)w=h*r; else h=w/r; canvas.style.width=w+'px'; canvas.style.height=h+'px'; }
  addEventListener('resize',fit); fit();

  function spawn(){ return { boat:{x:W*0.15,y:H*0.5,v:0,a:0,r:0,lamp:false}, buoys:Array.from({length:cfg.buoy_count||14},()=>({x:rand(W*0.25,W*0.9),y:rand(H*0.1,H*0.9),r:16,hue:rand(0,360)})), reeds:Array.from({length:cfg.reeds_count||18},()=>({x:rand(W*0.2,W*0.95),y:rand(H*0.1,H*0.9),r:24})), score:0, won:false, goal:cfg.buoy_goal||10, max_speed:cfg.max_speed||240, drag:cfg.drag||0.6 }; }
  let state=spawn();

  const keys={}; addEventListener('keydown',e=>{keys[e.code]=true;}); addEventListener('keyup',e=>{keys[e.code]=false;});

  // --- Lamp handling ---
  const lampBtn=document.getElementById('lamp'); let lampHeld=false;
  function refreshLampButton(){ const on=lampHeld||!!keys['KeyT']; lampBtn.classList.toggle('active',on); lampBtn.textContent= on ? '💡 Lamp ON' : '💡 Lamp'; }
  function setLampHeld(v){ lampHeld=v; refreshLampButton(); }
  lampBtn.addEventListener('click',e=>{e.preventDefault(); keys['KeyT']=!keys['KeyT']; refreshLampButton();});
  const press=e=>{e.preventDefault();setLampHeld(true);}; const release=e=>{e.preventDefault();setLampHeld(false);};
  lampBtn.addEventListener('touchstart',press,{passive:false}); lampBtn.addEventListener('touchend',release,{passive:false}); lampBtn.addEventListener('mousedown',press); lampBtn.addEventListener('mouseup',release); lampBtn.addEventListener('mouseleave',release);
  refreshLampButton();

  document.getElementById('reset').addEventListener('click',()=>{state=spawn(); refreshLampButton();});

  // --- Game loop ---
  function update(dt){
    const b=state.boat; let thrust=0,brake=0,steer=0;
    thrust=keys['ArrowUp']?100:0; brake=keys['ArrowDown']?60:0; steer=(keys['ArrowLeft']?-1:0)+(keys['ArrowRight']?1:0);
    const turn=steer*(0.9-Math.min(0.6,b.v/200));
    b.a=thrust-brake-b.v*state.drag; b.v+=b.a*dt; b.v=Math.max(0,Math.min(state.max_speed,b.v)); b.r+=turn*dt; b.x+=Math.cos(b.r)*b.v*dt; b.y+=Math.sin(b.r)*b.v*dt;
    if(b.x<30){b.x=30;b.r=Math.PI-b.r;b.v*=0.4;} if(b.x>W-30){b.x=W-30;b.r=Math.PI-b.r;b.v*=0.4;} if(b.y<30){b.y=30;b.r=-b.r;b.v*=0.4;} if(b.y>H-30){b.y=H-30;b.r=-b.r;b.v*=0.4;}
    b.lamp=!!keys['KeyT']||lampHeld;
    for(const r of state.reeds){if(Math.hypot(b.x-r.x,b.y-r.y)<r.r+18)b.v*=0.965;}
    for(let i=state.buoys.length-1;i>=0;i--){const buoy=state.buoys[i]; if(Math.hypot(b.x-buoy.x,b.y-buoy.y)<buoy.r+16){state.buoys.splice(i,1); state.score++; if(state.score>=state.goal)state.won=true;}}
    document.getElementById('score').textContent=Math.min(state.score,state.goal); document.getElementById('goal').textContent=state.goal; document.getElementById('spd').textContent=(b.v/30).toFixed(1);
  }

  function draw(){const b=state.boat; ctx.clearRect(0,0,W,H);
    for(let i=0;i<5;i++){ctx.fillStyle=`rgba(255,255,255,${0.06-i*0.01})`; ctx.beginPath(); ctx.ellipse(b.x,b.y,80+i*28,40+i*18,b.r,0,Math.PI*2); ctx.fill();}
    for(const buoy of state.buoys){ctx.fillStyle=`hsl(${buoy.hue},90%,55%)`; ctx.beginPath(); ctx.arc(buoy.x,buoy.y,buoy.r,0,Math.PI*2); ctx.fill(); ctx.fillStyle="#fff"; ctx.beginPath(); ctx.arc(buoy.x,buoy.y,buoy.r*0.55,0,Math.PI*2); ctx.fill();}
    for(const r of state.reeds){ctx.strokeStyle="#0b7e2a"; ctx.lineWidth=3; ctx.beginPath(); ctx.moveTo(r.x,r.y+r.r-6); ctx.quadraticCurveTo(r.x+6,r.y-r.r*0.6,r.x,r.y-r.r-6); ctx.stroke();}
    ctx.save(); ctx.translate(b.x,b.y); ctx.rotate(b.r); const hullGrad=ctx.createLinearGradient(-28,0,28,0); hullGrad.addColorStop(0,"#111"); hullGrad.addColorStop(1,"#444"); ctx.fillStyle=hullGrad; ctx.strokeStyle="#ffffffcc"; ctx.lineWidth=3; ctx.beginPath(); ctx.moveTo(28,0); ctx.quadraticCurveTo(14,12,-18,14); ctx.quadraticCurveTo(-24,0,-18,-14); ctx.quadraticCurveTo(14,-12,28,0); ctx.closePath(); ctx.fill(); ctx.stroke(); ctx.fillStyle="#4169e1"; ctx.fillRect(-10,-3,20,6);
    if(b.lamp){const g=ctx.createRadialGradient(18,0,0,18,0,70); g.addColorStop(0,"rgba(65,105,225,.95)"); g.addColorStop(1,"rgba(65,105,225,0)"); ctx.fillStyle=g; ctx.beginPath(); ctx.arc(18,0,70,0,Math.PI*2); ctx.fill();
      ctx.save(); ctx.globalAlpha=0.35; ctx.beginPath(); ctx.moveTo(18,0); ctx.lineTo(180,-40); ctx.lineTo(180,40); ctx.closePath(); const bg=ctx.createLinearGradient(18,0,180,0); bg.addColorStop(0,"rgba(65,105,225,0.65)"); bg.addColorStop(1,"rgba(65,105,225,0)"); ctx.fillStyle=bg; ctx.fill(); ctx.restore();}
    ctx.fillStyle=b.lamp?"#4169e1":"#ccc"; ctx.beginPath(); ctx.arc(18,0,6,0,Math.PI*2); ctx.fill(); ctx.restore();
    if(state.won){ctx.fillStyle="rgba(255,255,255,.86)"; ctx.fillRect(W*0.2,H*0.4,W*0.6,110); ctx.strokeStyle="#0002"; ctx.lineWidth=6; ctx.strokeRect(W*0.2,H*0.4,W*0.6,110); ctx.fillStyle="#111"; ctx.font="bold 30px system-ui"; ctx.fillText("Victory",W*0.45,H*0.4+60);}
  }

  let last=performance.now(); function loop(t){const dt=Math.min(0.032,(t-last)/1000); last=t; update(dt); draw(); requestAnimationFrame(loop);} requestAnimationFrame(loop);
})();
</script>
</body>
</html>
"""

components.html(HTML.replace("__CFG_JSON__", json.dumps(cfg)), height=800, scrolling=False)
