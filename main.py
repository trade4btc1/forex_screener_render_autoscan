from flask import Flask
import threading
from screener import run_screener
from telegram import Bot
import os

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
bot = Bot(token=BOT_TOKEN)

def send_alert_to_telegram(message):
    bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="HTML")

@app.route('/')
def home():
    return "🟢 Screener Bot is running."

@app.route('/scan')
def scan():
    results = run_screener()
    for msg in results:
        send_alert_to_telegram(msg)
    return "✅ Scan Complete"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
import os
import time
import datetime
import threading
from screener import run_screener
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext

BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

bot = Bot(token=BOT_TOKEN)

def send_alert_to_telegram(message):
    bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="HTML")

def auto_scan_loop():
    while True:
        print("⏳ Auto scan started")
        results = run_screener()
        for msg in results:
            send_alert_to_telegram(msg)
        print("✅ Auto scan complete. Sleeping for 15 mins.")
        time.sleep(900)  # 15 minutes

def start(update: Update, context: CallbackContext):
    update.message.reply_text("✅ Bot is live! Use /scan to manually trigger.")

def scan(update: Update, context: CallbackContext):
    update.message.reply_text("🔍 Manual scan started...")
    results = run_screener()
    for msg in results:
        bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="HTML")
    update.message.reply_text("✅ Manual scan complete.")

def main():
    threading.Thread(target=auto_scan_loop, daemon=True).start()

    updater = Updater(token=BOT_TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("scan", scan))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
