import datetime
import requests
import pandas as pd

API_KEY = "YOUR_POLYGON_API_KEY"

symbols = {
    "C:EURUSD": "EUR/USD", "C:GBPUSD": "GBP/USD", "C:USDJPY": "USD/JPY",
    "C:USDCHF": "USD/CHF", "C:USDCAD": "USD/CAD", "C:AUDUSD": "AUD/USD",
    "C:NZDUSD": "NZD/USD", "X:BTCUSD": "BTC/USD", "X:ETHUSD": "ETH/USD",
    "X:XAUUSD": "XAU/USD", "X:XAGUSD": "XAG/USD"
}

def fetch_polygon_data(ticker):
    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/15/minute/2023-01-01/{datetime.datetime.utcnow().strftime('%Y-%m-%d')}?adjusted=true&limit=100&apiKey={API_KEY}"
    r = requests.get(url)
    if r.status_code != 200 or "results" not in r.json():
        return None
    data = r.json()["results"]
    df = pd.DataFrame(data)
    df["t"] = pd.to_datetime(df["t"], unit="ms")
    df = df.rename(columns={"o": "Open", "h": "High", "l": "Low", "c": "Close"})
    return df[["t", "Open", "High", "Low", "Close"]]

def detect_patterns(df):
    if df is None or len(df) < 3:
        return []

    alerts = []
    last, prev = df.iloc[-1], df.iloc[-2]

    # Bullish Engulfing + lower BB logic
    if prev["Close"] < prev["Open"] and last["Close"] > last["Open"] and \
       last["Close"] > prev["Open"] and last["Open"] < prev["Close"]:
        if last["Close"] < df["Close"].rolling(20).mean().iloc[-1]:  # lower BB approx
            alerts.append("🚀 Bullish Engulfing near Lower Bollinger Band")

    # Bearish Engulfing + upper BB logic
    if prev["Close"] > prev["Open"] and last["Close"] < last["Open"] and \
       last["Open"] > prev["Close"] and last["Close"] < prev["Open"]:
        if last["Close"] > df["Close"].rolling(20).mean().iloc[-1]:  # upper BB approx
            alerts.append("📉 Bearish Engulfing near Upper Bollinger Band")

    # Pin Bar at Support (bullish)
    if last["Low"] < df["Low"].rolling(10).min().iloc[-2] and \
       (last["Close"] - last["Open"]) > abs(last["Open"] - last["Low"]):
        alerts.append("📍 Bullish Pin Bar at Support")

    # Pin Bar at Resistance (bearish)
    if last["High"] > df["High"].rolling(10).max().iloc[-2] and \
       (last["Open"] - last["Close"]) > abs(last["High"] - last["Close"]):
        alerts.append("📍 Bearish Pin Bar at Resistance")

    return alerts

def run_screener():
    messages = []
    for ticker, name in symbols.items():
        df = fetch_polygon_data(ticker)
        patterns = detect_patterns(df)
        if patterns:
            price = df["Close"].iloc[-1]
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            msg = f"<b>{name} - 15min Alert</b>\nPrice: {price:.4f}\nTime: {timestamp}\n\n"
            msg += "\n".join(patterns)
            msg += "\n\n📌 Sans D Fx Trader"
            messages.append(msg)
    return messages
