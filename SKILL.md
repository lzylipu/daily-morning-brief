---
name: daily-morning-brief
description: "每日早安简报 — 天气+热搜，定时推送。触发词：早安简报、早报、morning brief。"
version: 2.0.0
metadata:
  hermes:
    tags: [cron, daily, weather, news, push]
---

# Daily Morning Brief — 每日早安简报

每天早上自动采集天气和热搜新闻，整理成一条简洁简报，定时推送。

## 触发词

- 早安简报 / 早报 / morning brief
- 每日推送 / 每日简报

## 输出范文（必须严格按此格式，一字不改模板结构）

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

## 格式硬规则（违反即为不合格输出）

1. 首行：每日早安报 日期，星期X，农历XX，工作愉快，生活喜乐
2. 天气只给3项：天气描述+温度范围+日出日落。绝对不给体感/湿度/风速/气压/能见度/生活指数/紫外线
3. 预警行：仅有天气预警时才显示，无预警不显示
4. 新闻15条连续编号：不用分类标题，1-15直接排列，每条结尾用分号
5. 新闻排序：社会民生/趣味争议优先 > 消费维权 > 科技生活 > 文体 > 财经 > 国际
6. 新闻字数：每条15-25字，交代清楚什么事
7. 新闻笔法：接地气带细节，不要新闻联播体
8. 同事件合并：同一事件多角度合一条
9. 不要Markdown：不用表格、加粗、分隔线、代码块、星号
10. 日出日落：HH:MM格式
11. 结尾：【每日微语】一句金句

## 数据源

### 天气 - 2345天气（首选，温度准确）

- 七日预报: 页面内 fortyData JS 变量
  - URL: https://tianqi.2345.com/{AREA_PATH}/{AREA_ID}.htm
- 预警: GET /Pc/getWeather?area_id={AREA_ID}&area_type={AREA_TYPE}&module=2
- 2345 区县级 real_time API (module=8/9) 始终返回空，不要用它

### 日出日落 - wttr.in（仅此一项）

- URL: https://wttr.in/{CITY}?format=j1
- 仅取 weather[0].astronomy[0].sunrise/sunset，不要取温度
- User-Agent 设为 curl/7.68.0

### 新闻 - NewsNow本地API（首选，多源聚合）

- 地址: http://{NN_BASE}/api/s?id=<source_id>
- 必须带 Referer + Accept: application/json
- 新闻源组合（按趣味性排序，6字去重取15条）:
  - weibo(5) / toutiao(4) / douyin(3) / baidu(2)
  - thepaper(2) / ifeng(2) / zhihu(2) / bilibili(1)
  - ithome(1) / 36kr(1) / wallstreetcn(1)

## 环境变量配置

| 变量 | 默认值 | 说明 |
|------|--------|------|
| BRIEF_AREA_ID | (必填) | 2345天气区域编码（如71777） |
| BRIEF_AREA_TYPE | 2 | 2=区县, 1=城市 |
| BRIEF_AREA_PATH | (必填) | 2345天气URL路径段 |
| BRIEF_CITY | (必填) | wttr.in城市名（拼音） |
| NN_BASE | http://localhost:4444 | NewsNow本地API地址 |

## Cron 配置示例

- 时间: 0 7 * * *（每天7点）
- 技能: daily-morning-brief
- 脚本: daily-morning-brief.py
- hooks_auto_accept 必须为 true
- cron.wrap_response 设为 false 去掉包头尾

## 支持文件

- scripts/daily-morning-brief.py - 数据采集脚本
- references/2345-weather-api.md - 2345天气API文档
