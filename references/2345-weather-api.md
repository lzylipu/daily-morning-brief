# 2345天气 API 详细文档

经过 2026-06-22 完整测试，从 Hermes Docker 容器（中国内网）验证。

## 核心结论

**2345 温度比 wttr.in 更准确**，是早安简报天气的首选源。
- 2345: 直接给 17~25°C（日间/夜间），准确直观
- wttr.in: maxtempC=25 但 hourly 数据跨天混乱（0点出现27°C），不可靠

## 区域编码

| 区域 | area_id | area_type | 页面 URL |
|------|---------|-----------|---------|
| your-district（your-city） | {AREA_ID} | 2 (区县) | /{AREA_PATH}/{AREA_ID}.htm |
| your-city市 | {CITY_AREA_ID} | 1 (城市) | /luoyang1d/{CITY_AREA_ID}.htm |

## 有效 API 端点

### 1. 天气预警 (`module=2`)

```
GET https://tianqi.2345.com/Pc/getWeather?area_id={AREA_ID}&area_type=2&module=2
Headers: User-Agent: Mozilla/5.0
         Referer: https://tianqi.2345.com/{AREA_PATH}/{AREA_ID}.htm
```

响应:
```json
{
  "code": 1,
  "data": {
    "alerts": [
      {
        "alarm_color": "yellow",
        "alarm_type": "baoyu",
        "alarm_code": "0202",
        "alarm_name": "暴雨预警",
        "alarm_short": "暴雨预警"
      }
    ]
  }
}
```

alarm_color: `yellow` / `orange` / `red` / `blue`

### 2. 天气概览 (`module=7`)

```
GET https://tianqi.2345.com/Pc/getWeather?area_id={AREA_ID}&area_type=2&module=7
```

响应:
```json
{
  "data": {
    "weather": {
      "whole_wea": "多云",
      "smarty_img": 28,
      "whole_temp": "17~25"
    }
  }
}
```

### 3. 生活指数 (POST)

```
POST https://tianqi.2345.com/pc/getLifeIndex
Content-Type: application/x-www-form-urlencoded
X-Requested-With: XMLHttpRequest
Referer: https://tianqi.2345.com/{AREA_PATH}/{AREA_ID}.htm

body: areaId={AREA_ID}&areaType=2&lifestyleType=1&lifestyleDate=
```

⚠️ **必须带 `X-Requested-With: XMLHttpRequest` + `Referer`**，否则返回空。

响应: 6 项指标 (固定顺序)：
1. 感冒 — "易发感冒" / "少发感冒"
2. 穿衣 — "天气较舒适" / "炎热"
3. 晾晒 — "不适宜晾晒" / "适宜晾晒"
4. 洗车 — "不适宜" / "适宜"
5. 紫外线 — "紫外线很弱" / "紫外线强"
6. 晨练 — "不宜晨练" / "适宜晨练"

每项含 `radarData`(0-100) + `raderInfo[].info`(中文) + `raderInfo[].class`("warn"=需注意)

### 4. 七日预报 (fortyData JS 变量)

页面 `https://tianqi.2345.com/{AREA_PATH}/{AREA_ID}.htm` 内嵌 JS:

```javascript
var fortyData={"data":[
  {"time":1782057600,"date":"6月22日","weather":"多云","day_img":"28",
   "day_temp":"25","night_temp":"17","sleet":0},
  ...
]};
```

**提取方式**: 不要 `json.loads` 整个变量（尾部截断报错），按 `{"time":` 分段逐条解析：
```python
import re
# 找所有天条目
items = re.findall(r'\{"time":\d+.*?"sleet":\d\}', html)
for item_str in items:
    day = json.loads(item_str)
    # day["date"], day["weather"], day["day_temp"], day["night_temp"]
```

## 无效端点（不要使用）

| module | 期望 | 实际 |
|--------|------|------|
| 8 | real_time | `{}` 区县级始终空 |
| 9 | real_time+info | `{}` 同上 |
| /Pc/Hourly | 小时数据 | 404 |
| /today-{AREA_ID}.htm | 今日详情 | 404 |

## 温度对比 (2026-06-22 实测)

| 源 | 温度 | 可靠性 |
|----|------|--------|
| 2345 fortyData | 17~25°C | ✅ 日常温度范围，准确 |
| 2345 module=7 | 17~25°C | ✅ 同上 |
| wttr.in maxtempC | 25°C | ⚠️ 与2345一致但hourly混乱 |
| wttr.in hourly 00:00 | 27°C | ❌ 跨天数据，不可用 |

**结论: 温度用 2345，日出日落用 wttr.in。**

## wttr.in 日出日落 (仅此项)

```
GET https://wttr.in/Luoyang?format=j1
Header: User-Agent: curl/7.68.0
→ weather[0].astronomy[0].sunrise / sunset
```

2345 不提供日出日落数据。
