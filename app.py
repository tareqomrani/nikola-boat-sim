# tesla_toy_boat_streamlit.py
# Streamlit: Tesla’s Toy Boat. (Royal Blue Edition, self-contained)
# Run with: streamlit run tesla_toy_boat_streamlit.py

import json
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Tesla’s Toy Boat.", page_icon="⛵️", layout="wide")

# Sidebar controls
st.sidebar.header("⛵️ Game Settings")
buoy_goal = st.sidebar.slider("Buoy goal (win condition)", 5, 25, 10, 1)
buoy_count = st.sidebar.slider("Total buoys spawned", buoy_goal, 40, max(14, buoy_goal), 1)
reeds_count = st.sidebar.slider("Reeds (hazards)", 0, 40, 18, 1)
max_speed = st.sidebar.slider("Max boat speed (pixels/s)", 120, 320, 220, 10)
drag = st.sidebar.slider("Water drag (higher = slows faster)", 0.2, 1.2, 0.6, 0.05)

cfg = dict(
    buoy_goal=int(buoy_goal),
    buoy_count=int(buoy_count),
    reeds_count=int(reeds_count),
    max_speed=float(max_speed),
    drag=float(drag),
)

# Inline HTML + JS template with placeholder for config
HTML_TEMPLATE = r"""
<!doctype html>
<html lang='en'>
<head>
<meta charset='utf-8' />
<meta name='viewport' content='width=device-width, initial-scale=1' />
<title>Tesla’s Toy Boat.</title>
<style>
  :root {
    --royal:#4169e1;
    --sea:#87cefa;
    --sea2:#4682b4;
  }
  html,body {
    margin:0;
    height:100%;
    background:linear-gradient(180deg,var(--sea),var(--sea2));
    font-family:sans-serif;
  }
  .wrap{display:flex;flex-direction:column;min-height:620px}
  header{display:flex;justify-content:center;padding:.6rem;background:linear-gradient(90deg,#fff8,var(--royal) 70%,#fff8);border-bottom:2px solid #0002}
  header h1{font-size:1.2rem;margin:0;color:var(--royal)}
  #pond {border:4px solid #ffffffaa;border-radius:16px;position:relative;overflow:hidden;min-height:420px;max-width:1200px;margin:0 auto}
  canvas{display:block;width:100%;height:100%}
  .hint{color:#000a;text-align:center;padding:.5rem 0}
</style>
</head>
<body>
<div class="wrap">
  <header><h1>Tesla’s Toy Boat.</h1></header>
  <div id="pond"><canvas id="game" width="1280" height="720" aria-label="Pond"></canvas></div>
  <div class="hint">Arrow keys to steer • T for lamp • Collect buoys • Avoid reeds</div>
</div>

<script id="cfg" type="application/json">__CFG_JSON__</script>
<script>
(() => {
  const cfg = JSON.parse(document.getElementById('cfg').textContent || "{}");

  const canvas = document.getElementById('game');
  const ctx = canvas.getContext('2d');
  const W=canvas.width,H=canvas.height;
  const rand=(a,b)=>a+Math.random()*(b-a);

  function fit() {
    const r = canvas.width / canvas.height;
    const box = document.getElementById('pond').getBoundingClientRect();
    let w = box.width, h = box.height;
    if (w/h > r) w = h * r; else h = w / r;
    canvas.style.width = w + 'px';
    canvas.style.height = h + 'px';
  }
  addEventListener('resize', fit); fit();

  const state = {
    boat: {x:W*0.15,y:H*0.5,v:0,a:0,r:0,lamp:false},
    buoys: Array.from({length: cfg.buoy_count || 14}, ()=>({x:rand(W*0.25,W*0.9),y:rand(H*0.1,H*0.9),r:16,hue:rand(0,360)})),
    reeds: Array.from({length: cfg.reeds_count || 18}, ()=>({x:rand(W*0.2,W*0.9),y:rand(H*0.1,H*0.9),r:24})),
    score: 0,
    won:false,
    goal: cfg.buoy_goal || 10,
    max_speed: cfg.max_speed || 220,
    drag: cfg.drag || 0.6
  };

  const keys={};
  document.addEventListener('keydown',e=>{keys[e.code]=true;});
  document.addEventListener('keyup',e=>{keys[e.code]=false;});

  let last=performance.now();
  function loop(t){
    const dt=Math.min(0.032,(t-last)/1000);last=t;
    update(dt);draw();
    requestAnimationFrame(loop);
  }
  requestAnimationFrame(loop);

  function update(dt){
    const b=state.boat;
    const thrust=keys['ArrowUp']?80:0,brake=keys['ArrowDown']?60:0;
    const left=keys['ArrowLeft']?-1:0,right=keys['ArrowRight']?1:0;
    const turn=(left+right)*(0.9-Math.min(0.6,b.v/200));

    b.a=thrust-brake-b.v*state.drag;
    b.v+=b.a*dt;
    b.v=Math.max(0,Math.min(state.max_speed,b.v));

    b.r+=turn*dt;
    b.x+=Math.cos(b.r)*b.v*dt;
    b.y+=Math.sin(b.r)*b.v*dt;

    if(b.x<30){b.x=30;b.r=Math.PI-b.r;b.v*=0.4;}
    if(b.x>W-30){b.x=W-30;b.r=Math.PI-b.r;b.v*=0.4;}
    if(b.y<30){b.y=30;b.r=-b.r;b.v*=0.4;}
    if(b.y>H-30){b.y=H-30;b.r=-b.r;b.v*=0.4;}

    b.lamp=!!keys['KeyT'];

    for(const r of state.reeds){
      if(Math.hypot(b.x-r.x,b.y-r.y)<r.r+18)b.v*=0.965;
    }
    for(let i=state.buoys.length-1;i>=0;i--){
      const buoy=state.buoys[i];
      if(Math.hypot(b.x-buoy.x,b.y-buoy.y)<buoy.r+16){
        state.buoys.splice(i,1);
        state.score++;
        if(state.score>=state.goal)state.won=true;
      }
    }
  }

  function draw(){
    const b=state.boat;
    ctx.clearRect(0,0,W,H);

    // ripples
    for(let i=0;i<5;i++){
      ctx.fillStyle=`rgba(255,255,255,${0.06-i*0.01})`;
      ctx.beginPath();ctx.ellipse(b.x,b.y,80+i*28,40+i*18,b.r,0,Math.PI*2);ctx.fill();
    }

    // buoys
    for(const buoy of state.buoys){
      ctx.fillStyle=`hsl(${buoy.hue},90%,55%)`;
      ctx.beginPath();ctx.arc(buoy.x,buoy.y,buoy.r,0,Math.PI*2);ctx.fill();
      ctx.fillStyle="#fff";ctx.beginPath();ctx.arc(buoy.x,buoy.y,buoy.r*0.55,0,Math.PI*2);ctx.fill();
    }

    // reeds
    for(const r of state.reeds){
      ctx.strokeStyle="#0b7e2a";ctx.lineWidth=3;
      ctx.beginPath();ctx.moveTo(r.x,r.y+r.r-6);
      ctx.quadraticCurveTo(r.x+6,r.y-r.r*0.6,r.x,r.y-r.r-6);
      ctx.stroke();
    }

    // boat
    ctx.save();ctx.translate(b.x,b.y);ctx.rotate(b.r);
    const hullGrad=ctx.createLinearGradient(-28,0,28,0);
    hullGrad.addColorStop(0,"#111");hullGrad.addColorStop(1,"#444");
    ctx.fillStyle=hullGrad;ctx.strokeStyle="#ffffffcc";ctx.lineWidth=3;
    ctx.beginPath();
    ctx.moveTo(28,0);ctx.quadraticCurveTo(14,12,-18,14);
    ctx.quadraticCurveTo(-24,0,-18,-14);
    ctx.quadraticCurveTo(14,-12,28,0);
    ctx.closePath();ctx.fill();ctx.stroke();

    // royal blue stripe
    ctx.fillStyle="#4169e1";ctx.fillRect(-10,-3,20,6);

    // lamp
    if(b.lamp){
      const g=ctx.createRadialGradient(18,0,0,18,0,36);
      g.addColorStop(0,"rgba(65,105,225,.9)");
      g.addColorStop(1,"rgba(65,105,225,0)");
      ctx.fillStyle=g;ctx.beginPath();ctx.arc(18,0,36,0,Math.PI*2);ctx.fill();
    }
    ctx.fillStyle=b.lamp?"#4169e1":"#ccc";
    ctx.beginPath();ctx.arc(18,0,6,0,Math.PI*2);ctx.fill();
    ctx.restore();

    if(state.won){
      ctx.fillStyle="rgba(255,255,255,.86)";
      ctx.fillRect(W*0.2,H*0.4,W*0.6,110);
      ctx.strokeStyle="#0002";ctx.lineWidth=6;
      ctx.strokeRect(W*0.2,H*0.4,W*0.6,110);
      ctx.fillStyle="#111";ctx.font="bold 30px system-ui";
      ctx.fillText("Victory in Royal Blue!",W*0.26,H*0.4+60);
    }
  }
})();
</script>
</body>
</html>
"""

# Inject config JSON
html = HTML_TEMPLATE.replace("__CFG_JSON__", json.dumps(cfg))

components.html(html, height=720, scrolling=False)
