import requests

url = "http://127.0.0.1:4444/getDetailsFromJson"

payload = {
    "day":"3d",
    "list": {
    '1':{"price":719.15,"symbol":"TATAMOTORS.NS","type":"inshare"},
    '2':{"price":719.15,"symbol":"aAPL","type":"usshare"},
    '3':{"price":719.15,"symbol":"110021","type":"inmf"}}
}

# Send POST request with JSON
response = requests.post(url, json=payload)

# Print response
if response.status_code == 200:
    print("Response JSON:", response.json())
else:
    print("Error:", response.status_code, response.text)
