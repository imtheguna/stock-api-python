from flask import Flask, request, jsonify
import yfinance as yf
import requests
import pandas as pd
import tempfile,datetime,os

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
            "/mflist": "GET all MF list",
            "/insharelist": "GET Indian equity master list",
            "/ussharelist": "GET US NASDAQ stock list"
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

        now = datetime.datetime.now()
        download_dir = "./data_cache"
        os.makedirs(download_dir, exist_ok=True)

        date_str = now.strftime("%Y%m%d")
        filename = f"EQUITY_L_{date_str}.csv"
        filepath = os.path.join(download_dir, filename)

        def file_is_older_than(filepath, minutes=60):
            if not os.path.exists(filepath):
                return True
            file_mtime = datetime.datetime.fromtimestamp(os.path.getmtime(filepath))
            age = now - file_mtime
            return age.total_seconds() > minutes * 60

        if file_is_older_than(filepath, 60):
            try:
                print('File Downloading '+filepath)
                response = requests.get(csv_url, headers=headers)
                response.raise_for_status()
                with open(filepath, "wb") as f:
                    f.write(response.content)
            except Exception as e:
                if os.path.exists(filepath):
                    # File exists, so reuse it silently on download failure
                    print('Reuse file ' + filename)
                else:
                    return jsonify({"error": f"Failed to download NSE CSV: {str(e)}"}), 503
        else:
            print('Reuse file ' + filename)

        try:
            df = pd.read_csv(filepath, usecols=[0, 1])
            json_data = df.to_dict(orient='records')
            return jsonify(json_data)
        except Exception as e:
            return jsonify({"error": "Failed to read cached CSV", "details": str(e)}), 500



@app.route("/ussharelist")
def getsharelistus():

    url = "https://datahub.io/core/nasdaq-listings/r/nasdaq-listed-symbols.csv"
    headers = {"User-Agent": "Mozilla/5.0"}

    now = datetime.datetime.now()
    download_dir = "./data_cache"
    os.makedirs(download_dir, exist_ok=True)

    today_str = now.strftime("%Y%m%d")
    today_file = os.path.join(download_dir, f"us_nasdaq_listings_{today_str}.csv")

    def file_is_older_than(filepath, minutes=60):
        if not os.path.exists(filepath):
            return True
        file_mtime = datetime.datetime.fromtimestamp(os.path.getmtime(filepath))
        age = now - file_mtime
        return age.total_seconds() > minutes * 60

    # Download if file doesn't exist or older than 1 hour
    if file_is_older_than(today_file, 60):
        try:
            print('File Downloading '+today_file)
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            with open(today_file, "wb") as f:
                f.write(response.content)
        except Exception as e:
            # If file exists already, ignore error and use cached file
            if os.path.exists(today_file):
                pass
            else:
                return jsonify({"error": f"Failed to fetch NASDAQ data: {str(e)}"}), 503
    else:
            print('Reuse file '+today_file)
    # At this point file should exist, else error
    if not os.path.exists(today_file):
        return jsonify({"error": "Data not available. Please try again later."}), 503

    # Read and return JSON data
    try:
        df = pd.read_csv(today_file, usecols=[0, 1])
        return jsonify(df.to_dict(orient='records'))
    except Exception as e:
        return jsonify({"error": f"Failed to read CSV: {str(e)}"}), 500


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

    now = datetime.datetime.now()
    download_dir = "./data_cache"
    os.makedirs(download_dir, exist_ok=True)
    date_str = now.strftime("%Y%m%d")
    filename = f"NAVAll_{date_str}.txt"
    filepath = os.path.join(download_dir, filename)

    def file_is_older_than(filepath, minutes=60):
        if not os.path.exists(filepath):
            return True
        file_mtime = datetime.datetime.fromtimestamp(os.path.getmtime(filepath))
        age = now - file_mtime
        return age.total_seconds() > minutes * 60

    if file_is_older_than(filepath, 60):
        try:
            print('Downloading file '+filepath)
            url = "https://www.amfiindia.com/spages/NAVAll.txt"
            response = requests.get(url)
            response.raise_for_status()
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(response.text)
        except Exception as e:
            if os.path.exists(filepath):
                print('Reuse file ' + filename)
            else:
                return jsonify({"error": str(e)}), 500
    else:
        print('Reuse file ' + filename)

    # Read and search the file
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for line in lines:
            if line.startswith(scheme_code + ";"):
                parts = line.strip().split(";")
                return jsonify({
                    "scheme_code": scheme_code,
                    "scheme_name": parts[2],
                    "nav": parts[4],
                    "date": parts[5],
                    "fund_name": parts[3]
                })

        return jsonify({"error": "Scheme code not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ────── INDIAN MUTUAL FUND NAV (FROM AMFI) ──────
@app.route("/mflist", methods=["GET"])
def getmflist():
    now = datetime.datetime.now()
    download_dir = "./data_cache"
    os.makedirs(download_dir, exist_ok=True)
    date_str = now.strftime("%Y%m%d")
    filename = f"NAVAll_{date_str}.txt"
    filepath = os.path.join(download_dir, filename)

    def file_is_older_than(filepath, minutes=60):
        if not os.path.exists(filepath):
            return True
        file_mtime = datetime.datetime.fromtimestamp(os.path.getmtime(filepath))
        age = now - file_mtime
        return age.total_seconds() > minutes * 60

    if file_is_older_than(filepath, 60):
        try:
            url = "https://www.amfiindia.com/spages/NAVAll.txt"
            response = requests.get(url)
            response.raise_for_status()
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(response.text)
        except Exception as e:
            if os.path.exists(filepath):
                print('Reuse file ' + filename)
            else:
                return jsonify({"error": f"Failed to download NAV data: {str(e)}"}), 503
    else:
        print('Reuse file ' + filename)

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()

        funds = []
        for line in lines:
            parts = line.strip().split(";")
            if len(parts) >= 6 and parts[0].isdigit():
                funds.append({
                    "scheme_code": parts[0],
                    "scheme_name": parts[2],
                    "nav": parts[4],
                    "date": parts[5],
                    "fund_name": parts[3]
                })

        return jsonify(funds)
    except Exception as e:
        return jsonify({"error": "Failed to read cached NAV data", "details": str(e)}), 500

def creteApp():
    app.run(host='0.0.0.0',port=4444)
    #app.run(debug=True)
