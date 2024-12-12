import json
import requests
from geopy import distance
import folium
import os
from dotenv import load_dotenv


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = (
        response.json()['response']
        ['GeoObjectCollection']['featureMember']
    )
    response_data = response.json()
    found_places = (
        response_data['response']
        ['GeoObjectCollection']['featureMember']
    )

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def get_distance(coffee_shop):
    return coffee_shop['distance']


def main():
    load_dotenv()
    apikey = os.getenv('APIKEY')
    my_address = input("Где вы находитесь?")
    my_coords = fetch_coordinates(apikey, my_address)
    my_coords = (my_coords[1], my_coords[0])
    with open("coffee.json", "r", encoding="CP1251") as my_file:
        file_contents = my_file.read()
    content = json.loads(file_contents)
    m = folium.Map(location=[my_coords[0], my_coords[1]], zoom_start=10)
    folium.Marker(
        location=[my_coords[0], my_coords[1]],
        popup="Ваше местонахождение",
        icon=folium.Icon(color="red"),
    ).add_to(m)
    coffe_list = []
    for i in range(len(content)):
        coffe_coords = (
            content[i]["Latitude_WGS84"],
            content[i]["Longitude_WGS84"]
        )
        coffe_dict = {
            'title': content[i]["Name"],
            'distance': distance.distance(my_coords, coffe_coords).km,
            'latitude': content[i]["Latitude_WGS84"],
            'longitude': content[i]["Longitude_WGS84"]
        }
        coffe_list.append(coffe_dict)
    sorted_coffe_list = sorted(coffe_list, key=get_distance)
    for i in range(len(sorted_coffe_list[:5])):
        folium.Marker(
            location=[
                sorted_coffe_list[:5][i]['latitude'],
                sorted_coffe_list[:5][i]['longitude']
            ],
            popup=sorted_coffe_list[:5][i]['title'],
            icon=folium.Icon(icon='coffee', prefix='fa')
        ).add_to(m)
    m.save('map.html')


if __name__ == '__main__':
    main()
