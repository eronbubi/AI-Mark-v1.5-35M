import json, pathlib, sqlite3, urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
DB = str(pathlib.Path.home() / "Desktop" / "Rangliste-35M.db")
con = sqlite3.connect(DB, check_same_thread=False)
con.execute("PRAGMA query_only=ON")
DEVS = ["Anthropic","OpenAI","Google","DeepSeek","Alibaba","Meta","Mistral","xAI","Microsoft",
 "Z.ai","Moonshot AI","MiniMax","NVIDIA","IBM","Cohere","BigCode","01.AI","TII","Mosaic",
 "Databricks","AI21","Amazon","Tencent","Baidu","InternLM","Baichuan","Stability",
 "Community/Org-Finetune","Community","Diverse"]
BRAND = {
 "Anthropic":("A","#CC785C"),"OpenAI":("O","#111111"),"Google":("G","#4285F4"),
 "DeepSeek":("D","#4D6BFE"),"Alibaba":("Q","#FF6A00"),"Meta":("M","#0668E1"),
 "Mistral":("M","#FF7000"),"xAI":("X","#000000"),"Microsoft":("M","#00A4EF"),
 "Z.ai":("Z","#3E63DD"),"Moonshot AI":("K","#222222"),"MiniMax":("M","#7C3AED"),
 "NVIDIA":("N","#76B900"),"IBM":("I","#0F62FE"),"Cohere":("C","#39594D"),
 "BigCode":("S","#009688"),"01.AI":("Y","#9333EA"),"TII":("F","#0EA5E9"),
 "Mosaic":("M","#6366F1"),"Databricks":("D","#FF3621"),"AI21":("J","#059669"),
 "Amazon":("N","#FF9900"),"Tencent":("H","#0052D9"),"Baidu":("E","#2932E1"),
 "InternLM":("I","#0891B2"),"Baichuan":("B","#DC2626"),"Stability":("S","#8B5CF6"),
 "Community/Org-Finetune":("C","#64748B"),"Community":("C","#64748B"),"Diverse":("D","#64748B"),
}
def badge(dev):
    ch, col = BRAND.get(dev, ("?", "#64748B"))
    return (f"<span title='{dev}' style='display:inline-flex;align-items:center;justify-content:center;"
            f"width:26px;height:26px;border-radius:7px;background:{col};color:#fff;"
            f"font-weight:700;font-size:13px;margin-right:8px;vertical-align:middle'>{ch}</span>")
