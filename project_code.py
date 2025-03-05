import logging
import datetime
import numpy as np
import pandas as pd
from binance.client import Client
from binance.exceptions import BinanceAPIException
import pytz 
from telegram.ext import Updater, CommandHandler
from apscheduler.schedulers.background import BackgroundScheduler
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

# ---------------- Configuration ----------------
BINANCE_API_KEY = ' '
BINANCE_API_SECRET = ' '
TELEGRAM_BOT_TOKEN = ' '
SYMBOL = ' '  # symbol 
LOOKBACK_DAYS =   

# ---------------- Initialize Clients ----------------
client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)
# Global variable to store the Telegram chat ID
global_chat_id = None

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

# ---------------- Analysis & Prediction ----------------
def analyze_price(data):
   
    if data is None or data.empty:
        return None
    latest_close = data['Close'].iloc[-1]
    mean_price = data['Close'].mean()
    std_price = data['Close'].std()
    threshold = mean_price - std_price  # An arbitrary threshold
    recommendation = "buy" if latest_close < threshold else "wait"
    analysis_details = {
        "latest_price": latest_close,
        "mean_price": mean_price,
        "std_price": std_price,
        "threshold": threshold,
        "recommendation": recommendation
    }
    return analysis_details

def predict_price_next_24h(data):
    """
    Predict the next 24h price using a simple TensorFlow model.
    (Note: This is a dummy model for demonstration purposes.)
    """
    recent_data = data['Close'].tail(30).values
    x = np.arange(len(recent_data)).reshape(-1, 1)
    y = recent_data.reshape(-1, 1)
    
    # Define a simple model
    model = Sequential()
    model.add(Dense(10, input_dim=1, activation='relu'))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mean_squared_error')
    
    # Train the model briefly (in real use, you would train offline and load a saved model)
    model.fit(x, y, epochs=100, verbose=0)
    
    next_index = np.array([[len(recent_data)]])
    predicted_price = model.predict(next_index)
    return predicted_price[0][0]

# ---------------- Telegram Messaging ----------------
def send_telegram_message(bot, chat_id, message):
    bot.send_message(chat_id=chat_id, text=message)

# ---------------- Order Execution ----------------
def execute_buy_order(symbol, quantity):
    try:
        order = client.order_market_buy(symbol=symbol, quantity=quantity)
        return order
    except BinanceAPIException as e:
        logging.error(f"Buy order error: {e}")
        return None

def execute_sell_order(symbol, quantity):
    try:
        order = client.order_market_sell(symbol=symbol, quantity=quantity)
        return order
    except BinanceAPIException as e:
        logging.error(f"Sell order error: {e}")
        return None

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
        f"Latest Price: {float(analysis['latest_price']):.8f}\n"
        f"Mean Price: {analysis['mean_price']:.8f}\n"
        f"Std Dev: {analysis['std_price']:.8f}\n"
        f"Threshold (Mean - Std): {analysis['threshold']:.8f}\n"
        f"Recommendation: {analysis['recommendation'].upper()}"
    )
    # If recommendation is "buy", include a next 24h price prediction
    if analysis['recommendation'] == "buy":
        prediction = predict_price_next_24h(data)
        message += f"\nPredicted Price (next 24h): {prediction:.8f}"
    context.bot.send_message(chat_id=global_chat_id, text=message)

# ---------------- Telegram Command Handlers ----------------
def start(update, context):
    """
    /start command: Initializes the bot and stores the chat_id.
    """
    global global_chat_id
    global_chat_id = update.effective_chat.id
    update.message.reply_text(f"Bot started and monitoring {SYMBOL}.")
    
    # Optionally perform an immediate analysis on start-up
    data = fetch_historical_data(SYMBOL, Client.KLINE_INTERVAL_1DAY, LOOKBACK_DAYS)
    analysis = analyze_price(data)
    if analysis:
        message = (
        f"Analysis for {SYMBOL}:\n"
        f"Latest Price: {float(analysis['latest_price']):.8f}\n"
        f"Mean Price: {analysis['mean_price']:.8f}\n"
        f"Std Dev: {analysis['std_price']:.8f}\n"
        f"Threshold (Mean - Std): {analysis['threshold']:.8f}\n"
        f"Recommendation: {analysis['recommendation'].upper()}"
    )
        update.message.reply_text(message)

def buy(update, context):
    """
    /buy command: Executes a market buy order.
    """
    chat_id = update.effective_chat.id
    quantity = 1000  # Example quantity; adjust based on your strategy and account balance
    order = execute_buy_order(SYMBOL, quantity)
    if order:
        context.bot.send_message(chat_id=chat_id, text=f"Buy order executed:\n{order}")
    else:
        context.bot.send_message(chat_id=chat_id, text="Failed to execute buy order.")

def sell(update, context):
    """
    /sell command: Executes a market sell order.
    """
    chat_id = update.effective_chat.id
    quantity = 1000  # Example quantity; adjust accordingly
    order = execute_sell_order(SYMBOL, quantity)
    if order:
        context.bot.send_message(chat_id=chat_id, text=f"Sell order executed:\n{order}")
    else:
        context.bot.send_message(chat_id=chat_id, text="Failed to execute sell order.")

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
