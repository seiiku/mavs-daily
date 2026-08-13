
const $=id=>document.getElementById(id);
const esc=s=>String(s??"").replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[m]));
const money=v=>(v===null||v===undefined||v==="")?"—":new Intl.NumberFormat("ja-JP",{style:"currency",currency:"USD",maximumFractionDigits:0}).format(Number(v));
const slug=s=>String(s).toLowerCase().replace(/[^a-z0-9]+/g,"-").replace(/^-|-$/g,"");
async function j(n){const r=await fetch("./"+n+".json",{cache:"no-store"});if(!r.ok)throw new Error(n+" "+r.status);return r.json();}

function formatDate(s){
  if(!s) return "日付不明";
  const d=new Date(s);
  if(Number.isNaN(d.getTime())) return s;
  return `${d.getFullYear()}年${d.getMonth()+1}月${d.getDate()}日`;
}

async function load(){
 const [meta,news,roster,stats,salary,standings,picks,take]=await Promise.all(
   ["meta","news","roster","stats","salary","standings","picks","take"].map(j)
 );
 $("updated").textContent=`最終更新 ${meta.updated_at_jst} JST`;

 const mavs=standings.teams.find(t=>t.abbr==="DAL")||{};
 $("hero-record").textContent=`2025-26 最終成績：${mavs.record||"—"}　西地区 ${mavs.rank||"—"}位`;

 $("snapshot").innerHTML=[
  ["2025-26 最終成績",mavs.record||"—"],
  ["西地区順位",mavs.rank?`${mavs.rank}位`:"—"],
  ["現在のロースター",`${roster.players.length}人`],
  ["2026-27 総サラリー",money(salary.summary.total_allocations)]
 ].map(([a,b])=>`<div class="snap-row"><div class="snap-label">${esc(a)}</div><div class="snap-value">${esc(b)}</div></div>`).join("");

 $("news-list").innerHTML=news.items.map(n=>`
  <a class="post-card" href="${esc(n.url)}" target="_blank" rel="noopener">
    <div class="post-date-block">${esc(formatDate(n.published))}</div>
    <div>
      <div class="post-source">${esc(n.source)}</div>
      <div class="post-title">${esc(n.title)}</div>
    </div>
  </a>`).join("");

 $("player-grid").innerHTML=roster.players.map(p=>`
  <a class="player-card" href="./${slug(p.name)}.html">
    <div class="player-no">背番号 ${esc(p.number)}</div>
    <div class="player-name">${esc(p.name)}</div>
    <div class="player-meta">${esc(p.position)} ・ ${esc(p.age)}歳 ・ ${p.status==="Active"?"登録中":p.status==="Injured"?"負傷者リスト":p.status==="Two-way"?"2-way契約":esc(p.status)}</div>
  </a>`).join("");

 $("stats-body").innerHTML=stats.players.map(p=>`
  <tr>
    <td><strong>${esc(p.name)}</strong></td>
    <td>${p.gp}</td><td><b>${p.pts}</b></td><td>${p.reb}</td><td>${p.ast}</td><td>${p.fg}</td><td>${p.three}</td>
  </tr>`).join("");

 $("standings").innerHTML=standings.teams.map(t=>`
  <div class="stand-row ${t.abbr==="DAL"?"mavs":""}">
    <span>${t.rank}</span><span>${esc(t.team)}</span><span>${esc(t.record)}</span>
  </div>`).join("");

 const leaders=[...stats.players].sort((a,b)=>b.pts-a.pts).slice(0,6);
 $("leaders").innerHTML=leaders.map(p=>`
  <div class="leader-row">
    <strong>${esc(p.name)}</strong>
    <div class="leader-stat"><span>得点</span><b>${p.pts}</b></div>
    <div class="leader-stat"><span>REB</span><b>${p.reb}</b></div>
    <div class="leader-stat"><span>AST</span><b>${p.ast}</b></div>
  </div>`).join("");

 const s=salary.summary;
 $("cap-cards").innerHTML=[
   ["サラリーキャップ",s.salary_cap],
   ["現役ロースター",s.active_roster],
   ["総アロケーション",s.total_allocations],
   ["セカンドエプロン",s.second_apron]
 ].map(([a,b])=>`<div class="cap-card"><div class="cap-label">${a}</div><div class="cap-value">${money(b)}</div></div>`).join("");

 const max=Math.max(...salary.players.map(p=>p.cap_hit||0),1);
 $("salary-bars").innerHTML=salary.players.map(p=>`
  <div class="bar-row">
    <div>${esc(p.name)}</div>
    <div class="bar-track"><div class="bar-fill" style="width:${Math.round((p.cap_hit/max)*100)}%"></div></div>
    <div class="bar-money">${money(p.cap_hit)}</div>
  </div>`).join("");

 $("draft-grid").innerHTML=picks.years.map(y=>`
  <div class="draft-card">
    <div class="draft-year">${y.year}年</div>
    ${y.picks.map(p=>`<div class="pick"><span class="round">${p.round==="1st"?"1巡目":"2巡目"}</span>${esc(p.detail)}</div>`).join("")}
  </div>`).join("");

 $("take-text").textContent=take.text;
 $("take-date").textContent=`${take.date} 更新`;
}

load().catch(e=>{
 console.error(e);
 $("updated").textContent="データ読み込みエラー";
 const msg=document.createElement("div");
 msg.style.cssText="max-width:1180px;margin:12px auto;padding:12px 22px;background:#fff3cd;color:#664d03;font:14px system-ui";
 msg.textContent="データファイルの読み込みに失敗しました: "+e.message;
 document.body.insertBefore(msg,document.querySelector("main"));
});
