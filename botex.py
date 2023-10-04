import telegram.ext
import telegram
from telegram.ext import CommandHandler
import requests
import json
import time
#from tracker import get_prices
import asyncio
from translate import Translator
from bs4 import BeautifulSoup
from decouple import config



print('bot is starting...')
time.sleep(2)

# enter below your telegram bot token you find in the "botfather".
bot_token = config('BOT_TOKEN')
bot = telegram.Bot(token=bot_token)
updater = telegram.ext.Updater(bot_token, use_context=True)

#updater = telegram.ext.Updater(token=bot_token, use_context=True)
#updater = telegram.ext.Updater(bot_token, use_context=True)

print("API loaded correctly...")


latest_news = None
dispatcher = updater.dispatcher


async def get_latest_news():
    global latest_news, latest_news_link
    while True:
        url = 'https://cryptopotato.com/'
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        news_headlines = soup.find_all('div', {'class': 'media-body'})
        if news_headlines:
            current_latest_news = news_headlines[0].get_text().strip()
            current_latest_news_link = news_headlines[0].find('a')['href']
            if current_latest_news != latest_news:
                latest_news = current_latest_news
                latest_news_link = current_latest_news_link
                yield latest_news
            else:
                await asyncio.sleep(60)
        else:
            await asyncio.sleep(60)

async def send_message():
    async for latest_news in get_latest_news():
        translator = Translator(to_lang='pl')
        translation = translator.translate(latest_news)
        message = f"{translation}\n\n{latest_news_link}"
        try:
            last_message = bot.send_message(chat_id='@kryptopolska_pl', text=message, parse_mode='HTML', reply_to_message_id=85775)
        except telegram.error.BadRequest as e:
            # Handle the case when the original message was deleted
            last_message = bot.send_message(chat_id='@kryptopolska_pl', text=message, parse_mode='HTML')
        # Save the message ID so that we can reply to it next time
        message_thread_id = last_message.message_id
        await asyncio.sleep(60)



# function responsible for take by API coin price you want to get to know.
def get_price(symbol):
    url = f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD"
    response = requests.get(url)
    if response.status_code == 200:
        data = json.loads(response.content)
        if "USD" in data:
            return data["USD"]
        else:
            return None
    else:
        return None

# function that takes your message from telegram e.g if you write /eth function takes it and send it to the symbol.
def handle_message(update, context):
    if update.message:
        message = update.message.text
        if message.startswith("/"):
            symbol = message.split(" ")[0][1:].upper()
            if symbol == "gpu":
                gpu(update, context)
            else:
                price = get_price(symbol)
                if price:
                    chat_id = update.message.chat_id
                    context.bot.send_message(chat_id=chat_id, text=f"{symbol} ${price}")
                    print(f"{symbol} ${price}")
                else:
                    chat_id = update.message.chat_id
                    context.bot.send_message(chat_id=chat_id, text=f"Przepraszam, nie mogłem znaleźć kryptowaluty, którą napisałeś, proszę napisz jeszcze raz poprawnie albo istnieje szansa, że po prostu nie mam jej w swojej bazie danych.")
        else:
            pass




def show_24_gecko_coins(update, context):
    chat_id = update.effective_chat.id

    views_url_24 = 'https://api.coingecko.com/api/v3/search/trending'
    response = requests.get(views_url_24)
    data = response.json()
    trending_coins = data['coins']
    trending_coins.sort(key=lambda coin: coin['item']['market_cap_rank'])

    message = "<code>Top-7 najpopularniejszych monet na CoinGecko, wyszukiwanych przez użytkowników w ciągu ostatnich 24 godzin (w kolejności od najbardziej popularnej do najmniej popularnej):\n</code>"
    for i, coin in enumerate(trending_coins[:7]):
        name = coin['item']['name']
        symbol = coin['item']['symbol']
        rank = coin['item']['market_cap_rank']

        message += f'{i+1}. {name} ({symbol}) CoinGecko rank:{rank}\n'
        
    context.bot.send_message(chat_id=chat_id, text=message, parse_mode='HTML')

dispatcher.add_handler(CommandHandler("top7", show_24_gecko_coins))
updater.start_polling()





def companies_btc(update, context):
    chat_id = update.effective_chat.id
    url = "https://api.coingecko.com/api/v3/companies/public_treasury/bitcoin"

    response = requests.get(url)
    data = response.json()

    message = "<code>udziały spółek publicznych w BTC (uporządkowane według całkowitych udziałów malejąco):\n</code>"
    for company in data["companies"]:
        name = company["name"]
        symbol = company["symbol"]
        country = company["country"]
        total_holdings = company["total_holdings"]

        message += f'<b>Firma:</b> {name}\n'
        message += f'<b>Skrót:</b> {symbol}\n'
        message += f'<b>Kraj:</b> {country}\n'
        message += f'<b>Ilość:</b> {total_holdings} BTC\n\n'

    context.bot.send_message(chat_id=chat_id, text=message, parse_mode='HTML')

