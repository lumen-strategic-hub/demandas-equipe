"""Gera data.json do dashboard a partir da base Atividades do Notion.
Uso: NOTION_TOKEN=... python3 gera.py"""
import json, datetime
from puxa import call, todas
from tempo import parse
EQUIPE = {
 "7d0f5d3c-35b7-486d-a05d-95af9e295980": "Paula",
 "fa9edec2-6ba4-47b8-95d1-f0c77c8333a6": "Denise",
 "106d872b-594c-81cb-9c7e-000270eb9efb": "Ana",
 "373d872b-594c-8181-8113-0002836d2a4f": "Ju",
 "277d872b-594c-8128-8caa-0002579c6e8e": "Ricardo",
}
cache = {}
def titulo(pid):
    if pid not in cache:
        try:
            pg = call("GET", "/pages/" + pid)
            cache[pid] = next("".join(x["plain_text"] for x in v["title"]) for v in pg["properties"].values() if v["type"] == "title").strip()
        except Exception:
            cache[pid] = ""
    return cache[pid]
out = []
for p in todas():
    pr = p["properties"]
    resp = [EQUIPE[u["id"]] for u in pr["Responsável"]["people"] if u["id"] in EQUIPE]
    t = "".join(x["plain_text"] for x in pr["Atividade"]["title"]).strip()
    if not resp or not t:
        continue
    est = "".join(x["plain_text"] for x in pr["Estimativa"]["rich_text"]).strip()
    out.append({
        "t": t, "u": p["url"], "r": resp,
        "s": (pr["Status"]["status"] or {}).get("name") or "Não começou",
        "d": (pr["Data"]["date"] or {}).get("start", "")[:10] if pr["Data"]["date"] else "",
        "c": ", ".join(titulo(r["id"]) for r in pr["Cliente"]["relation"]),
        "p": ", ".join(titulo(r["id"]) for r in pr["Projetos"]["relation"]),
        "tipo": (pr["Tipo"]["select"] or {}).get("name") or "",
        "pri": len((pr["Prioridade"]["select"] or {}).get("name") or ""),
        "h": parse(est), "e": est,
    })
agora = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3)))
json.dump({"atualizado": agora.strftime("%d/%m/%Y %H:%M"), "demandas": out}, open("data.json", "w"), ensure_ascii=False)
print(len(out), "demandas;", sum(1 for x in out if x["h"] is None), "sem estimativa")
