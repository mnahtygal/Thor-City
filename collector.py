import socket,time,psutil
from fastapi import FastAPI
import uvicorn
app=FastAPI(title="THOR CITY Remote Collector")
boot=psutil.boot_time(); last=psutil.net_io_counters(); last_t=time.time()
@app.get("/api/snapshot")
def snapshot():
 global last,last_t
 now=time.time(); vm=psutil.virtual_memory(); net=psutil.net_io_counters(); dt=max(now-last_t,.001)
 rx=max(0,net.bytes_recv-last.bytes_recv)/dt; tx=max(0,net.bytes_sent-last.bytes_sent)/dt; last,last_t=net,now
 out=[]
 for p in psutil.process_iter(["pid","name","username","memory_info","num_threads","cmdline","status"]):
  try:
   i=p.info; cmd=" ".join(i.get("cmdline") or []); n=i.get("name") or "unknown"; s=(n+" "+cmd).lower()
   cat="DEV" if any(x in s for x in ("python","code","git","node","java")) else "NETWORK" if any(x in s for x in ("chrome","firefox","ssh")) else "DESKTOP" if any(x in s for x in ("windowserver","finder","dock")) else "SYSTEM"
   out.append({"pid":i["pid"],"name":n,"user":i.get("username") or "?","memory":i["memory_info"].rss if i.get("memory_info") else 0,"cpu":p.cpu_percent(None),"threads":i.get("num_threads") or 0,"status":i.get("status") or "?","cmd":cmd[:300],"category":cat})
  except (psutil.NoSuchProcess,psutil.AccessDenied,psutil.ZombieProcess): pass
 out.sort(key=lambda x:(x["memory"],x["cpu"]),reverse=True)
 return {"host":{"hostname":socket.gethostname(),"online":True,"cpu":psutil.cpu_percent(None),"memory_percent":vm.percent,"memory_used":vm.used,"memory_total":vm.total,"processes":len(out),"rx_per_sec":rx,"tx_per_sec":tx,"uptime":now-boot},"processes":out[:300],"timestamp":now}
if __name__=="__main__": uvicorn.run(app,host="0.0.0.0",port=8766)
