
const $=id=>document.getElementById(id);
const esc=s=>String(s??"").replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[m]));
const money=v=>(v===null||v===undefined||v==="")?"—":new Intl.NumberFormat("en-US",{style:"currency",currency:"USD",maximumFractionDigits:0}).format(Number(v));
async function j(n){return fetch(n+".json").then(r=>r.json())}

async function load(){
 const [meta,news,players,salary,standings,games,picks,take]=await Promise.all(["meta","news","players","salary","standings","games","picks","take"].map(j));
 $("updated").textContent=`UPDATED ${meta.updated_at_jst} JST`;
 const mavs=standings.teams.find(t=>t.abbr==="DAL")||{};
 $("hero-record").textContent=`${mavs.record||"—"}  ·  WEST ${mavs.rank||"—"}`;
 $("snapshot").innerHTML=[
  ["Record",mavs.record||"—"],["West Rank",mavs.rank?`#${mavs.rank}`:"—"],
  ["Roster",players.players.length],["2026-27 Allocations",money(salary.summary.total_allocations)]
 ].map(([a,b])=>`<div class="snap-row"><div class="snap-label">${esc(a)}</div><div class="snap-value">${esc(b)}</div></div>`).join("");

 $("news-grid").innerHTML=news.items.slice(0,7).map(n=>`<article class="news-card"><div class="news-source">${esc(n.source)}</div><a href="${esc(n.url)}" target="_blank" rel="noopener"><h3>${esc(n.title)}</h3></a><div class="news-meta">${esc(n.published)}</div></article>`).join("");

$("player-grid").innerHTML=players.players.map(p=>`<a class="player-card" href="${esc(p.slug)}.html"><div class="player-no">#${esc(p.number)}</div><div class="player-name">${esc(p.name)}</div><div class="player-meta">${esc(p.position)} · Age ${esc(p.age)}</div></a>`).join("");
 
 const usable=players.players.filter(p=>p.stats && p.stats.pts!=="—");
 const leaders=(usable.length?usable:players.players).slice().sort((a,b)=>(Number(b.stats.pts)||0)-(Number(a.stats.pts)||0)).slice(0,6);
 $("leaders").innerHTML=leaders.map(p=>`<div class="leader-row"><strong>${esc(p.name)}</strong><div class="leader-stat"><span>PTS</span><b>${esc(p.stats.pts)}</b></div><div class="leader-stat"><span>REB</span><b>${esc(p.stats.reb)}</b></div><div class="leader-stat"><span>AST</span><b>${esc(p.stats.ast)}</b></div></div>`).join("");

 $("games").innerHTML=games.items.length?games.items.map(g=>`<div class="game-row"><span>${esc(g.date)}</span><strong>${esc(g.opponent)}</strong><span class="${g.result==="W"?"win":"loss"}">${esc(g.result)} ${esc(g.score)}</span></div>`).join(""):`<div class="news-meta">Offseason — no recent games.</div>`;

 const max=Math.max(...salary.players.map(p=>p.cap_hit||0),1);
 $("salary-bars").innerHTML=salary.players.slice(0,12).map(p=>`<div class="bar-row"><div>${esc(p.name)}</div><div class="bar-track"><div class="bar-fill" style="width:${Math.round((p.cap_hit/max)*100)}%"></div></div><div class="bar-money">${money(p.cap_hit)}</div></div>`).join("");

 $("draft-grid").innerHTML=picks.years.map(y=>`<div class="draft-card"><div class="draft-year">${y.year}</div>${y.picks.map(p=>`<div class="pick"><span class="round">${esc(p.round)}</span>${esc(p.detail)}</div>`).join("")}</div>`).join("");
 $("take-text").textContent=take.text;$("take-date").textContent=take.date;
}
load().catch(e=>{console.error(e);$("updated").textContent="DATA ERROR";});
