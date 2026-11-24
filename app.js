const GRUPO={"Em andamento":"exec","Ajustes":"exec","Em revisão (Lumen)":"exec",
  "Aguardando terceiros":"wait","Pendente de Resposta (cliente)":"wait","Acompanhar":"wait",
  "Não começou":"todo","Backlog":"todo"};
const GNOME={exec:"Em execução",wait:"Esperando alguém",todo:"Não começou"};
const DIA=8; // horas de trabalho num dia, usado no alerta
const ORDEM=["Paula","Denise","Ana","Ju","Ricardo"];
const $=id=>document.getElementById(id);
const esc=s=>String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const fh=h=>{if(!h)return "0min";if(h<1){return Math.max(5,Math.round(h*60/5)*5)+"min"}return (Math.round(h*10)/10).toLocaleString("pt-BR")+"h"};
const iso=d=>d.getFullYear()+"-"+String(d.getMonth()+1).padStart(2,"0")+"-"+String(d.getDate()).padStart(2,"0");
const hoje=new Date(), HOJE=iso(hoje);
const sex=new Date(hoje); sex.setDate(hoje.getDate()+((5-hoje.getDay()+7)%7)); const SEXTA=iso(sex);
const fd=d=>d?d.slice(8,10)+"/"+d.slice(5,7):"sem prazo";
let D=[], sel="";

fetch("data.json?"+Date.now()).then(r=>r.json()).then(j=>{
  D=j.demandas.map(x=>({...x,h:x.s==="Acompanhar"?0:x.h,g:GRUPO[x.s]||"todo",late:!!x.d&&x.d<HOJE,hoje:x.d===HOJE,week:!!x.d&&x.d<=SEXTA}));
  $("upd").textContent="Atualizado em "+j.atualizado+" · fonte: Atividades no Notion";
  montaFiltros(); desenha();
}).catch(()=>{$("upd").textContent="Não foi possível carregar os dados."});

function montaFiltros(){
  $("fP").innerHTML='<option value="">Todas as pessoas</option>'+ORDEM.map(p=>`<option>${p}</option>`).join("");
  $("fS").innerHTML='<option value="">Todos os status</option>'+Object.entries(GNOME).map(([k,v])=>`<option value="${k}">${v}</option>`).join("");
  const cl=[...new Set(D.map(x=>x.c).filter(Boolean))].sort((a,b)=>a.localeCompare(b,"pt"));
  $("fC").innerHTML='<option value="">Todos os clientes</option><option value="-">Interno (sem cliente)</option>'+cl.map(c=>`<option>${esc(c)}</option>`).join("");
  ["fP","fS","fC","fQ","fL"].forEach(id=>$(id).addEventListener("input",()=>{sel=$("fP").value;desenha()}));
}

