---
name: daily-morning-brief
description: "每日早安简报 — 天气+热搜新闻自动采集，定时推送。"
version: 2.1.0
author: lzylipu
license: MIT
platforms: [linux]
prerequisites:
  env_vars: [BRIEF_AREA_ID, BRIEF_AREA_PATH, BRIEF_CITY]
  services:
    - name: NewsNow
      url: https://github.com/ourongxing/newsnow
      description: "本地部署的聚合新闻 API（可选，无则新闻为空）"
metadata:
  hermes:
    tags: [daily, morning, brief, weather, news, cron, push, weixin, telegram, 2345, wttr, newsnow, 早安, 简报, 早报, 每日推送, 天气, 热搜]
    related_skills: [daily-hotspot, newsnow-skill]
    homepage: https://github.com/lzylipu/daily-morning-brief
    category: personal
    skill_type: cron
    supported_channels: [weixin, telegram, discord]
    requires_script: true
---

# Daily Morning Brief · 每日早安简报

每天早上自动采集天气和热搜新闻，整理成一条简洁简报，定时推送到微信/Telegram。

## When to Use

- 用户想要每日定时推送天气+新闻简报
- 用户说"早安简报""早报""morning brief""每日推送"
- 用户想要配置 Cron 定时任务获取新闻
- 用户想了解如何部署自动化新闻+天气推送

## 输出范文

以下是标准输出格式，Agent 必须严格遵循：

```
每日早安报 6月22日，星期一，农历五月初八，工作愉快，生活喜乐

1、男子没开空调工作一天肾坏了，高温天一定注意防暑；
2、生日朋友圈发了三天了，网友直呼好家伙；
3、轻断食一天喝了6斤牛奶，这操作你敢试吗；
4、少年捡长枪送派出所，问不会奖励作业吧；
5、网友排队给西班牙队道歉，世界杯反转来了；
6、多部门调查纸尿裤甲酰胺问题，好奇等品牌回应未检出；
7、雷军再谈与董明珠打赌：开玩笑没想到被激怒批评小米；
8、英国首相斯塔默宣布辞职，继任者选出前继续任职；
9、伊朗队世界杯后被要求离美，更衣室留感谢信获赞；
10、填报高考志愿前先看这份指南，教育部系统已升级；
11、来香格里拉打跳清空所有烦恼，国内首个非遗水市火了；
12、专家称中国牛市刚刚开始，市场信心回暖；
13、长三角地区进出口规模再创新高；
14、链博会含金量含新量持续上升；
15、世界越大偏见越小，旅行的意义就在于此；

【每日微语】：挺过艰难的岁月，那些日子终会变成生命中最精彩的篇章。
```

## 格式硬规则

1. **首行**：每日早安报 日期，星期X，农历XX，工作愉快，生活喜乐
2. **天气3项**：天气描述 + 温度范围 + 日出日落。绝对不给体感/湿度/风速/气压/生活指数
3. **预警行**：仅有预警时显示，无预警不显示
4. **新闻15条**：连续编号1-15，不用分类标题，每条结尾分号
5. **新闻排序**：社会民生/趣味 > 维权 > 科技 > 文体 > 财经 > 国际
6. **新闻字数**：每条15-25字
7. **新闻笔法**：接地气带细节，不要新闻联播体
8. **同事件合并**：多角度合一条
9. **不用Markdown**：无表格/加粗/分隔线/代码块/星号
10. **日出日落**：HH:MM格式
11. **结尾**：【每日微语】一句金句

## 数据源

### 天气 — 2345天气

- 七日预报: 页面内 `fortyData` JS 变量 → 第一条即当天
  - URL: `https://tianqi.2345.com/{AREA_PATH}/{AREA_ID}.htm`
- 预警: `GET /Pc/getWeather?area_id={AREA_ID}&area_type={AREA_TYPE}&module=2`
- 概览(备用): `GET /Pc/getWeather?area_id={AREA_ID}&area_type={AREA_TYPE}&module=7`
- ⚠️ 区县级 `real_time` API (module=8/9) 始终返回空，不要用

### 日出日落 — wttr.in

- URL: `https://wttr.in/{CITY}?format=j1`
- 仅取 `weather[0].astronomy[0].sunrise/sunset`
- User-Agent 必须设为 `curl/7.68.0`

### 新闻 — NewsNow 本地 API

- 地址: `http://{NN_BASE}/api/s?id=<source_id>`
- 必须带 `Referer` + `Accept: application/json`
- 11源组合（6字去重取15条）:

| 源 | 条数 | 权重 | 说明 |
|----|------|------|------|
| weibo | 5 | 1 | 微博热搜，社会民生+争议 |
| toutiao | 4 | 2 | 头条，消费维权+社会 |
| douyin | 3 | 3 | 抖音热点，猎奇/短视频 |
| baidu | 2 | 5 | 百度，补充遗漏 |
| thepaper | 2 | 8 | 澎湃，深度社会 |
| ifeng | 2 | 14 | 凤凰，时政+国际 |
| zhihu | 2 | 9 | 知乎，科技/职场 |
| bilibili | 1 | 10 | B站，年轻向 |
| ithome | 1 | 8 | IT之家，科技数码 |
| 36kr | 1 | 13 | 36氪，创业商业 |
| wallstreetcn | 1 | 15 | 华尔街见闻，财经 |

## 环境变量

| 变量 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| BRIEF_AREA_ID | ✅ | - | 2345天气区域编码 |
| BRIEF_AREA_TYPE | ❌ | `2` | 2=区县, 1=城市 |
| BRIEF_AREA_PATH | ✅ | - | 2345天气URL路径段 |
| BRIEF_CITY | ✅ | - | wttr.in城市名（英文/拼音） |
| NN_BASE | ❌ | `http://localhost:4444` | NewsNow 本地 API 地址 |

### 获取 area_id 和 area_path

1. 访问 [tianqi.2345.com](https://tianqi.2345.com) 搜索你的城市
2. URL 格式 `tianqi.2345.com/{area_path}/{area_id}.htm`
3. 例如 `tianqi.2345.com/jianxi/71777.htm` → `BRIEF_AREA_PATH=jianxi`, `BRIEF_AREA_ID=71777`

## Cron 配置

```yaml
schedule: "0 7 * * *"      # 每天7:00
skills: [daily-morning-brief]
script: daily-morning-brief.py
hooks_auto_accept: true     # 无人值守必须
cron.wrap_response: false   # 推送去掉包头尾
```

执行流程：脚本采集JSON → 注入Agent prompt → Agent按范文整理 → 推送

## References

- `references/2345-weather-api.md` — 2345天气 API 完整文档（端点/字段/踩坑）
- `scripts/daily-morning-brief.py` — 数据采集脚本（纯标准库，无第三方依赖）
