from flask import Flask, request, jsonify
import yfinance as yf
import requests
import pandas as pd
import tempfile

app = Flask(__name__)

@app.route("/test")
def test():
    return jsonify({
        "Service-Status":"OK"
    })

@app.route("/")
def home():
    return jsonify({
        "message": "Welcome to the Stock + Mutual Fund API",
        "endpoints": {
            "/price": "GET with ?symbol= (AAPL, RELIANCE.BO, VTSAX, etc.)",
            "/mf": "GET with ?code= (Indian Mutual Fund Scheme Code like 120503)",
            "/mflist":"GET all MF list"
        }
    })

@app.route("/insharelist")
def getsharelistin():
    csv_url = "https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv"
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp_file:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Accept": "text/csv,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.nseindia.com/",
            "Origin": "https://www.nseindia.com",
            "Connection": "keep-alive"
        }
        response = requests.get(csv_url, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch CSV: {response.status_code}")
        response.raise_for_status()
        tmp_file.write(response.content)
        temp_path = tmp_file.name

    df = pd.read_csv(temp_path,usecols=[0, 1])
    json_data = df.to_dict(orient='records')
    return jsonify(json_data)

@app.route("/ussharelist")
def getsharelistus():
    url = "https://datahub.io/core/nasdaq-listings/r/nasdaq-listed-symbols.csv"
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp_file:
        headers = {
            "User-Agent": "Mozilla/5.0",  # NSE may require a browser-like user agent
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        tmp_file.write(response.content)
        temp_path = tmp_file.name
        
    df = pd.read_csv(temp_path,usecols=[0, 1])
    json_data = df.to_dict(orient='records')
    return jsonify(json_data)

# ────── STOCK PRICE (US & INDIAN + US MF) ──────
@app.route("/price", methods=["GET"])
def get_price():
    symbol = request.args.get("symbol")
    if not symbol:
        return jsonify({"error": "Missing 'symbol' parameter"}), 400

    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1d")
        if data.empty:
            return jsonify({"error": "Invalid or unsupported symbol"}), 404

        price = data['Close'].iloc[-1]
        return jsonify({
            "symbol": symbol,
            "price": round(price, 2)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ────── INDIAN MUTUAL FUND NAV (FROM AMFI) ──────
@app.route("/mf", methods=["GET"])
def get_mf_nav():
    scheme_code = request.args.get("code")
    if not scheme_code:
        return jsonify({"error": "Missing 'code' (scheme_code) parameter"}), 400

    url = "https://www.amfiindia.com/spages/NAVAll.txt"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch NAV data"}), 500

        lines = response.text.splitlines()
        for line in lines:
            if line.startswith(scheme_code + ";"):
                parts = line.split(";")
                return jsonify({
                    "scheme_code": scheme_code,
                    "scheme_name": parts[2],
                    "nav": parts[4],
                    "date": parts[5],
                    "fund_name":parts[3]
                })
        return jsonify({"error": "Scheme code not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ────── INDIAN MUTUAL FUND NAV (FROM AMFI) ──────
@app.route("/mflist", methods=["GET"])
def getmflist():
    url = "https://www.amfiindia.com/spages/NAVAll.txt"
    response = requests.get(url)

    lines = response.text.splitlines()
    funds = []

    for line in lines:
        parts = line.split(";")
        if len(parts) >= 5 and parts[0].isdigit():
            funds.append({
                 "scheme_code": parts[0],
                    "scheme_name": parts[2],
                    "nav": parts[4],
                    "date": parts[5],
                    "fund_name":parts[3]
            })

    return funds

def creteApp():
    app.run(host='0.0.0.0',port=4444)
    #app.run(debug=True)
