# 2345天气 API 文档

基于 2026-06-22 实测验证，适用于 Hermes Docker 容器环境。

> **核心结论**：温度用 2345，日出日落用 wttr.in。区县级 `real_time` API 不可用。

## 区域编码获取

1. 访问 [tianqi.2345.com](https://tianqi.2345.com)
2. 搜索目标城市/区县
3. URL 格式：`tianqi.2345.com/{area_path}/{area_id}.htm`

| 参数 | 说明 | 示例 |
|------|------|------|
| `area_id` | 区域数字编码 | 71777 |
| `area_type` | 1=城市, 2=区县 | 2 |
| `area_path` | URL路径段 | jianxi |

## 有效 API 端点

### 1. 天气预警 (module=2)

```
GET https://tianqi.2345.com/Pc/getWeather?area_id={AREA_ID}&area_type=2&module=2
Headers:
  User-Agent: Mozilla/5.0
  Referer: https://tianqi.2345.com/{AREA_PATH}/{AREA_ID}.htm
```

响应：
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

`alarm_color`: `yellow` / `orange` / `red` / `blue`

### 2. 天气概览 (module=7)

```
GET https://tianqi.2345.com/Pc/getWeather?area_id={AREA_ID}&area_type=2&module=7
```

响应：
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

可作为 fortyData 解析失败时的备用温度源。

### 3. 生活指数 (POST)

```
POST https://tianqi.2345.com/pc/getLifeIndex
Content-Type: application/x-www-form-urlencoded
X-Requested-With: XMLHttpRequest
Referer: https://tianqi.2345.com/{AREA_PATH}/{AREA_ID}.htm

body: areaId={AREA_ID}&areaType=2&lifestyleType=1&lifestyleDate=
```

**必须带 `X-Requested-With: XMLHttpRequest` + `Referer`**，否则返回空。

6 项指标（固定顺序）：感冒 / 穿衣 / 晾晒 / 洗车 / 紫外线 / 晨练

### 4. 七日预报 (fortyData JS 变量)

页面 `https://tianqi.2345.com/{AREA_PATH}/{AREA_ID}.htm` 内嵌 JS：

```javascript
var fortyData={"data":[
  {"time":1782057600,"date":"6月22日","weather":"多云","day_img":"28",
   "day_temp":"25","night_temp":"17","sleet":0},
  ...
]};
```

**⚠️ 不要对整个变量 `json.loads`**（尾部截断会报错），按 `{"time":` 分段逐条解析：

```python
import re
items = re.findall(r'{"time":\d+.*?"sleet":\d\}', html)
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

## wttr.in 日出日落

2345 不提供日出日落数据，需用 wttr.in 补充：

```
GET https://wttr.in/{CITY}?format=j1
Header: User-Agent: curl/7.68.0
→ weather[0].astronomy[0].sunrise / sunset
```

**仅取日出日落**，wttr.in 温度数据不可靠（hourly跨天混乱）。
