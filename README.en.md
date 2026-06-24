# daily-morning-brief

[![Hermes Skill](https://img.shields.io/badge/Hermes-Skill-blue?logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJ3aGl0ZSI+PHBhdGggZD0iTTEyIDJMNiA4djhsNiA2IDYtNlY4bC02LTZ6Ii8+PC9zdmc+)](https://github.com/lzylipu/daily-morning-brief)
[![Version](https://img.shields.io/badge/version-2.1.0-green)]()
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/platform-linux-orange)]()

**[English](./README.en.md) | [中文](./README.md)**

**Hermes Agent Skill**: Daily morning brief — auto-collect weather + trending news, scheduled push to WeChat / Telegram.

> 🌤 Weather from 2345 (accurate temps) + wttr.in (sunrise/sunset)
> 📰 News from NewsNow 11-source aggregation, 6-char dedup, sorted by interest
> 📋 Pure text 15-item brief, casual tone, WeChat-friendly
> 🔄 Auto-retry on HTTP 503/502/429 (3s interval, max 10 attempts)

## ✨ Features

- **Weather**: 2345 (temp + description + alerts) + wttr.in (sunrise/sunset)
- **News**: NewsNow local API 11-source aggregation, 6-char prefix dedup, top 15 by interest
- **Output**: Plain text brief, casual tone, 15-25 chars per item
- **Schedule**: Cron auto-execution, script collect → AI format → push
- **Retry**: HTTP 503/502/429 auto-retry every 3s, max 10 attempts
- **Zero dependencies**: Pure Python stdlib, no pip install needed

## 📦 Dependencies

| Dependency | Required | Description |
|------------|----------|-------------|
| [NewsNow](https://github.com/ourongxing/newsnow) | Recommended | Locally deployed news aggregation API; news section empty without it |
| Python 3.x | ✅ | Script runtime |
| 2345 Weather | ✅ | Public internet access, no deployment needed |
| wttr.in | ✅ | Public internet access, no deployment needed |

## 🚀 Quick Start

### 1. Deploy NewsNow (Recommended)

```bash
# See https://github.com/ourongxing/newsnow
docker run -d -p 4444:4444 ourongxing/newsnow
```

### 2. Get 2345 Weather Area Code

1. Visit https://tianqi.2345.com
2. Search for your city/district
3. URL format: `tianqi.2345.com/{area_path}/{area_id}.htm`
4. e.g. `tianqi.2345.com/jianxi/71777.htm` → `area_path=jianxi`, `area_id=71777`

### 3. Configure Environment Variables

```bash
# Required
export BRIEF_AREA_ID=71777          # 2345 weather area code
export BRIEF_AREA_PATH=jianxi       # 2345 URL path segment
export BRIEF_CITY=Luoyang          # wttr.in city name (pinyin)

# Optional
export NN_BASE=http://localhost:4444  # NewsNow API address
export BRIEF_AREA_TYPE=2             # 2=district (default), 1=city
```

### 4. Test Run

```bash
python3 scripts/daily-morning-brief.py
```

### 5. Create Cron Task

In Hermes, create a Cron task:
- Skill: `daily-morning-brief`
- Script: `daily-morning-brief.py`
- Schedule: `0 7 * * *` (daily at 7:00)
- `hooks_auto_accept`: true
- `cron.wrap_response`: false

## ⚙️ Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `BRIEF_AREA_ID` | ✅ | - | 2345 weather area code |
| `BRIEF_AREA_PATH` | ✅ | - | 2345 URL path segment |
| `BRIEF_CITY` | ✅ | - | wttr.in city name (English/Pinyin) |
| `BRIEF_AREA_TYPE` | ❌ | `2` | 2=district, 1=city |
| `NN_BASE` | ❌ | `http://localhost:4444` | NewsNow local API address |

## 📁 Project Structure

```
daily-morning-brief/
├── SKILL.md                        # Skill doc (format + data sources + config)
├── README.md                       # Chinese README
├── README.en.md                    # English README
├── scripts/
│   └── daily-morning-brief.py      # Data collection script
└── references/
    └── 2345-weather-api.md         # 2345 weather API docs
```

## 🔧 Script Details

`scripts/daily-morning-brief.py` is the data collection layer for Cron tasks:

- **Zero third-party deps**: Pure `urllib` / `re` / `json` stdlib
- **Structured JSON output**: Formatted by Hermes Agent per SKILL.md template
- **Auto-retry**: HTTP 503/502/429 retry every 3s, max 10 attempts
- **Weather fallback**: Auto-requests module=7 overview API when fortyData parse fails
- **6-char dedup**: Cross-source same-event auto-dedup

## 📄 License

MIT
