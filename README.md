Telegram Crypto Bot

This bot provides various functionalities related to cryptocurrency. It fetches the latest news, coin prices, trending coins on CoinGecko, company holdings in BTC, and GPU mining data.
Features:

    Latest News: Fetches the latest news from cryptopotato.com and translates it to Polish before sending it to a specified Telegram channel.
    Coin Price: Retrieves the current price of a specified cryptocurrency in USD.
    Trending Coins on CoinGecko: Displays the top 7 trending coins on CoinGecko based on user searches in the last 24 hours.
    Company BTC Holdings: Shows the BTC holdings of various public companies.
    GPU Mining Data: Provides details about various GPUs, their hashrates, power consumption, price, profitability, and more.
    Error Handling: The bot is equipped to handle various errors and exceptions.

Setup:

    Environment Setup: Store your Telegram bot token in an .env file with the key BOT_TOKEN. Use the decouple library to access it in the code.

    Example:

    makefile

BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN

Dependencies: Install the required libraries using pip:

bash

pip install telegram requests json asyncio translate bs4 python-decouple

Running the Bot: Simply run the main Python script to start the bot:

bash

    python your_script_name.py

Usage:

    /top7: Show the top 7 trending coins on CoinGecko.
    /spolki: Display BTC holdings of various public companies.
    /gpu: Get GPU mining data.
    /miner: Display mining data for various coins.
    /[coin_symbol]: Get the current price of the specified coin in USD. For example, /eth will return the current price of Ethereum in USD.

Note:

    Ensure that the bot token is kept secure and not exposed to the public.
    The bot is designed to work in group chats for some commands. Ensure you have the necessary permissions in the group to avoid any issues.
