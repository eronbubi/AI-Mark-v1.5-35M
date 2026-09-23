import sqlite3, random, pathlib, sys, csv
TOTAL = int(sys.argv[1]) if len(sys.argv) > 1 else 50000
DB = pathlib.Path("rangliste.db")
if DB.exists():
    DB.unlink()
con = sqlite3.connect(DB)
cur = con.cursor()
cur.execute("PRAGMA journal_mode=OFF")
cur.execute("PRAGMA synchronous=OFF")
cur.execute("PRAGMA cache_size=100000")
cur.execute("CREATE TABLE meta(k TEXT PRIMARY KEY, v TEXT)")
cur.execute("""CREATE TABLE models(
 rank INTEGER PRIMARY KEY, model TEXT NOT NULL, dev TEXT NOT NULL,
 score REAL NOT NULL, level TEXT NOT NULL)""")
cur.execute("""INSERT INTO meta VALUES
 ('hinweis','Nur Top-Modelle haben oeffentliche Harness-Werte (SWE-bench Verified/Pro, mini-SWE-agent u.a.). Rest interpoliert, keine Benchmark-Behauptung. Ab ca. Rang 2500 Variantenmuster realer Familien-Basen. Skala: Score /1 Bio. Sortierung rein nach Coding-Leistung, Preis ignoriert.'),
 ('skala','Score /1000000000000 mit 3 Dezimalstellen'),
 ('count','35000000')""")
# Top-7 kuratiert
top = [
 ("Claude Opus 5.5","Anthropic",1000000000000.0,"Frontier"),
 ("Claude Fable 5.1","Anthropic",996600000000.0,"Frontier"),
 ("GPT-6 Astra Codex","OpenAI",989500000000.0,"Frontier"),
 ("GPT-6 Astra","OpenAI",987300000000.0,"Frontier"),
 ("Claude Opus 5","Anthropic",984200000000.0,"Frontier"),
 ("Kimi K3","Moonshot AI",979400000000.0,"Frontier"),
 ("GPT-5.6 Sol","OpenAI",520000000000.0,"Frontier"),
]
r = 1
for m, d, s, l in top:
    cur.execute("INSERT INTO models VALUES(?,?,?,?,?)", (r, m, d, s, l))
    r += 1
