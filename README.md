# daily-morning-brief

[![Hermes Skill](https://img.shields.io/badge/Hermes-Skill-blue?logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJ3aGl0ZSI+PHBhdGggZD0iTTEyIDJMNiA4djhsNiA2IDYtNlY4bC02LTZ6Ii8+PC9zdmc+)](https://github.com/lzylipu/daily-morning-brief)
[![Version](https://img.shields.io/badge/version-2.1.0-green)]()
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/platform-linux-orange)]()

**Hermes Agent 技能**：每日早安简报 — 自动采集天气+热搜新闻，定时推送到微信/Telegram。

> 🌤 天气用 2345（温度精准）+ wttr.in（日出日落）
> 📰 新闻用 NewsNow 11源聚合，6字去重，按趣味性排序
> 📋 输出纯文本15条简报，接地气笔法，适合微信阅读
> 🔄 HTTP 503/502/429 自动3秒重试，最多10次

## ✨ 功能

- **天气**：2345天气（温度+描述+预警）+ wttr.in（日出日落）
- **新闻**：NewsNow 本地 API 11源聚合，6字前缀去重，按趣味性排序取15条
- **输出**：纯文本简报，接地气笔法，每条15-25字
- **定时**：Cron 自动执行，脚本采集 → AI格式化 → 推送
- **重试**：HTTP 503/502/429 自动3秒间隔重试，最多10次
- **零依赖**：纯 Python 标准库，无需 pip install

## 📦 依赖

| 依赖 | 必需 | 说明 |
|------|------|------|
| [NewsNow](https://github.com/ourongxing/newsnow) | 推荐 | 本地部署的聚合新闻 API，无则新闻为空 |
| Python 3.x | ✅ | 脚本运行环境 |
| 2345天气 | ✅ | 公网直接访问，无需部署 |
| wttr.in | ✅ | 公网直接访问，无需部署 |

## 🚀 快速开始

### 1. 部署 NewsNow（推荐）

```bash
# 参考 https://github.com/ourongxing/newsnow
docker run -d -p 4444:4444 ourongxing/newsnow
```

### 2. 获取 2345 天气区域编码

1. 访问 https://tianqi.2345.com
2. 搜索你的城市/区县
3. URL 格式为 `tianqi.2345.com/{area_path}/{area_id}.htm`
4. 例如 `tianqi.2345.com/jianxi/71777.htm` → `area_path=jianxi`, `area_id=71777`

### 3. 配置环境变量

```bash
# 必填
export BRIEF_AREA_ID=71777          # 2345天气区域编码
export BRIEF_AREA_PATH=jianxi       # 2345天气URL路径段
export BRIEF_CITY=Luoyang          # wttr.in城市名（拼音）

# 选填
export NN_BASE=http://localhost:4444  # NewsNow API地址
export BRIEF_AREA_TYPE=2             # 2=区县(默认), 1=城市
```

### 4. 测试运行

```bash
python3 scripts/daily-morning-brief.py
```

### 5. 创建 Cron 定时任务

在 Hermes 中创建 Cron 任务：
- 技能：`daily-morning-brief`
- 脚本：`daily-morning-brief.py`
- 时间：`0 7 * * *`（每天7:00）
- `hooks_auto_accept`: true
- `cron.wrap_response`: false

## ⚙️ 环境变量

| 变量 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `BRIEF_AREA_ID` | ✅ | - | 2345天气区域编码 |
| `BRIEF_AREA_PATH` | ✅ | - | 2345天气URL路径段 |
| `BRIEF_CITY` | ✅ | - | wttr.in城市名（英文/拼音） |
| `BRIEF_AREA_TYPE` | ❌ | `2` | 2=区县, 1=城市 |
| `NN_BASE` | ❌ | `http://localhost:4444` | NewsNow 本地 API 地址 |

## 📁 项目结构

```
daily-morning-brief/
├── SKILL.md                        # 技能主文档（格式规范+数据源+配置）
├── README.md                       # 项目说明（你正在看）
├── scripts/
│   └── daily-morning-brief.py      # 数据采集脚本
└── references/
    └── 2345-weather-api.md         # 2345天气 API 完整文档
```

## 🔧 脚本说明

`scripts/daily-morning-brief.py` 是 Cron 任务的数据采集层：

- **零第三方依赖**：纯 `urllib` / `re` / `json` 标准库
- **输出结构化 JSON**：由 Hermes Agent 按 SKILL.md 范文格式化
- **自动重试**：HTTP 503/502/429 自动3秒间隔重试，最多10次
- **天气 fallback**：fortyData 解析失败时自动请求 module=7 概览接口
- **6字去重**：跨新闻源同事件自动去重

## 🔍 搜索关键词

`早安简报` `早报` `每日推送` `每日简报` `morning brief` `daily brief` `天气` `热搜` `新闻聚合` `cron` `定时推送` `2345天气` `wttr.in` `NewsNow` `微信推送` `Telegram推送`

## 📄 License

MIT
