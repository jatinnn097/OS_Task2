
import json
import os
import threading
import time
import webbrowser
from pathlib import Path


class Trace:
    def __init__(self):
        self._lock = threading.Lock()
        self.events = []
        self._t0 = time.monotonic()

    def log(self, actor, kind, **data):
        with self._lock:
            event = {
                "seq": len(self.events),
                "t": round(time.monotonic() - self._t0, 3),
                "actor": actor,
                "kind": kind
            }
            event.update(data)
            self.events.append(event)


_TEMPLATE = r"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title>
<style>
body{font-family:system-ui,sans-serif;margin:0;background:#f1f5f9;color:#1e293b}
header{padding:20px;background:#fff;border-bottom:1px solid #cbd5e1;font-size:22px;font-weight:bold}
.controls{padding:16px;display:flex;gap:10px;flex-wrap:wrap}
button{border:0;padding:10px 16px;border-radius:8px;background:#2563eb;color:white;cursor:pointer}
main{display:grid;grid-template-columns:1.2fr 1fr;gap:16px;padding:16px}
section{background:white;border:1px solid #e2e8f0;border-radius:12px;padding:16px;min-width:0}
#stage{min-height:350px}
#log{height:450px;overflow:auto}
.event{padding:10px;border:1px solid #dbeafe;border-radius:8px;margin:10px 0;width:75%;background:#f8fafc}
.event:nth-child(even){margin-left:20%}
small{color:#64748b}
@media(max-width:700px){main{grid-template-columns:1fr}}
</style>
</head>
<body>
<header>__TITLE__</header>
<div class="controls">
<button id="play">Play</button>
<button id="step">Step</button>
<button id="reset">Reset</button>
<label>Speed <select id="speed"><option value="800">0.5x</option><option value="400" selected>1x</option><option value="200">2x</option><option value="80">5x</option></select></label>
<input id="slider" type="range" min="0" value="0">
<span id="clock"></span>
</div>
<main>
<section><h2>Simulation</h2><div id="stage"></div></section>
<section><h2>Event timeline</h2><div id="log"></div></section>
</main>
<script>
const D=__DATA__,E=D.events;
let idx=0,timer=null;
const $=id=>document.getElementById(id);
$('slider').max=E.length;
function compute(n){
 const state={},forks={};
 D.actors.forEach(a=>state[a]='thinking');
 for(let i=0;i<D.forks;i++)forks[i]=null;
 for(let i=0;i<n;i++){
  const e=E[i];
  if(e.kind==='state')state[e.actor]=e.state;
  if(e.kind==='fork')forks[e.fork]=e.owner;
 }
 return {state,forks};
}
function render(){
 const {state,forks}=compute(idx);
 let html='<div style="display:flex;flex-wrap:wrap;gap:12px">';
 D.actors.forEach(a=>{
  const s=state[a]||'thinking';
  const c=s==='eating'?'#bbf7d0':s==='hungry'?'#fef3c7':s==='done'?'#e2e8f0':'#dbeafe';
  html+=`<div style="padding:16px;border-radius:10px;background:${c};min-width:100px"><b>${a}</b><p>${s}</p></div>`;
 });
 html+='</div><h3>Forks</h3><div style="display:flex;gap:8px;flex-wrap:wrap">';
 Object.keys(forks).forEach(f=>{
  html+=`<div style="padding:10px;background:#f1f5f9;border-radius:8px">Fork ${f}: ${forks[f]===null?'Available':'P'+forks[f]}</div>`;
 });
 html+='</div>';
 $('stage').innerHTML=html;
 $('log').innerHTML=E.slice(0,idx).map(e=>{
  let msg=e.kind==='state'?`${e.actor} → ${e.state}`:
   e.kind==='fork'?`Fork ${e.fork}: ${e.owner===null?'released':'taken by P'+e.owner}`:
   `${e.actor}: ${e.kind}`;
  return `<div class="event"><b>${msg}</b><br><small>Event ${e.seq+1} · ${e.t}s</small></div>`;
 }).join('');
 $('slider').value=idx;
 $('clock').textContent=idx+'/'+E.length+' events';
 $('log').scrollTop=$('log').scrollHeight;
}
function pause(){clearInterval(timer);timer=null;$('play').textContent='Play'}
function tick(){if(idx<E.length){idx++;render()}else pause()}
function play(){if(timer){pause();return}if(idx>=E.length)idx=0;timer=setInterval(tick,+$('speed').value);$('play').textContent='Pause'}
$('play').onclick=play;
$('step').onclick=()=>{pause();tick()};
$('reset').onclick=()=>{pause();idx=0;render()};
$('speed').onchange=()=>{if(timer){pause();play()}};
$('slider').oninput=e=>{pause();idx=+e.target.value;render()};
render();
</script>
</body>
</html>
"""


def write_html(path, title, mode, actors, trace, forks=0):
    payload = {
        "title": title,
        "mode": mode,
        "actors": actors,
        "forks": forks,
        "events": trace.events
    }

    html = _TEMPLATE.replace("__TITLE__", title)
    html = html.replace("__DATA__", json.dumps(payload))

    path = os.path.abspath(path)
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as file:
        file.write(html)

    print(f"HTML simulation written to: {path}")
    print(f"Total events: {len(trace.events)}")

    try:
        webbrowser.open(Path(path).as_uri())
    except Exception:
        print("Open the HTML file manually in your browser.")