# Kern-Basen aus der 500K-CSV (kurze Namen)
import csv
# Kern-Basen: zuerst lokale CSV nutzen (falls vorhanden), sonst eingebaute Liste
FALLBACK = [
 ("Claude Opus 5","Anthropic"),("Claude Opus 4.5","Anthropic"),("Claude Opus 4.1","Anthropic"),
 ("Claude Sonnet 4.5","Anthropic"),("Claude Sonnet 4","Anthropic"),("Claude Haiku 4.5","Anthropic"),
 ("Claude Fable 5","Anthropic"),("GPT-5.2 Codex","OpenAI"),("GPT-5.1 Codex","OpenAI"),("GPT-5","OpenAI"),
 ("GPT-4o","OpenAI"),("GPT-4.1","OpenAI"),("o3","OpenAI"),("o1","OpenAI"),("o4-mini","OpenAI"),
 ("Gemini 3 Pro","Google"),("Gemini 3 Flash","Google"),("Gemini 2.5 Pro","Google"),("Gemini 2.5 Flash","Google"),
 ("Gemini 2.0 Flash","Google"),("Gemma 3 27B","Google"),("Gemma 2 9B","Google"),("CodeGemma 7B","Google"),
 ("DeepSeek V3","DeepSeek"),("DeepSeek R1","DeepSeek"),("DeepSeek Coder 33B","DeepSeek"),("DeepSeek Coder 6.7B","DeepSeek"),
 ("Qwen3 32B","Alibaba"),("Qwen3 8B","Alibaba"),("Qwen2.5 72B","Alibaba"),("Qwen2.5 32B","Alibaba"),
 ("Qwen2.5 7B","Alibaba"),("Qwen2.5-Coder 32B","Alibaba"),("Qwen2.5-Coder 7B","Alibaba"),("Qwen2 72B","Alibaba"),
 ("Llama 3.3 70B","Meta"),("Llama 3.1 405B","Meta"),("Llama 3.1 70B","Meta"),("Llama 3.1 8B","Meta"),
 ("Code Llama 70B","Meta"),("Code Llama 7B","Meta"),("Mixtral 8x22B","Mistral"),("Mixtral 8x7B v0.1","Mistral"),
 ("Mistral Large 2","Mistral"),("Mistral Small 24B","Mistral"),("Codestral 22B","Mistral"),("Devstral 24B","Mistral"),
 ("Phi-4 14B","Microsoft"),("Phi-3 mini","Microsoft"),("WizardCoder 15B","Microsoft"),
 ("Grok 4","xAI"),("Grok 3","xAI"),("Grok Code Fast","xAI"),
 ("GLM-4.5","Z.ai"),("GLM-4","Z.ai"),("CodeGeeX4 9B","Z.ai"),
 ("Kimi K2","Moonshot AI"),("MiniMax M2","MiniMax"),
 ("Command R+","Cohere"),("Command A","Cohere"),("Command R7B","Cohere"),
 ("Granite 34B Code","IBM"),("Granite 8B Code","IBM"),
 ("StarCoder2 15B","BigCode"),("StarCoder 15.5B","BigCode"),("SantaCoder 1.1B","BigCode"),
 ("Yi Coder 9B","01.AI"),("Yi 34B","01.AI"),
 ("Falcon 180B","TII"),("Falcon 7B","TII"),("MPT 30B","Mosaic"),("DBRX Instruct","Databricks"),
 ("Jamba 1.5 Large","AI21"),("Nova Pro","Amazon"),("Hunyuan Large","Tencent"),("ERNIE 4.0","Baidu"),
 ("InternLM2 20B","InternLM"),("Baichuan2 13B","Baichuan"),("Stable Code 3B","Stability"),
 ("Nemotron 70B","NVIDIA"),("NVLM 72B","NVIDIA"),("Vicuna 13B","Community"),("OpenHermes 7B","Community"),
]
core, seen0, dev_of = [], set(), {}
try:
    with open("coding-rangliste/gesamt-2000plus.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            dev_of[row["Modell"]] = row["Entwickler"]
            n0 = row["Modell"]
            if len(core) < 1500 and len(n0) < 45 and n0 not in seen0:
                seen0.add(n0)
                core.append(n0)
except FileNotFoundError:
    pass
if not core:
    for n0, d0 in FALLBACK:
        core.append(n0)
        dev_of[n0] = d0
del seen0
C, T = len(core), None
tasks = ["Code","Chat","Instruct","SFT","DPO","RLHF","Reasoning","Reasoning-High","Agentic","Agent-SWE",
 "ToolUse","LongCtx","LongCtx-1M","FIM","Infilling","Repair","Refactor","TestGen","DocGen","SQL","API","Web",
 "Debug","Review","Merge","Commit","Issue","PR","Terminal","Repo","Multifile","Shell","FunctionCall","Vision","Math"]
vers = ["v1","v1.1","v1.2","v1.5","v2","v2.1","v2.5","v3","v4","2021","2022","2023","2024","2025","2026",
 "Q1","Q2","Q3","Q4","Alpha","Beta","RC1","Final","Turbo","Lite","Pro","Ultra","Edge","Core","Neo"]
langs = ["DE","EN","FR","ES","ZH","JA","AR","HI","PT","RU","IT","NL","PL","TR","KO","SV","NO","DA","FI","CS","EL","HE","TH","VI"]
T, V, L = len(tasks), len(vers), len(langs)
print("core:", len(core), "ziel:", TOTAL)
topnames = set(m for m, _, _, _ in top)
batch, B = [], 10000
made = 0
i = 0
def dev_for(b):
    return dev_of.get(b, "Community/Org-Finetune")
# deterministischer Score: streng fallend
def score_for(k):
    return 510000000000.0 - k * 14500.0 - ((k * 2654435761) % 5000)
while made < TOTAL - 7:
    b = core[i % C]
    t = tasks[(i // C) % T]
    v = vers[(i // (C * T)) % V]
    l = langs[(i // 13) % L]
    w = (i // (C * T * V)) % 400
    name = f"{b} {t} {v} {l} R{w}" if w else f"{b} {t} {v} {l}"
    i += 1
    if name in topnames:
        continue
    if len(name) > 130:
        continue
    k = made
    sc = round(score_for(k), 3)
    lvl = "Minimal" if sc < 8000000000.0 else ("Low" if sc < 30000000000.0 else ("Mid" if sc < 200000000000.0 else "High"))
    batch.append((r, name, dev_for(b), sc, lvl))
    r += 1
    made += 1
    if len(batch) >= B:
        cur.executemany("INSERT INTO models VALUES(?,?,?,?,?)", batch)
        batch = []
        if made % 1000000 == 0:
            con.commit()
            print(f"{made} ...", flush=True)
if batch:
    cur.executemany("INSERT INTO models VALUES(?,?,?,?,?)", batch)
con.commit()
print("index ...", flush=True)
cur.execute("CREATE INDEX idx_model ON models(model)")
cur.execute("CREATE INDEX idx_score ON models(score DESC)")
con.commit()
n = cur.execute("SELECT COUNT(*) FROM models").fetchone()[0]
print("fertig:", n)
con.close()
