import requests
from datetime import datetime
import pytz
import telegram

# Credentials
TELEGRAM_TOKEN = "7787144306:AAGQNw9vWDTwu5gTKqjahBOYpCNNDYvoCps"
CHAT_ID = "1833875678"
FINNHUB_API_KEY = "cV_58MxGkU53YPID3M7wqbFpThEDLo3T"

# Forex and crypto pairs
pairs = [
    "OANDA:EUR_USD", "OANDA:GBP_USD", "OANDA:USD_JPY", "BINANCE:BTCUSDT",
    "BINANCE:ETHUSDT", "OANDA:XAU_USD", "OANDA:XAG_USD", "OANDA:AUD_USD",
    "OANDA:USD_CAD", "OANDA:NZD_USD"
]

# Timeframes (in minutes): 15m, 1h, 4h
timeframes = ["15", "60", "240"]

def fetch_candles(symbol, resolution):
    if "BINANCE" in symbol:
        url = f"https://finnhub.io/api/v1/crypto/candle?symbol={symbol}&resolution={resolution}&count=100&token={FINNHUB_API_KEY}"
    else:
        url = f"https://finnhub.io/api/v1/forex/candle?symbol={symbol}&resolution={resolution}&count=100&token={FINNHUB_API_KEY}"
    response = requests.get(url)
    data = response.json()
    if data.get("s") == "ok":
        return [
            {"t": t, "o": o, "h": h, "l": l, "c": c, "v": v}
            for t, o, h, l, c, v in zip(data["t"], data["o"], data["h"], data["l"], data["c"], data["v"])
        ][::-1]  # reverse to get latest first
    return []

def detect_bullish_engulfing(candles):
    if len(candles) < 3:
        return None
    c1, c2 = candles[0], candles[1]
    if c2["c"] < c2["o"] and c1["c"] > c1["o"]:
        if c1["o"] < c2["c"] and c1["c"] > c2["o"]:
            return "Bullish Engulfing"
    return None

def run_screener():
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist).strftime("%d %b %Y, %H:%M IST")

    for tf in timeframes:
        for symbol in pairs:
            candles = fetch_candles(symbol, tf)
            pattern = detect_bullish_engulfing(candles)
            if pattern:
                entry = candles[0]["c"]
                sl = round(entry - 20, 2)
                tp = round(entry + 30, 2)
                display_name = symbol.split(":")[-1].replace("_", "/").replace("USDT", "/USD")

                message = f"""
🔔 {display_name} ({tf} min)
🧩 Pattern: {pattern}
📍 Entry: {entry} | SL: {sl} | TP: {tp}
📆 Time: {now}
📌 Sans D Fx Trader
"""
                bot.send_message(chat_id=CHAT_ID, text=message.strip())
