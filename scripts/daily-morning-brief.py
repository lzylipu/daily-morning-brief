1|#!/usr/bin/env python3
2|"""每日早安简报数据采集脚本
3|
4|数据源:
5|  - 2345天气: 当天温度(高/低)+天气描述+预警
6|  - wttr.in: 仅取日出日落（2345不提供）
7|  - NewsNow本地API: 多源聚合新闻，按趣味性/民生优先排序
8|
9|输出结构化 JSON，供 Agent 按 SKILL.md 范文格式整理。
10|
11|用法:
12|  python3 daily-morning-brief.py
13|  环境变量: BRIEF_AREA_ID(必填，如71777), BRIEF_AREA_TYPE(默认2)
14|"""
15|
16|import json
17|import re
18|import urllib.request
19|import urllib.parse
20|import os
21|from datetime import datetime
22|
23|AREA_ID = os.environ.get("BRIEF_AREA_ID", "")  # 例: 71777
24|AREA_TYPE = os.environ.get("BRIEF_AREA_TYPE", "2")
AREA_PATH = os.environ.get("BRIEF_AREA_PATH", "")  # 例: jianxi  # 2345天气URL路径段
25|BROWSER_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
26|CITY = os.environ.get("BRIEF_CITY", "")  # 例: Luoyang  # wttr.in城市名(拼音)
CURL_UA = "curl/7.68.0"
27|NN_BASE = os.environ.get("NN_BASE", "http://localhost:4444")  # NewsNow本地API地址
28|NEWS_TOTAL = 15
29|
30|# 新闻源: (source_id, 取条数, 排序权重-越小越靠前)
31|SOURCES = [
32|    ("weibo",        5,  1),
33|    ("toutiao",      4,  2),
34|    ("douyin",       3,  3),
35|    ("baidu",        2,  5),
36|    ("thepaper",     2,  8),
37|    ("ifeng",        2,  14),
38|    ("zhihu",        2,  9),
39|    ("bilibili",     1,  10),
40|    ("ithome",       1,  8),
41|    ("36kr",         1,  13),
42|    ("wallstreetcn", 1,  15),
43|]
44|
45|
46|def _get(url, headers=None, timeout=10):
47|    req = urllib.request.Request(url, headers=headers or {})
48|    with urllib.request.urlopen(req, timeout=timeout) as resp:
49|        return resp.read()
50|
51|
52|def _post(url, body_bytes, headers=None, timeout=10):
53|    req = urllib.request.Request(url, data=body_bytes, headers=headers or {})
54|    with urllib.request.urlopen(req, timeout=timeout) as resp:
55|        return resp.read()
56|
57|
58|def fetch_2345_weather():
59|    url = f"https://tianqi.2345.com/{AREA_PATH}/{AREA_ID}.htm"
60|    html = _get(url, headers={"User-Agent": BROWSER_UA}, timeout=15).decode("utf-8", errors="ignore")
61|    m = re.search(r'var\s+fortyData\s*=\s*(\{.*?\});', html, re.DOTALL)
62|    if not m:
63|        return {"error": "fortyData not found"}
64|    raw = m.group(1)
65|    segments = raw.split('{"time":')
66|    if len(segments) < 2:
67|        return {"error": "no segments"}
68|    first_seg = segments[1]
69|    brace_count = 0
70|    end = 0
71|    for i, ch in enumerate(first_seg):
72|        if ch == '{': brace_count += 1
73|        elif ch == '}':
74|            if brace_count == 0: end = i; break
75|            brace_count -= 1
76|    try:
77|        day_json = json.loads('{"time":' + first_seg[:end + 1])
78|        return {"date": day_json.get("date",""), "weather": day_json.get("wea",""), "day_temp": day_json.get("day_temp",""), "night_temp": day_json.get("night_temp","")}
79|    except json.JSONDecodeError:
80|        for pat, field in [(r'"wea"\s*:\s*"([^"]+)"',"weather"),(r'"day_temp"\s*:\s*"(\d+)"',"day_temp"),(r'"night_temp"\s*:\s*"(\d+)"',"night_temp"),(r'"date"\s*:\s*"([^"]+)"',"date")]:
81|            pass
82|        weather = re.search(r'"wea"\s*:\s*"([^"]+)"', first_seg)
83|        day_t = re.search(r'"day_temp"\s*:\s*"(\d+)"', first_seg)
84|        night_t = re.search(r'"night_temp"\s*:\s*"(\d+)"', first_seg)
85|        date_m = re.search(r'"date"\s*:\s*"([^"]+)"', first_seg)
86|        return {"date": date_m.group(1) if date_m else "", "weather": weather.group(1) if weather else "", "day_temp": day_t.group(1) if day_t else "", "night_temp": night_t.group(1) if night_t else ""}
87|
88|
89|def fetch_2345_weather_overview():
90|    url = f"https://tianqi.2345.com/Pc/getWeather?area_id={AREA_ID}&area_type={AREA_TYPE}&module=7"
91|    try:
92|        data = json.loads(_get(url, headers={"User-Agent": BROWSER_UA, "Referer": f"https://tianqi.2345.com/{AREA_PATH}/{AREA_ID}.htm"}, timeout=10))
93|        w = data.get("data",{}).get("weather",{})
94|        return {"whole_wea": w.get("whole_wea",""), "whole_temp": w.get("whole_temp","")}
95|    except: return {}
96|
97|
98|def fetch_2345_alerts():
99|    url = f"https://tianqi.2345.com/Pc/getWeather?area_id={AREA_ID}&area_type={AREA_TYPE}&module=2"
100|    try:
101|        data = json.loads(_get(url, headers={"User-Agent": BROWSER_UA, "Referer": f"https://tianqi.2345.com/{AREA_PATH}/{AREA_ID}.htm"}, timeout=10))
102|        return [{"name":a.get("alarm_name",""),"color":a.get("alarm_color",""),"short":a.get("alarm_short","")} for a in data.get("data",{}).get("alerts",[])]
103|    except: return []
104|
105|
106|def fetch_wttr_sunrise_sunset():
107|    url = f"https://wttr.in/{CITY}?format=j1"
108|    try:
109|        data = json.loads(_get(url, headers={"User-Agent": CURL_UA}, timeout=10))
110|        astro = data["weather"][0]["astronomy"][0]
111|        return {"sunrise": astro.get("sunrise",""), "sunset": astro.get("sunset","")}
112|    except Exception as e:
113|        return {"error": str(e)}
114|
115|
116|def fetch_newsnow(sid):
117|    url = f"{NN_BASE}/api/s?id={sid}"
118|    try:
119|        data = json.loads(_get(url, headers={"User-Agent": BROWSER_UA, "Accept": "application/json", "Referer": f"{NN_BASE}/"}, timeout=8))
120|        return data.get("items", [])
121|    except: return []
122|
123|
124|def fetch_news():
125|    """多源聚合，按权重排序，6字判重去重，取15条"""
126|    all_items = []
127|    seen = set()
128|    for sid, count, weight in SOURCES:
129|        items = fetch_newsnow(sid)
130|        added = 0
131|        for item in items:
132|            title = item.get("title", "")
133|            if not title: continue
134|            key = title[:6]
135|            if key in seen: continue
136|            seen.add(key)
137|            desc = ""
138|            extra = item.get("extra", {})
139|            if isinstance(extra, dict):
140|                desc = extra.get("hover", "") or extra.get("info", "")
141|            all_items.append((weight, title, desc))
142|            added += 1
143|            if added >= count: break
144|    all_items.sort(key=lambda x: x[0])
145|    return [{"title": t, "desc": d} for _, t, d in all_items[:NEWS_TOTAL]]
146|
147|
148|def main():
149|    now = datetime.now()
150|    weekdays = ["一","二","三","四","五","六","日"]
151|    date_str = f"{now.year}年{now.month:02d}月{now.day:02d}日 周{weekdays[now.weekday()]}"
152|
153|    weather_2345 = fetch_2345_weather()
154|    alerts = fetch_2345_alerts()
155|    sun = fetch_wttr_sunrise_sunset()
156|    news = fetch_news()
157|
158|    if weather_2345.get("error") or not weather_2345.get("weather"):
159|        overview = fetch_2345_weather_overview()
160|        if overview:
161|            temp_range = overview.get("whole_temp","")
162|            parts = temp_range.split("~") if "~" in temp_range else ["",""]
163|            weather_2345 = {"weather": overview.get("whole_wea",""), "night_temp": parts[0].strip(), "day_temp": parts[1].strip() if len(parts)>1 else ""}
164|
165|    print(json.dumps({"date": date_str, "weather_2345": weather_2345, "alerts": alerts, "sun": sun, "news": news}, ensure_ascii=False, indent=2))
166|
167|
168|if __name__ == "__main__":
169|    main()
170|