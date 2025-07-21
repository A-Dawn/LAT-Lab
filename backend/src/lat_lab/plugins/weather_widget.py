# 天气小部件插件
# 此插件展示如何创建一个获取和显示天气信息的小部件
# 作者: LAT-LAB开发团队

import datetime
import json
import random

# 获取参数
params = globals().get("params", {})
city = params.get("city", "北京")
unit = params.get("unit", "celsius")  # celsius 或 fahrenheit
theme = params.get("theme", "light")  # light 或 dark
api_key = params.get("api_key", "")
show_forecast = params.get("show_forecast", True)

# 天气图标映射
WEATHER_ICONS = {
    "sunny": "☀️",
    "partly_cloudy": "⛅",
    "cloudy": "☁️",
    "rainy": "🌧️",
    "thunderstorm": "⛈️",
    "snowy": "❄️",
    "foggy": "🌫️",
    "windy": "🌬️"
}

# 由于这是一个演示插件，我们将模拟天气数据
# 在实际应用中，你应该使用天气API，例如OpenWeatherMap
def get_weather_data(city, api_key=None):
    # 这里应该是实际的API调用
    # 例如：
    # import requests
    # url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    # response = requests.get(url)
    # if response.status_code == 200:
    #     return response.json()
    # else:
    #     return None
    
    # 为了演示，我们返回模拟数据
    weather_types = ["sunny", "partly_cloudy", "cloudy", "rainy", "thunderstorm", "snowy", "foggy", "windy"]
    current_temp = random.randint(15, 30)  # 15°C到30°C之间的随机温度
    
    # 基于城市名称确定一个固定的随机种子，这样同一个城市每天的天气相对稳定
    random.seed(f"{city}_{datetime.datetime.now().strftime('%Y-%m-%d')}")
    current_weather = random.choice(weather_types)
    humidity = random.randint(30, 90)
    wind_speed = random.randint(0, 30)
    
    # 生成5天的天气预报
    forecast = []
    for i in range(5):
        day = (datetime.datetime.now() + datetime.timedelta(days=i+1)).strftime('%m-%d')
        forecast.append({
            "date": day,
            "weather": random.choice(weather_types),
            "temp_high": current_temp + random.randint(-5, 5),
            "temp_low": current_temp + random.randint(-10, 0)
        })
    
    return {
        "city": city,
        "temperature": current_temp,
        "weather": current_weather,
        "humidity": humidity,
        "wind_speed": wind_speed,
        "forecast": forecast
    }

# 温度单位转换
def format_temperature(temp, unit):
    if unit == "fahrenheit":
        temp = temp * 9/5 + 32
        return f"{int(temp)}°F"
    else:
        return f"{int(temp)}°C"

# 获取天气数据
weather_data = get_weather_data(city, api_key)

# 准备HTML内容
if weather_data:
    # 设置基于主题的样式
    if theme == "dark":
        background_color = "#222"
        text_color = "#fff"
        border_color = "#444"
        highlight_color = "#3498db"
    else:
        background_color = "#f8f9fa"
        text_color = "#333"
        border_color = "#ddd"
        highlight_color = "#3498db"
    
    # 当前天气HTML
    current_weather_html = f"""
    <div class="weather-current">
        <div class="weather-icon" style="font-size: 3em; margin-right: 10px;">
            {WEATHER_ICONS.get(weather_data["weather"], "☁️")}
        </div>
        <div class="weather-info">
            <div style="font-size: 1.5em; font-weight: bold;">{format_temperature(weather_data["temperature"], unit)}</div>
            <div>{weather_data["weather"].replace('_', ' ').title()}</div>
        </div>
    </div>
    <div class="weather-details" style="margin-top: 10px; display: flex; justify-content: space-between;">
        <div>
            <div style="font-size: 0.9em; color: {highlight_color};">湿度</div>
            <div>{weather_data["humidity"]}%</div>
        </div>
        <div>
            <div style="font-size: 0.9em; color: {highlight_color};">风速</div>
            <div>{weather_data["wind_speed"]} km/h</div>
        </div>
    </div>
    """
    
    # 天气预报HTML
    forecast_html = ""
    if show_forecast and weather_data["forecast"]:
        forecast_html = """
        <div class="weather-forecast" style="margin-top: 15px; border-top: 1px solid {border_color}; padding-top: 10px;">
            <h4 style="margin: 0 0 10px 0;">5日天气预报</h4>
            <div style="display: flex; justify-content: space-between;">
        """
        
        for day in weather_data["forecast"]:
            forecast_html += f"""
            <div class="forecast-day" style="text-align: center;">
                <div style="font-size: 0.8em;">{day["date"]}</div>
                <div style="font-size: 1.5em; margin: 5px 0;">{WEATHER_ICONS.get(day["weather"], "☁️")}</div>
                <div style="font-size: 0.8em;">{format_temperature(day["temp_high"], unit)}/{format_temperature(day["temp_low"], unit)}</div>
            </div>
            """
        
        forecast_html += """
            </div>
        </div>
        """
    
    # 完整的小部件HTML
    widget_html = f"""
    <div style="
        font-family: Arial, sans-serif;
        background-color: {background_color};
        color: {text_color};
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        border: 1px solid {border_color};
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <h3 style="margin: 0; font-size: 1.2em;">{city}天气</h3>
            <div style="font-size: 0.8em;">{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
        </div>
        {current_weather_html}
        {forecast_html}
        <div style="font-size: 0.7em; text-align: center; margin-top: 10px; color: #999;">
            数据仅供演示，实际使用请配置天气API
        </div>
    </div>
    """