HTML = """<!DOCTYPE html><html lang="de"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Rangliste 35M Browser</title>
<style>
:root{--bg:#0f172a;--card:#1e293b;--line:#334155;--txt:#e2e8f0;--mut:#94a3b8;--acc:#38bdf8}
*{box-sizing:border-box}body{font-family:'Segoe UI',Arial,sans-serif;margin:0;background:var(--bg);color:var(--txt)}
header{padding:20px 24px 8px}header h1{margin:0 0 4px;font-size:24px}header p{margin:0;color:var(--mut);font-size:13px}
.top{display:flex;gap:10px;overflow-x:auto;padding:12px 24px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:10px 14px;min-width:190px}
.card .rk{font-size:12px;color:var(--mut)}.card .nm{font-weight:700;margin:4px 0}.card .sc{color:var(--acc);font-variant-numeric:tabular-nums}
.bar{position:sticky;top:0;background:var(--bg);padding:10px 24px;border-bottom:1px solid var(--line);display:flex;gap:8px;flex-wrap:wrap;align-items:center;z-index:5}
input,select,button{padding:7px 10px;border-radius:8px;border:1px solid var(--line);background:var(--card);color:var(--txt)}
button{cursor:pointer;background:#0369a1;border-color:#0369a1}button:hover{background:#0284c7}
table{border-collapse:collapse;width:calc(100% - 48px);margin:12px 24px}
th,td{border-bottom:1px solid var(--line);padding:7px 10px;text-align:left}th{color:var(--mut);font-size:12px;text-transform:uppercase}
tr:hover td{background:#16213a}.pill{display:inline-block;padding:2px 10px;border-radius:20px;font-size:12px}
.Frontier{background:#7c2d12}.High{background:#14532d}.Mid{background:#1e3a8a}.Low{background:#3b0764}.Minimal{background:#27272a}
.num{font-variant-numeric:tabular-nums}#st{color:var(--mut);font-size:13px}.spin{display:inline-block;animation:sp 1s linear infinite}
@keyframes sp{to{transform:rotate(360deg)}}
</style></head><body>
<header><h1>KI-Coding-Rangliste · 35.000.000 Modelle</h1>
<p>Nur Top-Modelle haben öffentliche Harness-Werte; Rest interpoliert, keine Benchmark-Behauptung. Sortierung rein nach Coding-Leistung.</p></header>
<div class="top" id="top"></div>
<div class="bar">
<input id="q" type="text" placeholder="Modell suchen … (Enter)" style="min-width:220px">
<select id="dev"><option value="">Alle Firmen</option></select>
<select id="lvl"><option value="">Alle Level</option><option>Frontier</option><option>High</option><option>Mid</option><option>Low</option><option>Minimal</option></select>
<button id="find">Suchen</button><button id="reset">Zurück zur Liste</button>
<span>Rang <input id="jump" type="number" min="1" style="width:110px"> <button id="go">OK</button></span>
<span id="st"></span>
</div>
<table><thead><tr><th>Rang</th><th>Modell</th><th>Score /1 Bio.</th><th>Level</th></tr></thead>
<tbody id="tb"></tbody></table><div id="more" style="height:80px"></div>
<script>
const DEVS=__DEVS__,BRAND=__BRAND__;
const tb=document.getElementById("tb"),st=document.getElementById("st");
const devSel=document.getElementById("dev");
DEVS.forEach(d=>{const o=document.createElement("option");o.value=d;o.textContent=d;devSel.appendChild(o);});
function fmt(n){return n.toLocaleString("de-DE",{minimumFractionDigits:3,maximumFractionDigits:3});}
function badge(d){const b=BRAND[d]||["?","#64748B"];
 return "<span title='"+d+"' style='display:inline-flex;align-items:center;justify-content:center;width:26px;height:26px;border-radius:7px;background:"+b[1]+";color:#fff;font-weight:700;font-size:13px;margin-right:8px;vertical-align:middle'>"+b[0]+"</span>";}
let mode="list",start=0,term="",fdev="",flvl="";const STEP=200;
async function api(p){return fetch(p).then(r=>r.json());}
function rows(h,R){for(const m of R)h+="<tr id='r"+m[0]+"'><td>"+m[0].toLocaleString("de-DE")+"</td><td>"+badge(m[2])+"<b>"+m[1]+"</b><br><small style='color:#94a3b8'>"+m[2]+"</small></td><td class='num'>"+fmt(m[3])+"</td><td><span class='pill "+m[4]+"'>"+m[4]+"</span></td></tr>";return h;}
async function loadMore(){if(mode!=="list")return;const r=await api("/api/rows?start="+start+"&n="+STEP);
 tb.insertAdjacentHTML("beforeend",rows("",r.rows));start+=r.rows.length;st.textContent="Geladen bis Rang "+start.toLocaleString("de-DE")+" / 35.000.000";}
async function showTop(){const r=await api("/api/rows?start=0&n=7");let h="";
 for(const m of r.rows)h+="<div class='card'><div class='rk'>#"+m[0]+" · "+m[4]+"</div><div class='nm'>"+badge(m[2])+m[1]+"</div><div class='sc'>"+fmt(m[3])+"</div></div>";
 document.getElementById("top").innerHTML=h;}
async function doSearch(){term=document.getElementById("q").value.trim();fdev=devSel.value;flvl=document.getElementById("lvl").value;
 if(!term&&!fdev&&!flvl){resetList();return;}mode="search";tb.innerHTML="";st.innerHTML="<span class='spin'>⏳</span> Suche …";
 const r=await api("/api/search?q="+encodeURIComponent(term)+"&dev="+encodeURIComponent(fdev)+"&lvl="+encodeURIComponent(flvl));
 tb.innerHTML=rows("",r.rows);st.textContent=r.rows.length+" Treffer · "+r.ms+" ms"+(r.partial?" · Teilsuche (Prefix, Indexed)":"");}
function resetList(){mode="list";start=0;tb.innerHTML="";loadMore();}
new IntersectionObserver(e=>{if(e[0].isIntersecting)loadMore();}).observe(document.getElementById("more"));
document.getElementById("find").onclick=doSearch;
document.getElementById("q").onkeydown=e=>{if(e.key==="Enter")doSearch();};
document.getElementById("reset").onclick=()=>{document.getElementById("q").value="";devSel.value="";document.getElementById("lvl").value="";resetList();};
document.getElementById("go").onclick=async()=>{const rk=Math.max(1,+document.getElementById("jump").value||1);
 mode="list";tb.innerHTML="";const r=await api("/api/rows?start="+(rk-1)+"&n="+STEP);
 tb.innerHTML=rows("",r.rows);start=rk-1+r.rows.length;document.getElementById("r"+rk).scrollIntoView();};
showTop();loadMore();
</script></body></html>"""
HTML = HTML.replace("__DEVS__", json.dumps(DEVS)).replace("__BRAND__", json.dumps(BRAND))
class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass
    def _send(self, obj, ctype):
        b = obj.encode() if isinstance(obj, str) else obj
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)
    def do_GET(self):
        import time
        u = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(u.query)
        if u.path == "/":
            self._send(HTML, "text/html; charset=utf-8")
        elif u.path == "/api/rows":
            s = max(0, int(q.get("start", ["0"])[0]))
            n = min(1000, int(q.get("n", ["200"])[0]))
            rows = con.execute("SELECT rank,model,dev,score,level FROM models WHERE rank>? ORDER BY rank LIMIT ?", (s, n)).fetchall()
            self._send(json.dumps({"rows": rows}), "application/json")
        elif u.path == "/api/search":
            t0 = time.time()
            term = q.get("q", [""])[0][:60].strip()
            dev = q.get("dev", [""])[0]
            lvl = q.get("lvl", [""])[0]
            cond, par = [], []
            if dev:
                cond.append("dev=?"); par.append(dev)
            if lvl:
                cond.append("level=?"); par.append(lvl)
            rows, partial = [], False
            if term:
                # 1) Prefix per Index (schnell)
                c2, p2 = cond + ["model>=?", "model<?"], par + [term, term + "\uffff"]
                rows = con.execute(f"SELECT rank,model,dev,score,level FROM models WHERE {' AND '.join(c2)} ORDER BY rank LIMIT 500", p2).fetchall()
                # 2) Falls wenig Treffer: Substring-Nachsuche (kann Sekunden dauern)
                if len(rows) < 200:
                    partial = True
                    ids = {r[0] for r in rows}
                    more = con.execute(f"SELECT rank,model,dev,score,level FROM models WHERE {' AND '.join(cond + ['model LIKE ?'])} ORDER BY rank LIMIT 500", par + [f"%{term}%"]).fetchall()
                    rows = sorted(rows + [r for r in more if r[0] not in ids], key=lambda r: r[0])[:500]
            else:
                rows = con.execute(f"SELECT rank,model,dev,score,level FROM models WHERE {' AND '.join(cond)} ORDER BY rank LIMIT 500", par).fetchall()
            ms = int((time.time() - t0) * 1000)
            self._send(json.dumps({"rows": rows, "ms": ms, "partial": partial}), "application/json")
        else:
            self.send_error(404)
HTTPServer(("127.0.0.1", 8765), H).serve_forever()
