#!/usr/bin/env python3
"""每日早安简报 — 数据采集脚本

数据源:
  - 2345天气: 当天温度(高/低) + 天气描述 + 预警
  - wttr.in: 仅取日出日落（2345不提供此项）
  - NewsNow本地API: 多源聚合新闻，按趣味性/民生优先排序

输出结构化 JSON，供 Hermes Agent 按 SKILL.md 范文格式整理输出。

环境变量:
  BRIEF_AREA_ID   (必填) 2345天气区域编码，如 71777
  BRIEF_AREA_TYPE (选填) 2=区县(默认), 1=城市
  BRIEF_AREA_PATH (必填) 2345天气URL路径段，如 jianxi
  BRIEF_CITY      (必填) wttr.in城市名(拼音)，如 Luoyang
  NN_BASE         (选填) NewsNow本地API地址，默认 http://localhost:4444
"""

import json
import re
import urllib.request
import urllib.error
import os
import time
from datetime import datetime

# ==================== 配置 ====================

# 天气区域（必填，从 tianqi.2345.com URL 获取）
AREA_ID = os.environ.get("BRIEF_AREA_ID", "")
AREA_TYPE = os.environ.get("BRIEF_AREA_TYPE", "2")  # 2=区县, 1=城市
AREA_PATH = os.environ.get("BRIEF_AREA_PATH", "")    # 如 jianxi

# wttr.in 城市名（必填，英文/拼音）
CITY = os.environ.get("BRIEF_CITY", "")

# NewsNow 本地 API 地址（选填，部署 newsnow 后填入）
NN_BASE = os.environ.get("NN_BASE", "http://localhost:4444")

# 输出新闻条数
NEWS_TOTAL = 15

# HTTP 请求重试配置
MAX_RETRIES = 10    # 最大重试次数（503/502/429 触发）
RETRY_DELAY = 3     # 重试间隔（秒）

# User-Agent
BROWSER_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
CURL_UA = "curl/7.68.0"

# 新闻源配置: (source_id, 每源取条数, 排序权重-越小越靠前)
SOURCES = [
    ("weibo",        5,  1),   # 微博热搜 — 民生+争议话题
    ("toutiao",      4,  2),   # 头条 — 消费维权+社会
    ("douyin",       3,  3),   # 抖音 — 猎奇/短视频热门
    ("baidu",        2,  5),   # 百度 — 补充遗漏
    ("thepaper",     2,  8),   # 澎湃 — 深度社会
    ("ithome",       1,  8),   # IT之家 — 科技数码
    ("zhihu",        2,  9),   # 知乎 — 科技/职场
    ("bilibili",     1,  10),  # B站 — 年轻向
    ("36kr",         1,  13),  # 36氪 — 创业商业
    ("ifeng",        2,  14),  # 凤凰 — 时政+国际
    ("wallstreetcn", 1,  15),  # 华尔街见闻 — 财经
]


# ==================== HTTP 工具 ====================

def _get(url, headers=None, timeout=10):
    """GET 请求，503/502/429 自动重试"""
    req = urllib.request.Request(url, headers=headers or {})
    for attempt in range(MAX_RETRIES):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except urllib.error.HTTPError as e:
            if e.code in (503, 502, 429) and attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
                continue
            raise
        except (urllib.error.URLError, TimeoutError, OSError):
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
                continue
            raise


def _post(url, body_bytes, headers=None, timeout=10):
    """POST 请求，503/502/429 自动重试"""
    req = urllib.request.Request(url, data=body_bytes, headers=headers or {})
    for attempt in range(MAX_RETRIES):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except urllib.error.HTTPError as e:
            if e.code in (503, 502, 429) and attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
                continue
            raise
        except (urllib.error.URLError, TimeoutError, OSError):
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
                continue
            raise


# ==================== 天气 — 2345 ====================

def fetch_2345_weather():
    """从2345天气页面提取当天天气(fortyData JS变量第一条)"""
    url = f"https://tianqi.2345.com/{AREA_PATH}/{AREA_ID}.htm"
    html = _get(url, headers={"User-Agent": BROWSER_UA}, timeout=15).decode("utf-8", errors="ignore")
    m = re.search(r'var\s+fortyData\s*=\s*(\{.*?\});', html, re.DOTALL)
    if not m:
        return {"error": "fortyData not found"}
    raw = m.group(1)
    segments = raw.split('{"time":')
    if len(segments) < 2:
        return {"error": "no segments"}
    first_seg = segments[1]
    # 手动匹配第一个完整JSON对象（应对截断）
    brace_count = 0
    end = 0
    for i, ch in enumerate(first_seg):
        if ch == '{': brace_count += 1
        elif ch == '}':
            if brace_count == 0: end = i; break
            brace_count -= 1
    try:
        day_json = json.loads('{"time":' + first_seg[:end + 1])
        return {
            "date": day_json.get("date", ""),
            "weather": day_json.get("wea", ""),
            "day_temp": day_json.get("day_temp", ""),
            "night_temp": day_json.get("night_temp", ""),
        }
    except json.JSONDecodeError:
        # fallback: 正则逐个提取
        weather = re.search(r'"wea"\s*:\s*"([^"]+)"', first_seg)
        day_t = re.search(r'"day_temp"\s*:\s*"(\d+)"', first_seg)
        night_t = re.search(r'"night_temp"\s*:\s*"(\d+)"', first_seg)
        date_m = re.search(r'"date"\s*:\s*"([^"]+)"', first_seg)
        return {
            "date": date_m.group(1) if date_m else "",
            "weather": weather.group(1) if weather else "",
            "day_temp": day_t.group(1) if day_t else "",
            "night_temp": night_t.group(1) if night_t else "",
        }


