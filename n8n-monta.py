"""Cria/atualiza no N8N o robo 'Lumen — Dashboard de demandas (ao vivo)'.
Uso: N8N_KEY=... python3 n8n-monta.py [id-do-workflow-para-atualizar]"""
import json, os, sys, uuid, urllib.request
BASE = "https://n8neditor.paulamunhoz.online/api/v1"
NOTION = {"httpHeaderAuth": {"id": "ndfO3rfSmqBTAE0c", "name": "Header Auth account"}}
EQUIPE = {"7d0f5d3c-35b7-486d-a05d-95af9e295980": "Paula", "fa9edec2-6ba4-47b8-95d1-f0c77c8333a6": "Denise",
          "106d872b-594c-81cb-9c7e-000270eb9efb": "Ana", "373d872b-594c-8181-8113-0002836d2a4f": "Ju",
          "277d872b-594c-8128-8caa-0002579c6e8e": "Ricardo"}
PAG = {"pagination": {"pagination": {"paginationMode": "updateAParameterInEachRequest",
       "parameters": {"parameters": [{"type": "body", "name": "start_cursor", "value": "={{ $response.body.next_cursor }}"}]},
       "paginationCompleteWhen": "other", "completeExpression": "={{ !$response.body.has_more }}",
       "limitPagesFetched": True, "maxRequests": 15}}}
def notion(nome, ds, body, pos, once=False):
    n = {"parameters": {"method": "POST", "url": f"https://api.notion.com/v1/data_sources/{ds}/query",
         "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth", "sendHeaders": True,
         "headerParameters": {"parameters": [{"name": "Notion-Version", "value": "2025-09-03"}]},
         "sendBody": True, "specifyBody": "json", "jsonBody": json.dumps(body), "options": PAG},
         "name": nome, "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2, "position": pos,
         "id": str(uuid.uuid4()), "credentials": NOTION, "retryOnFail": True, "maxTries": 3, "waitBetweenTries": 1500}
    if once: n["executeOnce"] = True
    return n
filtro = {"and": [{"property": "Status", "status": {"does_not_equal": "Finalizado"}},
                  {"or": [{"property": "Responsável", "people": {"contains": i}} for i in EQUIPE]}]}
JS = r"""
const EQUIPE = %s;
const parse = (txt) => {
  if (txt == null) return null;
  const t = String(txt).trim().toLowerCase().replace(/,/g, '.');
  if (!t) return null;
  let m = t.match(/^(\d+(?:\.\d+)?)\s*(?:h|hr|hrs|hora|horas)\s*(?:e\s*)?(\d+)?\s*(?:m|min|mins|minuto|minutos)?$/);
  if (m) return parseFloat(m[1]) + (m[2] ? parseInt(m[2]) / 60 : 0);
  m = t.match(/^(\d+(?:\.\d+)?)\s*(?:m|min|mins|minuto|minutos)$/);
  if (m) return parseFloat(m[1]) / 60;
  m = t.match(/^(\d+):(\d{2})$/);
  if (m) return parseInt(m[1]) + parseInt(m[2]) / 60;
  if (/^\d+(?:\.\d+)?$/.test(t)) { const v = parseFloat(t); return v <= 8 ? v : v / 60; }
  return null;
};
const titulos = {};
for (const nome of ['Notion — clientes', 'Notion — projetos']) {
  for (const it of $(nome).all()) for (const p of (it.json.results || [])) {
    const tp = Object.values(p.properties).find(v => v.type === 'title');
    titulos[p.id] = tp ? tp.title.map(x => x.plain_text).join('').trim() : '';
  }
}
const txt = a => (a || []).map(x => x.plain_text).join('').trim();
const out = [];
for (const it of $('Notion — demandas').all()) for (const p of (it.json.results || [])) {
  const pr = p.properties;
  const r = pr['Responsável'].people.filter(u => EQUIPE[u.id]).map(u => EQUIPE[u.id]);
  const t = txt(pr['Atividade'].title);
  if (!r.length || !t) continue;
  const est = txt(pr['Estimativa'] ? pr['Estimativa'].rich_text : []);
  out.push({
    t, u: p.url, r,
    s: (pr['Status'].status || {}).name || 'Não começou',
    d: pr['Data'].date ? String(pr['Data'].date.start || '').slice(0, 10) : '',
    c: pr['Cliente'].relation.map(x => titulos[x.id] || '').filter(Boolean).join(', '),
    p: pr['Projetos'].relation.map(x => titulos[x.id] || '').filter(Boolean).join(', '),
    tipo: (pr['Tipo'].select || {}).name || '',
    pri: [...((pr['Prioridade'].select || {}).name || '')].length,
    h: parse(est), e: est,
  });
}
const agora = new Date().toLocaleString('pt-BR', { timeZone: 'America/Sao_Paulo', day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' }).replace(',', '');
return [{ json: { atualizado: agora, aoVivo: true, demandas: out } }];
""" % json.dumps(EQUIPE, ensure_ascii=False)
PATH = "demandas-equipe-ao-vivo-5127"
nodes = [
 {"parameters": {"httpMethod": "GET", "path": PATH, "responseMode": "responseNode", "options": {}},
  "name": "Webhook", "type": "n8n-nodes-base.webhook", "typeVersion": 2, "position": [0, 0], "webhookId": PATH, "id": str(uuid.uuid4())},
 notion("Notion — demandas", "b736e171-5362-8371-9c8b-87b4616803de", {"page_size": 100, "filter": filtro}, [220, 0]),
 notion("Notion — clientes", "c226e171-5362-83e0-94ab-07d8d1629dbf", {"page_size": 100}, [440, 0], once=True),
 notion("Notion — projetos", "b126e171-5362-82ff-8f7d-072b089c3c13", {"page_size": 100}, [660, 0], once=True),
 {"parameters": {"jsCode": JS}, "name": "Monta os dados", "type": "n8n-nodes-base.code", "typeVersion": 2, "position": [880, 0], "id": str(uuid.uuid4())},
 {"parameters": {"respondWith": "json", "responseBody": "={{ $json }}", "options": {"responseHeaders": {"entries": [
     {"name": "Access-Control-Allow-Origin", "value": "*"}, {"name": "Cache-Control", "value": "no-store"}]}}},
  "name": "Responde", "type": "n8n-nodes-base.respondToWebhook", "typeVersion": 1.1, "position": [1100, 0], "id": str(uuid.uuid4())},
]
ordem = [n["name"] for n in nodes]
conn = {a: {"main": [[{"node": b, "type": "main", "index": 0}]]} for a, b in zip(ordem, ordem[1:])}
wf = {"name": "Lumen — Dashboard de demandas (ao vivo)", "nodes": nodes, "connections": conn,
      "settings": {"executionOrder": "v1", "timezone": "America/Sao_Paulo", "saveDataSuccessExecution": "none"}}
def api(method, path, body=None):
    req = urllib.request.Request(BASE + path, method=method, data=json.dumps(body).encode() if body is not None else None,
          headers={"X-N8N-API-KEY": os.environ["N8N_KEY"], "Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r: return json.load(r)
if len(sys.argv) > 1:
    wid = sys.argv[1]; api("PUT", "/workflows/" + wid, wf)
else:
    wid = api("POST", "/workflows", wf)["id"]
api("POST", f"/workflows/{wid}/activate")
print(wid, "https://n8nwebhook.paulamunhoz.online/webhook/" + PATH)
