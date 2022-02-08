from spn import spn_
import sys
import os
import pygame
import requests
import math

pygame.init()


def lonlat_distance(a, b):
    degree_to_meters_factor = 111 * 1000
    a_lon, a_lat = a
    b_lon, b_lat = b

    radians_lattitude = math.radians((a_lat + b_lat) / 2.)
    lat_lon_factor = math.cos(radians_lattitude)

    dx = abs(a_lon - b_lon) * degree_to_meters_factor * lat_lon_factor
    dy = abs(a_lat - b_lat) * degree_to_meters_factor

    distance = math.sqrt(dx * dx + dy * dy)

    if distance >= 1000:
        return f"{round(distance / 1000, 2)} км"

    return f"{round(distance, 2)} м"


toponym_to_find = " ".join(sys.argv[1:])

geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

geocoder_params = {
    "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
    "geocode": toponym_to_find,
    "format": "json"}

response = requests.get(geocoder_api_server, params=geocoder_params)

if not response:
    # обработка ошибочной ситуации
    pass

# Преобразуем ответ в json-объект
json_response = response.json()
# Получаем первый топоним из ответа геокодера.
toponym = json_response["response"]["GeoObjectCollection"][
    "featureMember"][0]["GeoObject"]
# Координаты центра топонима:
toponym_coodrinates = toponym["Point"]["pos"]
# Долгота и широта:
toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")

cor = f"{toponym_longitude},{toponym_lattitude}"


search_api_server = "https://search-maps.yandex.ru/v1/"
api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"

address_ll = cor

search_params = {
    "apikey": api_key,
    "text": "аптека",
    "lang": "ru_RU",
    "ll": address_ll,
    "type": "biz"
}

response = requests.get(search_api_server, params=search_params)
if not response:
    #...
    pass


# Преобразуем ответ в json-объект
json_response = response.json()

# Получаем первую найденную организацию.


organization = json_response["features"][0]

# Название организации.
org_name = organization["properties"]["CompanyMetaData"]["name"]
# Адрес организации.
org_address = organization["properties"]["CompanyMetaData"]["address"]

# Получаем координаты ответа.
point = organization["geometry"]["coordinates"]
org_point = "{0},{1}".format(point[0], point[1])

x = list(map(float, address_ll.split(",")))
x2 = list(map(float, org_point.split(",")))

# Собираем параметры для запроса к StaticMapsAPI:
map_params = {
    # позиционируем карту центром на наш исходный адрес
    "ll": f"{(x[0] + x2[0]) / 2},{(x[1] + x2[1]) / 2}",
    "spn": spn_(address_ll, organization),
    "l": "map",
    # добавим точку, чтобы указать найденную аптеку
    "pt": "{0},flag~{1},home".format(org_point, address_ll),
    "size": "650,450"
}


map_api_server = "http://static-maps.yandex.ru/1.x/"
# ... и выполняем запрос
response = requests.get(map_api_server, params=map_params)

map_file = "map.png"
with open(map_file, "wb") as file:
    file.write(response.content)

clock = pygame.time.Clock()
size = width, height = 1200, 450
screen = pygame.display.set_mode(size)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            os.remove(map_file)
            sys.exit()
    screen.fill((0, 0, 0))
    k = pygame.image.load(f'map.png').convert()
    pygame.draw.rect(screen, (200, 200, 200), (650, 0, 550, 450))
    screen.blit(k, (0, 0))

    font = pygame.font.Font(None, 40)
    text = font.render(f'{organization["properties"]["name"]}', True, (0, 0, 0))
    screen.blit(text, (700, 10))

    font = pygame.font.Font(None, 25)
    text = font.render(f'{organization["properties"]["description"]}', True, (0, 0, 0))
    screen.blit(text, (670, 100))

    font = pygame.font.Font(None, 25)
    text = font.render(f'{organization["properties"]["CompanyMetaData"]["Hours"]["text"]}', True, (0, 0, 0))
    screen.blit(text, (670, 150))

    font = pygame.font.Font(None, 25)
    text = font.render(f'{lonlat_distance(x, x2)}', True, (0, 0, 0))
    screen.blit(text, (670, 200))

    pygame.display.flip()
    clock.tick(60)
