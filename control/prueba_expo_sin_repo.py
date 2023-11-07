import requests

url = "https://exp.host/--/api/v2/push/send"

headers = {
    "host": "exp.host",
    "accept": "application/json",
    "accept-encoding": "gzip, deflate",
    "content-type": "application/json",
}

data = {
    "to": "ExponentPushToken[bhFOjeJADEUXSb66G_a6Ad]",
    "title": "Hello",
    "body": "World",
}

response = requests.post(url, headers=headers, json=data)

if response.status_code == 200:
    print("SE ENVIO LA NOTIFICACION")
else:
    print("ERRORRRR")
    print("cod de rta:", response.status_code)
    print("rta:", response.text)
