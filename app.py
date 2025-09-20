
# tesla_toy_boat_streamlit.py
# Streamlit app: Tesla's Toy Boat — Teleautomaton Mini-Game (Royal Blue Theme, full recolor)

import json
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Tesla’s Toy Boat — Streamlit", page_icon="⛵️", layout="wide")

# Sidebar controls
st.sidebar.header("⛵️ Game Settings")
buoy_goal = st.sidebar.slider("Buoy goal (win condition)", 5, 25, 10, 1)
buoy_count = st.sidebar.slider("Total buoys spawned", buoy_goal, 40, max(14, buoy_goal), 1)
reeds_count = st.sidebar.slider("Reeds (hazards)", 0, 40, 18, 1)
max_speed = st.sidebar.slider("Max boat speed (pixels/s)", 120, 320, 220, 10)
drag = st.sidebar.slider("Water drag (higher = slows faster)", 0.2, 1.2, 0.6, 0.05)
st.sidebar.caption("Tip: Lower max speed and higher drag = calmer handling.")

st.title("⚡️ Tesla’s Toy Boat — Teleautomaton (1898) [Royal Blue Edition]")

cfg = {
    "buoy_goal": int(buoy_goal),
    "buoy_count": int(buoy_count),
    "reeds_count": int(reeds_count),
    "max_speed": float(max_speed),
    "drag": float(drag),
}
cfg_json = json.dumps(cfg)

# HTML/JS code (game engine)
html = f"""
<!doctype html>
<html lang='en'>
<head>
<meta charset='utf-8' />
<meta name='viewport' content='width=device-width, initial-scale=1' />
<title>Tesla’s Toy Boat — Royal Blue</title>
<style>
  :root {{
    --royal:#4169e1;
    --sea:#87cefa; --sea2:#4682b4;
  }}
  html,body {{margin:0;height:100%;background:linear-gradient(180deg,var(--sea),var(--sea2));font-family:sans-serif;}}
  #pond {{border:4px solid #ffffffaa;border-radius:16px;position:relative;overflow:hidden;min-height:420px}}
  canvas{{display:block;width:100%;height:100%}}
</style>
</head>
<body>
<div id="pond"><canvas id="game" width="1280" height="720"></canvas></div>
<script>
(() => {{
  const cfg = {cfg_json};
  const canvas=document.getElementById('game'),ctx=canvas.getContext('2d');
  const W=canvas.width,H=canvas.height,rand=(a,b)=>a+Math.random()*(b-a);
  let boat={{x:W*0.15,y:H*0.5,v:0,r:0,lamp:false}},buoys=[],reeds=[],score=0,won=false;
  for(let i=0;i<cfg.buoy_count;i++) buoys.push({{x:rand(W*0.25,W*0.9),y:rand(H*0.1,H*0.9),r:16,hue:rand(0,360)}});
  for(let i=0;i<cfg.reeds_count;i++) reeds.push({{x:rand(W*0.2,W*0.9),y:rand(H*0.1,H*0.9),r:24}});
  const keys={{}};document.addEventListener('keydown',e=>keys[e.code]=true);document.addEventListener('keyup',e=>keys[e.code]=false);
  let last=performance.now();function loop(t){{const dt=Math.min(0.032,(t-last)/1000);last=t;update(dt);draw();requestAnimationFrame(loop);}}requestAnimationFrame(loop);
  function update(dt){{const thrust=keys['ArrowUp']?80:0;brake=keys['ArrowDown']?60:0;left=keys['ArrowLeft']?-1:0;right=keys['ArrowRight']?1:0;boat.v+= (thrust-brake-boat.v*cfg.drag)*dt;boat.v=Math.max(0,Math.min(cfg.max_speed,boat.v));boat.r+=(left+right)*dt;boat.x+=Math.cos(boat.r)*boat.v*dt;boat.y+=Math.sin(boat.r)*boat.v*dt;boat.lamp=keys['KeyT']||false;for(let i=buoys.length-1;i>=0;i--){{if(Math.hypot(boat.x-buoys[i].x,boat.y-buoys[i].y)<buoys[i].r+16){{buoys.splice(i,1);score++;if(score>=cfg.buoy_goal)won=true;}}}}}}
  function draw(){{ctx.clearRect(0,0,W,H);ctx.save();ctx.translate(boat.x,boat.y);ctx.rotate(boat.r);ctx.fillStyle="#333";ctx.beginPath();ctx.moveTo(28,0);ctx.quadraticCurveTo(14,12,-18,14);ctx.quadraticCurveTo(-24,0,-18,-14);ctx.quadraticCurveTo(14,-12,28,0);ctx.closePath();ctx.fill();ctx.fillStyle="#4169e1";ctx.fillRect(-10,-3,20,6);if(boat.lamp){{const g=ctx.createRadialGradient(18,0,0,18,0,36);g.addColorStop(0,"rgba(65,105,225,.9)");g.addColorStop(1,"rgba(65,105,225,0)");ctx.fillStyle=g;ctx.beginPath();ctx.arc(18,0,36,0,Math.PI*2);ctx.fill();}}ctx.fillStyle=boat.lamp?"#4169e1":"#ccc";ctx.beginPath();ctx.arc(18,0,6,0,Math.PI*2);ctx.fill();ctx.restore();for(const b of buoys){{ctx.fillStyle=`hsl(${b.hue},90%,55%)`;ctx.beginPath();ctx.arc(b.x,b.y,b.r,0,Math.PI*2);ctx.fill();}}if(won){{ctx.fillStyle="rgba(255,255,255,.8)";ctx.fillRect(W*0.2,H*0.4,W*0.6,100);ctx.fillStyle="#000";ctx.font="24px sans-serif";ctx.fillText("Victory in Royal Blue!",W*0.3,H*0.46);}}}}
}})();
</script>
</body>
</html>
"""

components.html(html,height=680,scrolling=False)