function desenha(){
  const semH=D.filter(x=>x.h==null).length;
  const tot=D.reduce((a,x)=>a+(x.h||0),0);
  $("kpis").innerHTML=[
    [D.length,"demandas abertas"],
    [fh(tot),"horas estimadas no total"],
    [fh(D.filter(x=>x.late).reduce((a,x)=>a+(x.h||0),0)),D.filter(x=>x.late).length+" demandas atrasadas","alert"],
    [fh(D.filter(x=>x.hoje).reduce((a,x)=>a+(x.h||0),0)),"com prazo hoje"],
    [fh(D.filter(x=>x.week).reduce((a,x)=>a+(x.h||0),0)),"vencem até sexta"],
    [semH,"sem estimativa"]
  ].map(k=>`<div class="kpi ${k[2]||""}"><b>${k[0]}</b><span>${k[1]}</span></div>`).join("");

  const P=ORDEM.map(p=>{
    const it=D.filter(x=>x.r.includes(p));
    const hp=x=>x.r[0]===p?(x.h||0):0;
    const g={exec:0,wait:0,todo:0}; it.forEach(x=>g[x.g]+=hp(x));
    return {p,n:it.length,h:it.reduce((a,x)=>a+hp(x),0),g,
      wk:it.filter(x=>x.week).reduce((a,x)=>a+hp(x),0),late:it.filter(x=>x.late).length,lateH:it.filter(x=>x.late).reduce((a,x)=>a+hp(x),0),hojeN:it.filter(x=>x.hoje).length,hojeH:it.filter(x=>x.hoje).reduce((a,x)=>a+hp(x),0),sem:it.filter(x=>x.h==null).length};
  });
  const maxWk=Math.max(1,...P.map(x=>x.wk));
  $("people").innerHTML=P.map(x=>{
    const t=x.h||1;
    return `<button class="person ${sel===x.p?"on":""}" data-p="${x.p}">
      <div class="nm">${x.p}<small>${x.n} demandas</small></div>
      <div class="hrs">${fh(x.h)} <small>em aberto</small></div>
      <div class="bar"><i style="width:${x.g.exec/t*100}%;background:var(--exec)"></i><i style="width:${x.g.wait/t*100}%;background:var(--wait)"></i><i style="width:${x.g.todo/t*100}%;background:var(--todo)"></i></div>
      <div class="today ${x.lateH+x.hojeH>DIA?"over":""}">
        <div class="lb">Para hoje</div>
        <div class="big">${fh(x.lateH+x.hojeH)}</div>
        <div class="parts">Atrasadas <b>${fh(x.lateH)}</b> (${x.late}) + hoje <b>${fh(x.hojeH)}</b> (${x.hojeN})</div>
        ${x.lateH+x.hojeH>DIA?`<div class="warn">Passa de ${DIA}h num dia: realocar datas</div>`:""}
      </div>
      <div class="week">Vence até sexta: <b>${fh(x.wk)}</b><div class="wk"><i style="width:${x.wk/maxWk*100}%"></i></div></div>
      <div class="chips">${x.sem?`<span class="chip">${x.sem} sem estimativa</span>`:""}</div>
    </button>`}).join("");
  document.querySelectorAll(".person").forEach(b=>b.onclick=()=>{sel=sel===b.dataset.p?"":b.dataset.p;$("fP").value=sel;desenha()});

  const hr=x=>sel&&x.r[0]!==sel?0:x.h;
  const q=$("fQ").value.trim().toLowerCase(), s=$("fS").value, c=$("fC").value, L=$("fL").value;
  const rows=D.filter(x=>(!sel||x.r.includes(sel))&&(!s||x.g===s)&&(!c||(c==="-"?!x.c:x.c===c))&&(!L||(L==='a'?x.late:L==='h'?x.hoje:(x.late||x.hoje)))&&(!q||(x.t+" "+x.c+" "+x.p).toLowerCase().includes(q)))
    .sort((a,b)=>(a.d||"9999").localeCompare(b.d||"9999")||b.pri-a.pri);
  $("count").textContent=rows.length+" demanda"+(rows.length===1?"":"s")+" · "+fh(rows.reduce((a,x)=>a+(hr(x)||0),0))+" estimadas"+(sel?" para "+sel:"");
  $("tbl").innerHTML='<div class="row head"><div>Demanda</div><div>Responsável</div><div>Status</div><div>Prazo</div><div class="num">Estim.</div></div>'+
    (rows.length?rows.map(x=>`<div class="row">
      <div><a href="${esc(x.u)}" target="_blank" rel="noopener">${esc(x.t)}</a><div class="meta">${esc(x.r[0]+(x.r.length>1?" (executa) + "+x.r.slice(1).join(" + "):""))}${x.c?" · "+esc(x.c):""}${x.tipo?" · "+esc(x.tipo):""}</div></div>
      <div>${esc(x.r.join(" + "))}</div>
      <div><span class="st ${x.g}">${esc(x.s)}</span></div>
      <div class="${x.late?"late":""}">${fd(x.d)}${x.late?" · atrasada":""}</div>
      <div class="num">${hr(x)==null?"—":fh(hr(x))}${sel&&x.r[0]!==sel?'<div class="meta">só acompanha</div>':""}</div></div>`).join(""):'<div class="empty">Nenhuma demanda com esse filtro.</div>');
}