dispatcher.add_handler(CommandHandler("spolki", companies_btc))
updater.start_polling()





def get_mining_data():
    url = "https://whattomine.com/coins.json"
    response = requests.get(url)
    mining_data = []

    if response.status_code == 200:
        data = response.json()

        for coin in data["coins"].values():
            tag = coin["tag"]
            profitability24 = coin["profitability24"]
            market_cap = coin["market_cap"]
            algorithm = coin["algorithm"]

            mining_data.append((tag, profitability24, market_cap, algorithm))

    return mining_data

# funkcja obsługi dla komendy "/miner"
def mine(update, context):
    chat_id = update.effective_chat.id
    chat_type = update.effective_chat.type

    # check if the chat is a group
    if chat_type == "group" or chat_type == "supergroup":
        mining_data = get_mining_data()
        message = ""

        for tag, profitability24, market_cap, algorithm in mining_data:
            message += f"Moneta: {tag}\n"
            message += f"Profil 24h: {profitability24}\n"
            message += f"Market Cap: ${market_cap}\n"
            message += f"Algorytm do kopania: {algorithm}\n\n"

        message_parts = split_message(message)
        for part in message_parts:
            context.bot.send_message(chat_id=chat_id, text=part, reply_to_message_id=86069)
    else:
        context.bot.send_message(chat_id=chat_id, text="Komenda /miner dostępna jest tylko w grupach.")


def split_message(message, max_length=4096):
    return [message[i:i + max_length] for i in range(0, len(message), max_length)]

def get_gpu_data():
    url = "https://whattomine.com/gpus"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    table = soup.find('table', {'class': 'table table-sm table-hover table-vcenter border-top'})
    rows = table.find_all('tr', {'data-test': 'gpu-row'})

    gpu_data = []

    for row in rows:
        cells = row.find_all('td')
        if len(cells) >= 10:
            gpu_name = cells[0].get_text().strip()
            gpu_release_date = cells[1].get_text().strip()
            gpu_hashrate = cells[2].get_text().strip()
            gpu_power = cells[3].get_text().strip()
            gpu_price = cells[4].get_text().strip()
            gpu_break_even = cells[5].get_text().strip()
            gpu_daily_profit = cells[6].get_text().strip()
            gpu_daily_electricity = cells[7].get_text().strip()
            gpu_best_algorithm = cells[8].get_text().strip()
            gpu_best_profit = cells[9].get_text().strip()

            gpu_data.append((gpu_name, gpu_release_date, gpu_hashrate, gpu_power, gpu_price, gpu_break_even, gpu_daily_profit, gpu_daily_electricity, gpu_best_algorithm, gpu_best_profit))

    return gpu_data



def gpu(update, context):
    chat_id = update.effective_chat.id
    chat_type = update.effective_chat.type

    # sprawdź, czy czat jest grupą
    if chat_type == "group" or chat_type == "supergroup":
        gpu_data = get_gpu_data()
        message = ""

        for gpu in gpu_data:
            message += f"<b>{gpu[0]}</b> ({gpu[1]})\n"
            message += f"Hashrate: {gpu[2]}\n"
            message += f"Power: {gpu[3]}\n"
            message += f"Price: {gpu[4]}\n"
            message += f"Break Even: {gpu[5]}\n"
            message += f"Daily Profit: {gpu[6]}\n"
            message += f"Daily Electricity: {gpu[7]}\n"
            message += f"Best Algorithm: {gpu[8]}\n"
            message += f"Best Profit: {gpu[9]}\n\n"

            context.bot.send_message(chat_id=chat_id, text=message, reply_to_message_id=86069, parse_mode='HTML')
    else:
        context.bot.send_message(chat_id=chat_id, text="Komenda /gpu dostępna jest tylko w grupach.")


dispatcher.add_handler(CommandHandler("gpu", gpu))
updater.start_polling()


# dodaj handler dla "/mine"

dispatcher.add_handler(CommandHandler("miner", mine))
updater.start_polling()


# Add the error handler to the dispatcher
dp = updater.dispatcher

# main function.
# remember if bot at the start printing "Timed out, trying again..." please remove your bot from a telegram group.
def main():
    dp.add_handler(telegram.ext.CommandHandler("top", show_24_gecko_coins))
    dispatcher.add_handler(CommandHandler("gpu", gpu))
    
    dispatcher.add_handler(CommandHandler("miner", mine))
    dispatcher.add_handler(CommandHandler("spolki", companies_btc))

    dp.add_handler(telegram.ext.MessageHandler(telegram.ext.Filters.text, handle_message))
    asyncio.run(send_message())

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()



'''





asyncio.run(send_message())


'''