# 📈 Stock + Mutual Fund API (Flask + yfinance + AMFI + NSE)

A lightweight REST API built with Flask to serve real-time and historical stock/mutual fund data from:

- Yahoo Finance (via yfinance) for stocks and US mutual funds
- NSE India for Indian equity list
- AMFI India for Indian mutual fund NAVs

---

## 🚀 Features

| Endpoint             | Description                                                                 |
|----------------------|-----------------------------------------------------------------------------|
| `/test`              | Health check endpoint                                                       |
| `/`                  | Welcome message with available endpoints                                    |
| `/price?symbol=`     | Get current stock price or US MF NAV using yfinance                         |
| `/mf?code=`          | Get Indian mutual fund NAV using AMFI Scheme Code                           |
| `/mflist`            | Get the full list of Indian mutual funds with NAVs                          |
| `/insharelist`       | Get current list of Indian equity stocks (NSE)                              |
| `/ussharelist`       | Get list of US stocks (NASDAQ-listed companies from DataHub)                |

---

## 🧰 Tech Stack

- Python 3.x
- Flask
- yfinance
- requests
- pandas
- tempfile (for reading remote CSVs)

---

## 📦 Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/yourname/stock-mf-api.git
cd stock-mf-api
