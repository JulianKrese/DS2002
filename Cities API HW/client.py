import requests

API_URL = "http://34.48.125.135:5000/api/getLocalTime"
TOKEN = "this is a secure secret"

headers = {
    "Authorization": f"Bearer {TOKEN}"
}

input_city = input("Enter a city to find the local time of, ensuring properly capitalzation (Example: 'Paris'): ")

regions = [
    "Africa",
    "America",
    "Antarctica",
    "Asia",
    "Atlantic",
    "Australia",
    "Europe",
    "Indian",
    "Pacific"
]
print("Region Options: ", regions)
input_region = input("Enter the region of that city: ")

params = {
    "city": input_city,
    "region": input_region
}

response = requests.get(API_URL, headers=headers, params=params)
if response.status_code == 200:
    print("Success:", response.json())
else:
    print("Failed:", response.status_code, response.text)
