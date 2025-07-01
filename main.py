from flask import Flask, request, jsonify
import yfinance as yf
import requests

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
