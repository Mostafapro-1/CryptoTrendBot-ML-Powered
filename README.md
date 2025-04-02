This is a simplified version of my crypto trading bot featuring core functionality.
For the full version (including advanced prediction and live trading features)
text me   :)

 

So How does the Bot function?

1. Data Collection:
The bot uses the Binance API to fetch historical candlestick data (klines) for the cryptocurrency pair over the past year.
I used Pandas and NumPy to handle and manipulate time-series data. 

2. Price Analysis:
Using historical data collected, the bot calculates the mean and standard deviation of the closing prices. The logic is simple: if the latest closing price is below (mean – standard deviation), the bot considers it a potential "buy" opportunity otherwise, it advises to "wait". 

3.Price Prediction:
Implemented a dummy prediction model using TensorFlow and Keras. The model uses the last 30 closing prices and a simple neural network (with one hidden Dense layer) to predict the price for the next 24 hours. Although it’s a basic model (for demo purposes), it illustrates the potential for integrating more advanced ML techniques.

4.Telegram Integration:
The bot interacts with user via Telegram commands:
/start: Initializes the bot and sends an immediate market analysis.
/buy: Executes a market buy order.
/sell: Executes a market sell order.
Built using the python-telegram-bot library .

5. Automated Analysis:
Uses APScheduler to schedule hourly market analyses and push notifications to Telegram. 

Why These Libraries?
Binance API & python-binance: fetching real-time and historical market data.

Pandas & NumPy: Powerful tools for data manipulation.

TensorFlow & Keras: for building and training predictive models.

python-telegram-bot: making the bot interactive using Telegram messaging.

APScheduler: Allows scheduling of tasks.

Logging & Datetime: to track bot activity and handle time-related data accurately.

