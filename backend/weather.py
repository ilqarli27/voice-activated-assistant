import requests

API_KEY = "925206a849d3d1eb8385db52ddfd966e"  # OpenWeatherMap API

def get_weather(city="Warsaw"):
    city = city.strip()  # boşluqları təmizlə
    if not city:
        city = "Warsaw"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={API_KEY}"
    try:
        res = requests.get(url, timeout=5).json()
        if "main" in res:
            temp = res["main"]["temp"]
            desc = res["weather"][0]["description"]
            return f"The current temperature in {city} is {temp}°C with {desc}."
        else:
            return f"Weather info not available for {city}."
    except Exception as e:
        return f"Weather service error: {e}"
