import json, pathlib, sqlite3, urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
DB = str(pathlib.Path("rangliste.db").resolve())
con = sqlite3.connect(DB, check_same_thread=False)
con.execute("PRAGMA query_only=ON")
HTML = """<!DOCTYPE html><html lang="de"><head><meta charset="utf-8">
<title>Rangliste 35M Browser</title>
<style>body{font-family:Arial,sans-serif;margin:16px}table{border-collapse:collapse;width:100%}
th,td{border:1px solid #ccc;padding:4px 8px;text-align:left}th{background:#eee;position:sticky;top:0}
.bar{position:sticky;top:0;background:#fff;padding:8px 0}input{padding:4px}</style></head><body>
<h1>KI-Coding-Rangliste: 35.000.000 Modelle</h1>
<div class="bar">Rang <input id="jump" type="number" min="1" style="width:110px"> <button id="go">Springen</button>
&nbsp; Suche <input id="q" type="text" placeholder="Modellname"> <button id="find">Suchen</button>
&nbsp; <span id="st"></span></div>
<table><thead><tr><th>Rang</th><th>Modell</th><th>Entwickler</th><th>Score</th><th>Level</th></tr></thead>
<tbody id="tb"></tbody></table><div id="more" style="height:80px"></div>
<script>
let start=0;const N=500,NSTEP=200;const tb=document.getElementById("tb"),st=document.getElementById("st");
async function load(s){const r=await fetch("/api/rows?start="+s+"&n="+NSTEP).then(r=>r.json());
 let h="";for(const m of r.rows)h+="<tr id='r"+m[0]+"'><td>"+m[0]+"</td><td>"+m[1]+"</td><td>"+m[2]+"</td><td>"+m[3].toFixed(3)+"</td><td>"+m[4]+"</td></tr>";
 tb.insertAdjacentHTML("beforeend",h);start=s+r.rows.length;st.textContent="Geladen bis Rang "+start+" / 35000000";}
async function jump(rk){tb.innerHTML="";await load(rk-1);document.getElementById("r"+rk).scrollIntoView();}
new IntersectionObserver(e=>{if(e[0].isIntersecting)load(start);}).observe(document.getElementById("more"));
document.getElementById("go").onclick=()=>jump(Math.max(1,+document.getElementById("jump").value||1));
document.getElementById("find").onclick=async()=>{const q=document.getElementById("q").value;if(!q)return;
 const r=await fetch("/api/search?q="+encodeURIComponent(q)).then(r=>r.json());
 if(!r.rows.length){alert("Nichts gefunden");return;}tb.innerHTML="";
 let h="";for(const m of r.rows)h+="<tr><td>"+m[0]+"</td><td>"+m[1]+"</td><td>"+m[2]+"</td><td>"+m[3].toFixed(3)+"</td><td>"+m[4]+"</td></tr>";
 tb.innerHTML=h;st.textContent=r.rows.length+" Treffer (max 500)";};
load(0);
</script></body></html>"""
class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass
    def _send(self, body, ctype):
        b = body.encode() if isinstance(body, str) else body
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)
    def do_GET(self):
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
            term = q.get("q", [""])[0][:60]
            rows = con.execute("SELECT rank,model,dev,score,level FROM models WHERE model LIKE ? ORDER BY rank LIMIT 500", (f"%{term}%",)).fetchall()
            self._send(json.dumps({"rows": rows}), "application/json")
        else:
            self.send_error(404)
HTTPServer(("127.0.0.1", 8765), H).serve_forever()
