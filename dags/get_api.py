import requests


api_key = "f7c7d7e9c66c1c882e9d33e17063515f"
url = f"https://api.openweathermap.org/data/2.5/weather?q=Hanoi&appid={api_key}&units=metric"


def get_data():
    response = requests.get(url)
    return response.json()


get_data()
