#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import json,re,html,urllib.parse,urllib.request,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/"data"
UA={"User-Agent":"Mozilla/5.0 (compatible; MavsDaily/2.0; personal fan site)"}
def get(url,timeout=20):
    req=urllib.request.Request(url,headers=UA)
    with urllib.request.urlopen(req,timeout=timeout) as r:return r.read()
def save(n,o):(DATA/n).write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding="utf-8")
def load(n):return json.loads((DATA/n).read_text(encoding="utf-8"))
def update_news():
    q=urllib.parse.quote("Dallas Mavericks when:7d")
    x=ET.fromstring(get(f"https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"))
    items=[]
    for it in x.findall(".//item")[:12]:
        items.append({"title":html.unescape(it.findtext("title") or ""),"source":it.findtext("source") or "Google News","published":it.findtext("pubDate") or "","url":it.findtext("link") or ""})
    if items:save("news.json",{"items":items})
def update_roster():
    raw=json.loads(get("https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams/dal/roster"))
    athletes=raw.get("athletes",[]); players=[]
    for x in athletes:
        entries=x.get("items",[]) if isinstance(x,dict) and "items" in x else [x]
        for p in entries:
            if not isinstance(p,dict):continue
            players.append({"number":p.get("jersey","—"),"name":p.get("fullName") or p.get("displayName",""),"position":(p.get("position") or {}).get("abbreviation",""),"age":p.get("age",""),"status":(p.get("status") or {}).get("name","Active")})
    if players:save("roster.json",{"source":"ESPN","players":players})
def update_schedule():
    raw=json.loads(get("https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams/dal/schedule"))
    rows=[]
    for e in raw.get("events",[]):
        comp=(e.get("competitions") or [{}])[0]; cs=comp.get("competitors") or []
        dal=next((c for c in cs if (c.get("team") or {}).get("abbreviation")=="DAL"),None)
        opp=next((c for c in cs if (c.get("team") or {}).get("abbreviation")!="DAL"),None)
        if not dal or not opp:continue
        completed=(comp.get("status") or {}).get("type",{}).get("completed",False)
        if completed:
            ds=int(dal.get("score") or 0); os=int(opp.get("score") or 0)
            rows.append({"date":e.get("date","")[:10],"opponent":("vs " if dal.get("homeAway")=="home" else "@ ")+(opp.get("team") or {}).get("shortDisplayName",""),"result":"W" if ds>os else "L","score":f"{ds}-{os}"})
    rows=sorted(rows,key=lambda x:x["date"],reverse=True)[:8]
    save("games.json",{"items":rows})

def update_standings():
    raw=json.loads(get("https://site.api.espn.com/apis/v2/sports/basketball/nba/standings"))
    teams=[]
    children=(raw.get("children") or [])
    west=next((c for c in children if "western" in ((c.get("name") or "")+" "+(c.get("abbreviation") or "")).lower()),None)
    entries=(west or {}).get("standings",{}).get("entries",[])
    for i,e in enumerate(entries,1):
        t=e.get("team") or {}
        stats=e.get("stats") or []
        def sv(names):
            for st in stats:
                if (st.get("name") or "") in names:
                    return st.get("displayValue") or st.get("value")
            return None
        wins=sv({"wins"}); losses=sv({"losses"})
        rec=f"{wins}-{losses}" if wins is not None and losses is not None else (sv({"overall"}) or "")
        teams.append({"rank":i,"team":t.get("displayName",""),"abbr":t.get("abbreviation",""),"record":rec})
    if teams: save("standings.json",{"season":"current","teams":teams})

def update_stats():
    # NBA Stats endpoint; preserves the last good file if blocked or its schema changes.
    season_year=datetime.now(ZoneInfo("America/Chicago")).year
    # In Aug-Dec, NBA season begins that calendar year; Jan-Jul belongs to prior-start season.
    now=datetime.now(ZoneInfo("America/Chicago"))
    start_year=now.year if now.month>=8 else now.year-1
    season=f"{start_year}-{str(start_year+1)[-2:]}"
    params=urllib.parse.urlencode({
        "College":"","Conference":"","Country":"","DateFrom":"","DateTo":"","Division":"",
        "DraftPick":"","DraftYear":"","GameScope":"","GameSegment":"","Height":"","LastNGames":"0",
        "LeagueID":"00","Location":"","MeasureType":"Base","Month":"0","OpponentTeamID":"0",
        "Outcome":"","PORound":"0","PaceAdjust":"N","PerMode":"PerGame","Period":"0",
        "PlayerExperience":"","PlayerPosition":"","PlusMinus":"N","Rank":"N","Season":season,
        "SeasonSegment":"","SeasonType":"Regular Season","ShotClockRange":"","StarterBench":"",
        "TeamID":"1610612742","VsConference":"","VsDivision":"","Weight":""
    })
    req=urllib.request.Request("https://stats.nba.com/stats/leaguedashplayerstats?"+params,headers={
        **UA,"Referer":"https://www.nba.com/","Origin":"https://www.nba.com",
        "Accept":"application/json, text/plain, */*"
    })
    with urllib.request.urlopen(req,timeout=25) as r:
        raw=json.load(r)
    rs=(raw.get("resultSets") or [{}])[0]
    headers=rs.get("headers") or []; rows=rs.get("rowSet") or []
    idx={h:i for i,h in enumerate(headers)}
    out=[]
    for row in rows:
        def v(k,default="—"):
            i=idx.get(k); return row[i] if i is not None and i<len(row) else default
        def pct(k):
            x=v(k,None)
            return "—" if x is None else f"{float(x)*100:.1f}%"
        out.append({"name":v("PLAYER_NAME"),"gp":v("GP"),"pts":v("PTS"),"reb":v("REB"),
                    "ast":v("AST"),"fg":pct("FG_PCT"),"three":pct("FG3_PCT")})
    if out: save("stats.json",{"season":season,"players":out})

def update_salary_summary():
    cur=load("salary.json")
    try:
        text=get("https://www.spotrac.com/nba/dallas-mavericks/cap/_/year/2026").decode("utf-8","ignore")
        clean=re.sub(r"\s+"," ",text)
        pats={"salary_cap":r"Cap Maximum[^$]{0,140}\$([0-9,]+)","active_roster":r"Active Roster[^$]{0,140}\$([0-9,]+)","total_allocations":r"Total Allocations[^$]{0,140}\$([0-9,]+)","first_apron":r"1st Apron Maximum[^$]{0,140}\$([0-9,]+)","second_apron":r"2nd Apron Maximum[^$]{0,140}\$([0-9,]+)"}
        for k,p in pats.items():
            m=re.search(p,clean,re.I)
            if m:cur["summary"][k]=int(m.group(1).replace(",",""))
        save("salary.json",cur)
    except Exception:pass
def main():
    for fn in (update_news,update_roster,update_schedule,update_standings,update_stats,update_salary_summary):
        try:fn();print("OK",fn.__name__)
        except Exception as e:print("WARN",fn.__name__,repr(e))
    save("meta.json",{"updated_at_jst":datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y-%m-%d %H:%M"),"season":"2026-27"})
if __name__=="__main__":main()
