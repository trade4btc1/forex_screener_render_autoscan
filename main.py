import time
from screener import run_screener
from telegram.ext import Updater, CommandHandler

TELEGRAM_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
CHAT_ID = 'YOUR_CHAT_ID'

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="📈 Forex Screener Bot Started!")

def scan(update, context):
    alerts = run_screener()
    if alerts:
        for alert in alerts:
            context.bot.send_message(chat_id=update.effective_chat.id, text=alert)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="No valid signals at this time.")

def main():
    updater = Updater(token=TELEGRAM_TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("scan", scan))

    updater.start_polling()
    print("Bot is polling...")
    updater.idle()

if __name__ == '__main__':
    while True:
        run_screener()
        time.sleep(900)  # 15 minutes