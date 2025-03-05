"""
Lite Version of Crypto Trading Bot
------------------------------------
This is a simplified version of my crypto trading bot featuring core functionality.
For the full version (including advanced prediction and live trading features),
text me  :)
"""

import logging
import datetime
import numpy as np
import pandas as pd
from binance.client import Client
from binance.exceptions import BinanceAPIException
import pytz 
from telegram.ext import Updater, CommandHandler
from apscheduler.schedulers.background import BackgroundScheduler

# ---------------- Configuration ----------------
# Replace the placeholders with your own API keys (or set them as environment variables)
BINANCE_API_KEY = 
BINANCE_API_SECRET = 
TELEGRAM_BOT_TOKEN = 
SYMBOL =   # Example symbol
LOOKBACK_DAYS =   

# ---------------- Initialize Clients ----------------
client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)
global_chat_id = None  # Will be set when a user starts the bot

# ---------------- Logging ----------------
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

# ---------------- Binance Data Functions ----------------
def fetch_historical_data(symbol, interval, lookback):
    """
    Fetch historical kline (candlestick) data from Binance.
    """
    end_time = datetime.datetime.now()
    start_time = end_time - datetime.timedelta(days=lookback)
    start_str = start_time.strftime("%d %b, %Y")
    try:
        klines = client.get_historical_klines(symbol, interval, start_str)
        data = pd.DataFrame(klines, columns=[
            'Open time', 'Open', 'High', 'Low', 'Close', 'Volume',
            'Close time', 'Quote asset volume', 'Number of trades',
            'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'
        ])
        data['Open time'] = pd.to_datetime(data['Open time'], unit='ms')
        data['Close time'] = pd.to_datetime(data['Close time'], unit='ms')
        numeric_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        data[numeric_cols] = data[numeric_cols].astype(float)
        return data
    except BinanceAPIException as e:
        logging.error(f"Error fetching historical data: {e}")
        return None

# ---------------- Analysis Function ----------------
def analyze_price(data):
    """
    Perform a basic analysis on historical data.
    Determines if the current price is below an arbitrary threshold.
    """
    if data is None or data.empty:
        return None
    latest_close = data['Close'].iloc[-1]
    mean_price = data['Close'].mean()
    std_price = data['Close'].std()
    threshold = mean_price - std_price
    recommendation = "buy" if latest_close < threshold else "wait"
    return {
        "latest_price": latest_close,
        "mean_price": mean_price,
        "std_price": std_price,
        "threshold": threshold,
        "recommendation": recommendation
    }

# ---------------- Placeholder Prediction Function ----------------
def predict_price_next_24h(data):
    """
    [LITE VERSION]
    Dummy function for price prediction.
    For the full model, text me for full code!
    """
    return 0.0  # Returns a dummy value

# ---------------- Telegram Messaging ----------------
def send_telegram_message(bot, chat_id, message):
    bot.send_message(chat_id=chat_id, text=message)

# ---------------- Scheduled Analysis ----------------
def scheduled_analysis(context):
    global global_chat_id
    if global_chat_id is None:
        logging.info("No Telegram chat_id available. Skipping scheduled analysis.")
        return
    data = fetch_historical_data(SYMBOL, Client.KLINE_INTERVAL_1DAY, LOOKBACK_DAYS)
    analysis = analyze_price(data)
    if analysis is None:
        return
    message = (
        f"Analysis for {SYMBOL}:\n"
        f"Latest Price: {analysis['latest_price']:.8f}\n"
        f"Mean Price: {analysis['mean_price']:.8f}\n"
        f"Std Dev: {analysis['std_price']:.8f}\n"
        f"Threshold (Mean - Std): {analysis['threshold']:.8f}\n"
        f"Recommendation: {analysis['recommendation'].upper()}\n"
        "Lite version. Text me for the full code!"
    )
    context.bot.send_message(chat_id=global_chat_id, text=message)

# ---------------- Telegram Command Handlers ----------------
def start(update, context):
    """
    /start command: Initializes the bot and stores the chat_id.
    """
    global global_chat_id
    global_chat_id = update.effective_chat.id
    update.message.reply_text(
        f"Bot started and monitoring {SYMBOL}.\nThis is the lite version. Text me for full code!"
    )
    # Perform an immediate analysis upon start
    data = fetch_historical_data(SYMBOL, Client.KLINE_INTERVAL_1DAY, LOOKBACK_DAYS)
    analysis = analyze_price(data)
    if analysis:
        message = (
            f"Analysis for {SYMBOL}:\n"
            f"Latest Price: {analysis['latest_price']:.8f}\n"
            f"Mean Price: {analysis['mean_price']:.8f}\n"
            f"Std Dev: {analysis['std_price']:.8f}\n"
            f"Threshold (Mean - Std): {analysis['threshold']:.8f}\n"
            f"Recommendation: {analysis['recommendation'].upper()}\n"
            "Lite version. Text me for the full code!"
        )
        update.message.reply_text(message)

def buy(update, context):
    """
    /buy command: Executes a market buy order.
    [LITE VERSION: Functionality not available]
    """
    update.message.reply_text(" Text me for full code!")

def sell(update, context):
    """
    /sell command: Executes a market sell order.
    [LITE VERSION: Functionality not available]
    """
    update.message.reply_text(" Text me for full code!")

# ---------------- Main Function ----------------
def main():
    # Set up Telegram updater and dispatcher
    updater = Updater(TELEGRAM_BOT_TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("buy", buy))
    dp.add_handler(CommandHandler("sell", sell))

    # Set up a scheduler for periodic analysis (e.g., every hour)
    scheduler = BackgroundScheduler(timezone=pytz.utc)
    scheduler.add_job(lambda: scheduled_analysis(updater), 'interval', hours=1)
    scheduler.start()

    # Start the Telegram bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
