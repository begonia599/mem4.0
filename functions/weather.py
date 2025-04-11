"""
天气查询模块 - 使用高德地图API查询天气
"""
import requests
import json
import argparse
import sys

# 添加 Pydantic 模型定义
from pydantic import BaseModel, Field
from typing import Literal, Optional

class WeatherRequest(BaseModel):
    city: str = Field(description="城市名称，例如'北京'")
    extensions: Literal["base", "all"] = Field(
        default="base", 
        description="天气数据类型，'base'为实况天气，'all'为预报天气"
    )

def get_weather(city, key=None, extensions="base", unit="celsius"):
    """
    查询指定城市的天气信息
    
    Args:
        city (str): 城市名称，例如：'北京'
        key (str, optional): 高德地图API密钥
        extensions (str, optional): 天气数据类型，'base'为实况天气，'all'为预报天气
        unit (str, optional): 温度单位，'celsius'或'fahrenheit'
        
    Returns:
        dict: 天气信息
    """
    from config import AMAP_KEY
    
    # 使用配置文件中的密钥或传入的密钥
    api_key = key or AMAP_KEY
    
    # 构建API请求URL
    url = "https://restapi.amap.com/v3/weather/weatherInfo"
    params = {
        "key": api_key,
        "city": city,
        "extensions": extensions,
        "output": "JSON"
    }
    
    try:
        # 发起请求
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        # 检查请求状态
        if data["status"] == "1":  # 高德API成功状态码为"1"
            if extensions == "base" and "lives" in data and data["lives"]:
                # 处理实况天气
                weather_info = data["lives"][0]
                temperature = float(weather_info["temperature"])
                
                # 温度单位转换
                if unit.lower() == "fahrenheit":
                    temperature = temperature * 9 / 5 + 32
                    unit_display = "°F"
                else:
                    unit_display = "°C"
                
                # 返回实况天气
                return {
                    "city": weather_info["city"],
                    "weather": weather_info["weather"],
                    "temperature": str(round(temperature, 1)) + unit_display,
                    "winddirection": weather_info["winddirection"],
                    "windpower": weather_info["windpower"],
                    "humidity": weather_info["humidity"],
                    "reporttime": weather_info["reporttime"]
                }
            elif extensions == "all" and "forecasts" in data and data["forecasts"]:
                # 返回天气预报
                forecast = data["forecasts"][0]
                return {
                    "city": forecast["city"],
                    "forecasts": [
                        {
                            "date": cast["date"],
                            "dayweather": cast["dayweather"],
                            "nightweather": cast["nightweather"],
                            "daytemp": cast["daytemp"],
                            "nighttemp": cast["nighttemp"],
                            "daywind": cast["daywind"],
                            "nightwind": cast["nightwind"]
                        } for cast in forecast["casts"]
                    ]
                }
            else:
                return {"error": "未找到天气数据"}
        else:
            return {"error": f"API错误: {data.get('info', '未知错误')}"}
    
    except requests.Timeout:
        return {"error": "天气API请求超时"}
    except requests.RequestException as e:
        return {"error": f"网络请求异常: {str(e)}"}
    except Exception as e:
        return {"error": f"处理天气数据时出错: {str(e)}"}

def print_weather_report(weather_data):
    """
    格式化打印天气数据
    
    Args:
        weather_data (dict): 天气数据
    """
    if "error" in weather_data:
        print(f"查询失败: {weather_data['error']}")
        return

    if "city" in weather_data and "weather" in weather_data:
        # 实况天气
        print(f"\n=== {weather_data['city']} 实时天气 ===")
        print(f"天气情况: {weather_data['weather']}")
        print(f"温度: {weather_data['temperature']}")
        print(f"风向: {weather_data['winddirection']}")
        print(f"风力: {weather_data['windpower']}")
        print(f"湿度: {weather_data['humidity']}%")
        print(f"发布时间: {weather_data['reporttime']}")
    elif "city" in weather_data and "forecasts" in weather_data:
        # 天气预报
        print(f"\n=== {weather_data['city']} 天气预报 ===")
        for forecast in weather_data["forecasts"]:
            print(f"\n日期: {forecast['date']}")
            print(f"白天天气: {forecast['dayweather']}")
            print(f"夜间天气: {forecast['nightweather']}")
            print(f"白天温度: {forecast['daytemp']}°C")
            print(f"夜间温度: {forecast['nighttemp']}°C")
            print(f"白天风向: {forecast['daywind']}")
            print(f"夜间风向: {forecast['nightwind']}")

def main():
    """命令行入口函数"""
    parser = argparse.ArgumentParser(description='查询指定城市的天气信息')
    parser.add_argument('city', help='城市名称或编码，例如：北京')
    parser.add_argument('--key', '-k', help='高德地图API密钥')
    parser.add_argument('--type', '-t', 
                        choices=['base', 'all'], 
                        default='base', 
                        help='天气数据类型，base为实况天气，all为预报天气')
    args = parser.parse_args()

    try:
        # 导入配置
        sys.path.append(r'e:\memgpt4')  # 添加项目根目录到路径
        print(f"正在查询 {args.city} 的{'实况' if args.type == 'base' else '预报'}天气...")
        weather_data = get_weather(args.city, args.key, args.type)
        print_weather_report(weather_data)
    except ImportError as e:
        print(f"配置导入错误: {e}")
        print("提示: 请确保当前目录是项目根目录，或设置正确的PYTHONPATH")
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    main()