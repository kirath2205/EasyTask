import requests
import json

url = "http://localhost:8000/userauth/dj-rest-auth/google/"
data = {
    "access_token": "",
    "id_token": ""
}

response = requests.post(url, json=data)
print(json.dumps(response.json(), indent=2))