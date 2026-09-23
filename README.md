# KI-Coding-Rangliste

Rangliste von KI-Modellen nach Coding-/Software-Engineering-Leistung. Top-Modelle mit öffentlichen Harness-Werten (SWE-bench Verified/Pro, mini-SWE-agent u. a.); der Rest ist interpoliert — **keine Benchmark-Behauptung**. Details in `00-HINWEISE.md`.

## Enthalten

| Datei | Inhalt |
| ----- | ------ |
| `build_db.py` | Erzeugt die SQLite-Rangliste lokal (`python build_db.py [anzahl]`, Standard 50000) |
| `rangliste_server.py` | Lokale Web-App: `python rangliste_server.py` → http://127.0.0.1:8765 |
| `sample-top1000.csv` | Top 1000 als Vorschau |
| `00-HINWEISE.md` | Methodik und Ehrlichkeits-Hinweise |

## Benutzung

```bash
python build_db.py 50000     # Datenbank bauen (35M dauert ~15-40 Min, ~5 GB)
python rangliste_server.py  # Browser: http://127.0.0.1:8765
```

Funktionen der Web-App: Endlos-Scrollen, Rang-Sprung, Modell-Suche.

## SQL-Beispiele

```sql
SELECT * FROM models ORDER BY rank LIMIT 10;
SELECT * FROM models WHERE model LIKE '%Astra%';
SELECT * FROM models WHERE rank BETWEEN 1000000 AND 1000100;
```

## Hinweis

Die große `.db`-Datei (GB-Bereich) ist absichtlich **nicht** im Repo (GitHub-Limit). Jeder baut sie lokal mit `build_db.py`.