def fetch_2345_weather_overview():
    """天气概览（fortyData解析失败时的备用源）"""
    url = f"https://tianqi.2345.com/Pc/getWeather?area_id={AREA_ID}&area_type={AREA_TYPE}&module=7"
    try:
        data = json.loads(_get(url, headers={
            "User-Agent": BROWSER_UA,
            "Referer": f"https://tianqi.2345.com/{AREA_PATH}/{AREA_ID}.htm"
        }, timeout=10))
        w = data.get("data", {}).get("weather", {})
        return {"whole_wea": w.get("whole_wea", ""), "whole_temp": w.get("whole_temp", "")}
    except Exception:
        return {}


def fetch_2345_alerts():
    """天气预警"""
    url = f"https://tianqi.2345.com/Pc/getWeather?area_id={AREA_ID}&area_type={AREA_TYPE}&module=2"
    try:
        data = json.loads(_get(url, headers={
            "User-Agent": BROWSER_UA,
            "Referer": f"https://tianqi.2345.com/{AREA_PATH}/{AREA_ID}.htm"
        }, timeout=10))
        return [
            {
                "name": a.get("alarm_name", ""),
                "color": a.get("alarm_color", ""),
                "short": a.get("alarm_short", ""),
            }
            for a in data.get("data", {}).get("alerts", [])
        ]
    except Exception:
        return []


# ==================== 日出日落 — wttr.in ====================

def fetch_wttr_sunrise_sunset():
    """从wttr.in获取日出日落（2345不提供此数据）"""
    url = f"https://wttr.in/{CITY}?format=j1"
    try:
        data = json.loads(_get(url, headers={"User-Agent": CURL_UA}, timeout=10))
        astro = data["weather"][0]["astronomy"][0]
        return {"sunrise": astro.get("sunrise", ""), "sunset": astro.get("sunset", "")}
    except Exception as e:
        return {"error": str(e)}


# ==================== 新闻 — NewsNow ====================

def fetch_newsnow(sid):
    """从NewsNow本地API获取单个新闻源"""
    url = f"{NN_BASE}/api/s?id={sid}"
    try:
        data = json.loads(_get(url, headers={
            "User-Agent": BROWSER_UA,
            "Accept": "application/json",
            "Referer": f"{NN_BASE}/",
        }, timeout=8))
        return data.get("items", [])
    except Exception:
        return []


def fetch_news():
    """多源聚合，按权重排序，6字前缀去重，取15条"""
    all_items = []
    seen = set()
    for sid, count, weight in SOURCES:
        items = fetch_newsnow(sid)
        added = 0
        for item in items:
            title = item.get("title", "")
            if not title:
                continue
            key = title[:6]  # 6字前缀判重
            if key in seen:
                continue
            seen.add(key)
            # 提取额外描述（hover/info）
            desc = ""
            extra = item.get("extra", {})
            if isinstance(extra, dict):
                desc = extra.get("hover", "") or extra.get("info", "")
            all_items.append((weight, title, desc))
            added += 1
            if added >= count:
                break
    all_items.sort(key=lambda x: x[0])
    return [{"title": t, "desc": d} for _, t, d in all_items[:NEWS_TOTAL]]


# ==================== 主流程 ====================

def main():
    now = datetime.now()
    weekdays = ["一", "二", "三", "四", "五", "六", "日"]
    date_str = f"{now.year}年{now.month:02d}月{now.day:02d}日 周{weekdays[now.weekday()]}"

    # 采集数据
    weather = fetch_2345_weather()
    alerts = fetch_2345_alerts()
    sun = fetch_wttr_sunrise_sunset()
    news = fetch_news()

    # fortyData 解析失败时，fallback 到概览接口
    if weather.get("error") or not weather.get("weather"):
        overview = fetch_2345_weather_overview()
        if overview:
            temp_range = overview.get("whole_temp", "")
            parts = temp_range.split("~") if "~" in temp_range else ["", ""]
            weather = {
                "weather": overview.get("whole_wea", ""),
                "night_temp": parts[0].strip(),
                "day_temp": parts[1].strip() if len(parts) > 1 else "",
            }

    # 输出 JSON
    result = {
        "date": date_str,
        "weather_2345": weather,
        "alerts": alerts,
        "sun": sun,
        "news": news,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
