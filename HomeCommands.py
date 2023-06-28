from enum import Enum
from yeelight import Bulb
import os, json, requests

bulb = Bulb('192.168.191.209') # лампочка

class commands(Enum):
    HELLO, WEATHER, LIGHT, DOCTOR, IDLE, BLUE, RED, YELLOW = range(8)

async def command_control(command: int):
    """
    Выбор команд
    """
    try:
        if command == commands.HELLO.value:
            #print("Hello")
            pass
        if command == commands.WEATHER.value:
            await weather_request(os.getenv('lat'), os.getenv('lon')) #запрос погоды
        elif command == commands.LIGHT.value:
            await light_control() # включить/выключить лампочку
        elif command == commands.DOCTOR.value:
            print("Do something")
        elif command in [5, 6, 7]:
            await change_color(command) # смена цвета лампочки
    except Exception as e:
        print(e)

async def light_control():
    bulb.toggle()

async def change_color(color: int):
    """
    Изменение цвета лампочки
    """
    try:
        if color == commands.BLUE.value:
            print('Синий')
            bulb.set_rgb(0, 0, 255) #синий
        elif color == commands.RED.value:
            print('Красный')
            bulb.set_rgb(255, 0, 0) #красный
        elif color == commands.YELLOW.value:
            bulb.set_rgb(255, 255, 0) #жёлтый
    except Exception as e:
        print('color error')
        print(e)

async def weather_request(lat, lon):
    """
    Получение информации о погоде
    """
    url = f'https://api.weather.yandex.ru/v2/informers?lat={lat}&lon={lon}&[lang=ru_RU]'
    try:
        req = requests.get(url, headers={'X-Yandex-API-Key': os.getenv('api_key')}, verify=True)
    except Exception as e:
        print('Weather error', e)
        return 0

    yandex_json = json.loads(req.text)
    weather = dict()
    params = ['condition', 'wind_dir', 'pressure_mm', 'humidity']
    weather['fact'] = dict()
    weather['fact']['temp'] = yandex_json['fact']['temp']
    for param in params:
        weather['fact'][param] = yandex_json['fact'][param]
    print(weather)

