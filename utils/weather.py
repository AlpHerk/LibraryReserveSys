import requests
import json

url = "https://api.caiyunapp.com/v2.6/WcqmxGvXTxxwNAEa/118.64104528639601,32.082130970743954/hourly?hourlysteps=1"

def weather():
    resp = requests.get(url).text
    resp = json.loads(resp)
    resp = resp['result']['hourly']
    
    description = resp['description']           # 天气描述
    skycon      = resp['skycon'][0]['value']    # 天气情况
    temperature = resp['temperature'][0]['value'] # 室外温度
    probability = resp['precipitation'][0]['probability'] # 未来一小时降雨强度

    return skycon, description,  temperature, probability