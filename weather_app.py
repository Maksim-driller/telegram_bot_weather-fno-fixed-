import requests
import json
import time
api_token = 'M6Uk03MDYG6lOQ6zHr5gcj5skUcUjEpd'
weather_url = 'http://dataservice.accuweather.com/forecasts/v1/daily/'
# получаем ключ для города
def get_location_key_for_city(city_name):
    CITY_SEARCH_URL = "http://dataservice.accuweather.com/locations/v1/cities/search"
    city_url = f"{CITY_SEARCH_URL}?apikey={api_token}&q={city_name}"

    response = requests.get(city_url)

    if response.status_code == 200:
        city_data = response.json()
        if city_data:
            return city_data[0]["Key"]
    else:
        print(f"Error: {response.status_code}, {response.text}")

    return None

# получаем данные о погоде с помощью ключа, который мы получили ранее
def get_weather_data(location_key, days):
    try:
        response = requests.get(f"{weather_url}{days}day/{location_key}", params={
            'apikey': api_token,
            'details': True,
            'metric': True
        })
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None
# данные в читаемом формате
def format_forecast(forecast):
    formatted = []
    for day in forecast['DailyForecasts']:
        date = day['Date'][:10]
        min_temp = day['Temperature']['Minimum']['Value']
        max_temp = day['Temperature']['Maximum']['Value']
        day_condition = day['Day']['IconPhrase']
        night_condition = day['Night']['IconPhrase']
        formatted.append({
            'date': date,
            'min_temp': min_temp,
            'max_temp': max_temp,
            'day_condition': day_condition,
            'night_condition': night_condition
        })
    return formatted
