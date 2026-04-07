# import requests

# session = requests.Session()

# # Step 1: Visit homepage to get cookies
# session.get("https://www.nseindia.com", headers={
#     "User-Agent": "Mozilla/5.0"
# })

# # Step 2: Try fetching JSON (e.g., NIFTY data)
# response = session.get("https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050", headers={
#     "User-Agent": "Mozilla/5.0",
#     "Referer": "https://www.nseindia.com/"
# })

# print(response.status_code)
# print(response)

import requests
from bs4 import BeautifulSoup

url = "https://www.moneycontrol.com/india/stockpricequote/it-software/tcs/TCS"
headers = {"User-Agent": "Mozilla/5.0"}

res = requests.get(url, headers=headers)
soup = BeautifulSoup(res.text, "html.parser")

def get_text(selector):
    el = soup.select_one(selector)
    return el.text.strip() if el else None

data = {
    "price": get_text(".inprice1"),
    "change": get_text(".nsecp"),
    "market_cap": get_text("#mktcap"),
    "pe": get_text("#pe"),
    "pb": get_text("#pb"),
    "roe": get_text("#roe"),
}
print(data)