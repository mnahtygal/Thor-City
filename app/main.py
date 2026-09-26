import asyncio, os, socket, time
from pathlib import Path
import psutil
import httpx
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

BASE=Path(__file__).resolve().parent
STATIC=BASE/"static"
app=FastAPI(title="THOR CITY",version="0.5.0")
app.mount("/static",StaticFiles(directory=STATIC),name="static")
BOOT=psutil.boot_time()
_last_net=psutil.net_io_counters(); _last_net_time=time.time()
REMOTE_URL=os.getenv("THOR_CITY_MAC_URL","http://10.0.0.47:8766/api/snapshot")
MAX_LOCAL=180; MAX_REMOTE=160

def category(name,cmd):
    s=f"{name} {cmd}".lower()
    if any(x in s for x in ("llama","jarvis","whisper","piper","ollama","stable-diffusion")): return "AI"
    if any(x in s for x in ("docker","containerd","podman")): return "DOCKER"
    if any(x in s for x in ("postgres","mysql","mariadb","redis","mongod","sql")): return "DATA"
    if any(x in s for x in ("code","cursor","git","node","npm","java","gradle","python")): return "DEV"
    if any(x in s for x in ("ssh","networkmanager","nm-","avahi","tailscale","nginx","apache","firefox","chrome","chromium")): return "NETWORK"
    if any(x in s for x in ("nvidia","cuda","nvargus","tegra","gpu")): return "NVIDIA"
    if any(x in s for x in ("gnome","gdm","xorg","wayland","pipewire","pulseaudio","dbus","xdg","windowserver","finder","dock")): return "DESKTOP"
    return "SYSTEM"

def local_snapshot():
    global _last_net,_last_net_time
    now=time.time(); vm=psutil.virtual_memory(); net=psutil.net_io_counters()
    dt=max(now-_last_net_time,.001); rx=max(0,net.bytes_recv-_last_net.bytes_recv)/dt; tx=max(0,net.bytes_sent-_last_net.bytes_sent)/dt
    _last_net,_last_net_time=net,now
    procs=[]
    for p in psutil.process_iter(["pid","name","username","memory_info","num_threads","cmdline","status"]):
        try:
            i=p.info; cmd=" ".join(i.get("cmdline") or []); name=i.get("name") or "unknown"
            procs.append({"pid":i["pid"],"name":name,"user":i.get("username") or "?","memory":i["memory_info"].rss if i.get("memory_info") else 0,
             "cpu":p.cpu_percent(None),"threads":i.get("num_threads") or 0,"status":i.get("status") or "?","cmd":cmd[:300],"category":category(name,cmd)})
        except (psutil.NoSuchProcess,psutil.AccessDenied,psutil.ZombieProcess): pass
    procs.sort(key=lambda x:(x["memory"],x["cpu"]),reverse=True)
    return {"host":{"hostname":socket.gethostname(),"label":"THOR","online":True,"cpu":psutil.cpu_percent(None),"memory_percent":vm.percent,
      "memory_used":vm.used,"memory_total":vm.total,"processes":len(procs),"rx_per_sec":rx,"tx_per_sec":tx,"uptime":now-BOOT},
      "processes":procs[:MAX_LOCAL],"aggregated":max(0,len(procs)-MAX_LOCAL),"timestamp":now}

async def combined():
    thor=local_snapshot(); hosts=[thor]
    try:
        async with httpx.AsyncClient(timeout=1.2) as client:
            r=await client.get(REMOTE_URL); r.raise_for_status(); mac=r.json()
            mac["host"]["label"]="MAC MINI"; mac["host"]["online"]=True
            rp=mac.get("processes",[]); rp.sort(key=lambda x:(x.get("memory",0)+x.get("cpu",0)*20000000),reverse=True)
            mac["processes"]=rp[:MAX_REMOTE]; mac["aggregated"]=max(0,mac["host"].get("processes",len(rp))-len(mac["processes"])); hosts.append(mac)
    except Exception:
        hosts.append({"host":{"hostname":"mac-mini","label":"MAC MINI","online":False,"cpu":0,"memory_percent":0,"processes":0,
          "rx_per_sec":0,"tx_per_sec":0,"uptime":0},"processes":[],"aggregated":0,"timestamp":time.time()})
    return {"hosts":hosts,"timestamp":time.time()}

@app.get("/")
async def index(): return FileResponse(STATIC/"index.html")
@app.get("/api/snapshot")
async def snap(): return await combined()
@app.websocket("/ws")
async def ws(websocket:WebSocket):
    await websocket.accept()
    try:
        while True:
            await websocket.send_json(await combined()); await asyncio.sleep(2.5)
    except (WebSocketDisconnect,RuntimeError): pass