else:
    widget_html = f"""
    <div style="
        font-family: Arial, sans-serif;
        background-color: #f8f9fa;
        color: #333;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        border: 1px solid #ddd;
    ">
        <h3 style="margin: 0 0 10px 0;">天气信息</h3>
        <p>无法获取{city}的天气数据</p>
        <p>请检查城市名称或API密钥</p>
    </div>
    """

# 定义参数表单
params_form = {
    "title": "天气小部件配置",
    "fields": [
        {
            "name": "city",
            "label": "城市",
            "type": "text",
            "default": "北京",
            "required": True,
            "description": "要显示天气的城市名称"
        },
        {
            "name": "unit",
            "label": "温度单位",
            "type": "select",
            "options": ["celsius", "fahrenheit"],
            "default": "celsius",
            "description": "温度单位（摄氏度或华氏度）"
        },
        {
            "name": "theme",
            "label": "主题",
            "type": "select",
            "options": ["light", "dark"],
            "default": "light",
            "description": "小部件的显示主题"
        },
        {
            "name": "api_key",
            "label": "API密钥",
            "type": "text",
            "default": "",
            "required": False,
            "description": "天气API密钥（演示模式下可为空）"
        },
        {
            "name": "show_forecast",
            "label": "显示天气预报",
            "type": "checkbox",
            "default": True,
            "description": "是否显示5日天气预报"
        }
    ]
}

# 定义小部件配置
widget_config = {
    "type": "home-widget",
    "name": "天气小部件",
    "position": "sidebar",
    "priority": 30,
    "html": widget_html,
    "refresh_interval": 3600  # 每小时刷新一次
}

# 输出结果
if weather_data:
    weather_display = f"""
# {city}天气信息

## 当前天气
- 天气: {weather_data["weather"].replace('_', ' ').title()} {WEATHER_ICONS.get(weather_data["weather"], "☁️")}
- 温度: {format_temperature(weather_data["temperature"], unit)}
- 湿度: {weather_data["humidity"]}%
- 风速: {weather_data["wind_speed"]} km/h

## 天气预报
"""
    
    for day in weather_data["forecast"]:
        weather_display += f"- {day['date']}: {day['weather'].replace('_', ' ').title()} {WEATHER_ICONS.get(day['weather'], '☁️')}, {format_temperature(day['temp_high'], unit)}/{format_temperature(day['temp_low'], unit)}\n"
else:
    weather_display = f"# 无法获取{city}的天气数据\n\n请检查城市名称或API密钥。"

# 最终结果
result = f"""
{weather_display}

## 小部件配置

此插件提供了一个天气小部件，可以在博客侧边栏显示天气信息。

```json
{json.dumps(widget_config, ensure_ascii=False, indent=2)}
```

> 注意：当前版本使用模拟数据，实际使用时请配置天气API。
""" 