from twilio.rest import Client
import requests
import os


WEATHER_API_KEY = os.environ.get("OWM_API_KEY")
LAT = 28.6650
LON = 77.4485
ACCOUNT_SID = "ACf511788dffdebc770d7afd6f37bd1418"
AUTH_TOKEN = os.environ.get("TW_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = "+19346491425"
MY_PHONE_NUMBER = os.environ.get("MY_PN")

parameters = {
    "lat": LAT,
    "lon": LON,
    "appid": WEATHER_API_KEY,
    "cnt": 4,
    "units": "metric"
}

response = requests.get(url="http://api.openweathermap.org/data/2.5/forecast", params=parameters)
response.raise_for_status()
data = response.json()

count = data["cnt"]

timestamp_codes = [data["list"][i]["weather"][0]["id"] for i in range(0, count)]


if any(code < 600 for code in timestamp_codes):
    client = Client(ACCOUNT_SID, AUTH_TOKEN)

    message = client.messages.create(
        from_='whatsapp:+14155238886',
        body="It's Going to Rain Today, Bring out the Umbrellas.🌧️☔️",
        to='whatsapp:+919871871250'
    )
    print(message.status)

