# daily-morning-brief

Hermes Agent 技能：每日早安简报 - 天气+热搜自动采集，定时推送。

## 功能

- 天气：2345天气（温度准确）+ wttr.in（日出日落）
- 新闻：NewsNow本地API 11源聚合，6字去重，按趣味性排序
- 输出：纯文本15条简报，接地气笔法
- 定时：Cron自动执行，脚本采集+AI格式化+推送

## 快速开始

1. 部署 [NewsNow](https://github.com/ourongxing/newsnow) 本地实例
2. 配置环境变量（见SKILL.md）
3. 创建Cron任务勾选 daily-morning-brief 技能

## 配置

| 环境变量 | 默认值 | 说明 |
|----------|--------|------|
| BRIEF_AREA_ID | (必填) | 2345天气区域编码 |
| BRIEF_AREA_PATH | (必填) | 2345天气URL路径段 |
| BRIEF_CITY | (必填) | wttr.in城市名（拼音） |
| NN_BASE | http://localhost:4444 | NewsNow本地API地址 |

## 许可

MIT
