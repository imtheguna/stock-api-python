import requests

session = requests.Session()

# Step 1: Visit homepage to get cookies
session.get("https://www.nseindia.com", headers={
    "User-Agent": "Mozilla/5.0"
})

# Step 2: Try fetching JSON (e.g., NIFTY data)
response = session.get("https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050", headers={
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.nseindia.com/"
})

print(response.status_code)
print(response)
