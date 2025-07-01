import requests

url = "https://www.amfiindia.com/spages/NAVAll.txt"
response = requests.get(url)

lines = response.text.splitlines()
funds = []

for line in lines:
    parts = line.split(";")
    print(parts)
    if len(parts) >= 5 and parts[0].isdigit():
        funds.append({
            "scheme_code": parts[0],
            "fund_name": parts[3],
            "scheme_name": parts[2],

        })

# Print first 5
for f in funds[:1]:
    print(f)
