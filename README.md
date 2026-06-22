# daily-morning-brief

[![Hermes Skill](https://img.shields.io/badge/Hermes-Skill-blue)](https://github.com/lzylipu/daily-morning-brief)
[![Version](https://img.shields.io/badge/version-2.1.0-green)]()

**Hermes Agent 技能**：每日早安简报 — 自动采集天气+热搜新闻，定时推送。

## ✨ 功能

- 🌤 **天气**：2345天气（温度精准）+ wttr.in（日出日落）
- 📰 **新闻**：NewsNow 11源聚合，6字去重，按趣味性排序
- 📋 **输出**：纯文本15条简报，接地气笔法，适合微信/Telegram阅读
- ⏰ **定时**：Cron 自动执行，脚本采集 → AI格式化 → 推送
- 🔄 **重试**：HTTP 503/502/429 自动3秒间隔重试，最多10次

## 📦 依赖

- [NewsNow](https://github.com/ourongxing/newsnow) — 本地部署的聚合新闻 API
- 2345天气 / wttr.in — 无需额外部署，直接访问

## 🚀 快速开始

1. 部署 [NewsNow](https://github.com/ourongxing/newsnow) 本地实例
2. 在 Hermes 中安装本技能
3. 配置环境变量（见下方）
4. 创建 Cron 任务，勾选 `daily-morning-brief` 技能

## ⚙️ 配置

| 环境变量 | 必填 | 默认值 | 说明 |
|----------|------|--------|------|
| `BRIEF_AREA_ID` | ✅ | - | 2345天气区域编码（打开 tianqi.2345.com 你的城市页面，URL中的数字） |
| `BRIEF_AREA_TYPE` | ❌ | `2` | 2=区县, 1=城市 |
| `BRIEF_AREA_PATH` | ✅ | - | 2345天气URL路径段（如 `jianxi`、`changsha`） |
| `BRIEF_CITY` | ✅ | - | wttr.in城市名，英文或拼音（如 `Luoyang`、`Beijing`） |
| `NN_BASE` | ❌ | `http://localhost:4444` | NewsNow 本地 API 地址 |

### 获取 area_id 和 area_path

1. 访问 https://tianqi.2345.com
2. 搜索你的城市/区县
3. URL 格式为 `tianqi.2345.com/{area_path}/{area_id}.htm`
4. 例如 `tianqi.2345.com/jianxi/71777.htm` → `BRIEF_AREA_PATH=jianxi`, `BRIEF_AREA_ID=71777`

## 📁 项目结构

```
daily-morning-brief/
├── SKILL.md                         # 技能主文档（格式规范+数据源+配置）
├── README.md                        # 项目说明
├── scripts/
│   └── daily-morning-brief.py       # 数据采集脚本（天气+日出日落+新闻）
└── references/
    └── 2345-weather-api.md          # 2345天气 API 详细文档
```

## 🔧 脚本说明

`scripts/daily-morning-brief.py` 是 Cron 任务的数据采集层：

- 无第三方依赖，纯 Python 标准库（urllib/re/json）
- 输出结构化 JSON，由 Hermes Agent 按 SKILL.md 范文格式化
- 支持 HTTP 503/502/429 自动重试（3秒间隔，最多10次）
- 天气 fallback：fortyData 解析失败时自动请求 module=7 概览接口

## 📄 License

MIT
