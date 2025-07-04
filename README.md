# 📈 Stock + Mutual Fund API (IN & US)

A lightweight REST API built with Flask to serve real-time and historical stock/mutual fund data from:

- In Stocks and US Stocks
- NSE/BSE India for Indian equity list
- Indian mutual fund NAVs

---

## 🚀 Features

| Endpoint             | Description                                                                 |
|----------------------|-----------------------------------------------------------------------------|
| `/test`              | Health check endpoint                                                       |
| `/`                  | Welcome message with available endpoints                                    |
| `/price?symbol=`     | Get current stock price or US MF NAV                                        |
| `/mf?code=`          | Get Indian mutual fund NAV using AMFI Scheme Code                           |
| `/mflist`            | Get the full list of Indian mutual funds with NAVs                          |
| `/insharelist`       | Get current list of Indian equity stocks (NSE/BSE)                          |
| `/ussharelist`       | Get list of US stocks                                                       |

---

### 1. Clone the repository

```bash
git clone https://github.com/yourname/stock-mf-api.git
```
### Test API
```bash
https://stock-api-python.onrender.com/
```
