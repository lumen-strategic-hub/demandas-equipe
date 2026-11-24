import json, urllib.request, os, sys
TOKEN = os.environ["NOTION_TOKEN"]
DS = "b736e171-5362-8371-9c8b-87b4616803de"
H = {"Authorization": f"Bearer {TOKEN}", "Notion-Version": "2025-09-03", "Content-Type": "application/json"}
def call(method, path, body=None):
    req = urllib.request.Request("https://api.notion.com/v1" + path, method=method, headers=H,
                                 data=json.dumps(body).encode() if body is not None else None)
    with urllib.request.urlopen(req) as r:
        return json.load(r)
def todas():
    out, cur = [], None
    while True:
        b = {"page_size": 100, "filter": {"property": "Status", "status": {"does_not_equal": "Finalizado"}}}
        if cur: b["start_cursor"] = cur
        r = call("POST", f"/data_sources/{DS}/query", b)
        out += r["results"]
        if not r.get("has_more"): return out
        cur = r["next_cursor"]
if __name__ == "__main__":
    pages = todas()
    json.dump(pages, open(sys.argv[1], "w"), ensure_ascii=False)
    users = call("GET", "/users?page_size=100")
    for u in users["results"]:
        print(u["id"], u.get("type"), u.get("name"))
    print(len(pages), "abertas")
    print(list(pages[0]["properties"].keys()))
