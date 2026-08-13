#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import json,urllib.request,urllib.parse,xml.etree.ElementTree as ET,html

ROOT=Path(__file__).resolve().parent
UA={"User-Agent":"Mozilla/5.0 (MavsDaily personal fan site)"}
def get(url):
    req=urllib.request.Request(url,headers=UA)
    with urllib.request.urlopen(req,timeout=25) as r:return r.read()
def save(name,obj):
    (ROOT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding="utf-8")

def news():
    q=urllib.parse.quote("Dallas Mavericks when:7d")
    x=ET.fromstring(get(f"https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"))
    items=[]
    for it in x.findall(".//item")[:10]:
        items.append({"title":html.unescape(it.findtext("title") or ""),"source":it.findtext("source") or "Google News","published":it.findtext("pubDate") or "","url":it.findtext("link") or ""})
    if items: save("news.json",{"items":items})

def roster():
    raw=json.loads(get("https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams/dal/roster"))
    athletes=raw.get("athletes",[]); players=[]
    for x in athletes:
        entries=x.get("items",[]) if isinstance(x,dict) and "items" in x else [x]
        for p in entries:
            if not isinstance(p,dict): continue
            players.append({"number":p.get("jersey","—"),"name":p.get("fullName") or p.get("displayName",""),"position":(p.get("position") or {}).get("abbreviation",""),"age":p.get("age",""),"status":(p.get("status") or {}).get("name","Active"),"salary":None})
    if players: save("roster.json",{"source":"ESPN API","players":players})

for fn in (news,roster):
    try: fn(); print("OK",fn.__name__)
    except Exception as e: print("WARN",fn.__name__,e)

save("meta.json",{"updated_at_jst":datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y-%m-%d %H:%M"),"season":"2026-27"})
