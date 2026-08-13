#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import json, urllib.request, urllib.parse, xml.etree.ElementTree as ET, html, time

ROOT=Path(__file__).resolve().parent
UA={"User-Agent":"Mozilla/5.0 (MavsDaily personal fan site)"}

def get(url, timeout=25):
    req=urllib.request.Request(url,headers=UA)
    with urllib.request.urlopen(req,timeout=timeout) as r:
        return r.read()

def save(name,obj):
    (ROOT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding="utf-8")

def translate_ja(text):
    """Best-effort English -> Japanese headline translation.
    If translation is unavailable, return the English original.
    """
    if not text:
        return text
    try:
        params=urllib.parse.urlencode({
            "client":"gtx",
            "sl":"en",
            "tl":"ja",
            "dt":"t",
            "q":text
        })
        raw=json.loads(get("https://translate.googleapis.com/translate_a/single?"+params, timeout=15))
        translated="".join(part[0] for part in raw[0] if part and part[0])
        return translated.strip() or text
    except Exception as e:
        print("WARN translate",repr(e))
        return text

def news():
    q=urllib.parse.quote("Dallas Mavericks when:7d")
    x=ET.fromstring(get(f"https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"))
    items=[]
    for it in x.findall(".//item")[:10]:
        title=html.unescape(it.findtext("title") or "")
        # Google News titles often append " - Source"; remove only when it clearly matches source.
        source=it.findtext("source") or "Google News"
        suffix=f" - {source}"
        if title.endswith(suffix):
            title=title[:-len(suffix)].strip()

        title_ja=translate_ja(title)
        items.append({
            "title":title,
            "title_ja":title_ja,
            "source":source,
            "published":it.findtext("pubDate") or "",
            "url":it.findtext("link") or ""
        })
        time.sleep(0.15)

    if items:
        save("news.json",{"items":items})

def roster():
    raw=json.loads(get("https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams/dal/roster"))
    athletes=raw.get("athletes",[])
    players=[]
    for x in athletes:
        entries=x.get("items",[]) if isinstance(x,dict) and "items" in x else [x]
        for p in entries:
            if not isinstance(p,dict):
                continue
            players.append({
                "number":p.get("jersey","—"),
                "name":p.get("fullName") or p.get("displayName",""),
                "position":(p.get("position") or {}).get("abbreviation",""),
                "age":p.get("age",""),
                "status":(p.get("status") or {}).get("name","Active"),
                "salary":None
            })
    if players:
        save("roster.json",{"source":"ESPN API","players":players})

for fn in (news,roster):
    try:
        fn()
        print("OK",fn.__name__)
    except Exception as e:
        print("WARN",fn.__name__,e)

save("meta.json",{
    "updated_at_jst":datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y-%m-%d %H:%M"),
    "season":"2026-27"
})
