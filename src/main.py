import os, json
import logging
import requests
from telegram.ext import Application, CommandHandler

config = json.load(open("config.json"))
token = config['token']
coinMarketCapKey = config['coinMarketCapKey']

# Create a new Telegram bot.
app = Application.builder().token(token).build()
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Define a function to handle the /start command
async def start(update, context):
    await update.message.reply_text('To use this bot, enter the /crypto command with the name or symbol of the crypto asset')

# Define a function to handle the /crypto command.
async def crypto(update, context):
    # Get the input crypto asset from the user.
    asset = " ".join(context.args).lower()

    # coinmarketcap headers
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': coinMarketCapKey,
    }

    # Fetch the latest data for the asset from CoinMarketCap.
    response = requests.get(f'https://pro-api.coinmarketcap.com/v1/cryptocurrency/symbol{asset}', headers=headers)
    print(response.json())

    if response.json()['status']['error_code'] != 200 or response.json()['status']['error_code'] != 00:
        await update.message.reply_text('Error fetching data from CoinMarketCap.')
        # context.bot.send_message(chat_id=update.effective_chat.id, text='Error fetching data from CoinMarketCap.')
        return

    # Parse the JSON response and extract the data for the asset.
    print(response.json())
    data = response.json()['data'][0]
    name = data['name']
    symbol = data['symbol']
    price = data['metrics']['price']['usd']
    market_cap = data['metrics']['marketcap']['usd']
    change_24h = data['metrics']['priceChangePercentage24H']
    rank = data['rank']

    # Send a message with the data for the asset.
    message = f"Name: {name}\nSymbol: {symbol}\nRank: {rank}\nPrice: ${price:.2f}\nMarket Cap: ${market_cap:.2f}\n24h Change: {change_24h:.2f}%\n\n"

    # Get the latest news for the asset from CoinMarketCap.
    news_response = requests.get(f'https://api.coinmarketcap.com/content/v3/news?coins={symbol}')
    if news_response.status_code == 200:
        news_data = news_response.json()
        if news_data['totalCount'] > 0:
            message += "Latest News:\n"
            for article in news_data['data']:
                title = article['meta']['title']
                url = article['meta']['sourceUrl']
                message += f"- {title}\n{url}\n"
            message += "\n"

    # Get the latest tweets for the asset from Twitter.
    twitter_response = requests.get(f'https://api.coinmarketcap.com/data-api/v3/cmc/social/posts?coinId={data["id"]}&socialNetworks=TWITTER')
    if twitter_response.status_code == 200:
        twitter_data = twitter_response.json()
        if twitter_data['postsCount'] > 0:
            message += "Latest Tweets:\n"
            for tweet in twitter_data['posts']:
                text = tweet['content']
                url = tweet['linkUrl']
                message += f"- {text}\n{url}\n"
            message += "\n"

    context.bot.send_message(chat_id=update.effective_chat.id, text=message)


crypto_handler = CommandHandler('crypto', crypto)
app.add_handler(crypto_handler)
start_handler = CommandHandler('start', start)
app.add_handler(start_handler)


app.run_polling()
# updater.idle()
