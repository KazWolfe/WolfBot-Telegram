# WolfBot
WolfBot is a relatively simple chatbot created for the popular messaging platform [Telegram](https://telegram.org/).

It was designed to help out a single chat, but it has since expanded into doing a few interesting and unique things, especially for the world of Pokemon GO. It is my sincere hope that you find WolfBot useful.

A running implementation of WolfBot is available at the username `@AwooBot` on Telegram. Feel free to add it and play with it as much as you like.

## Setting up the Bot

If you want to run your own instance of the bot, I've got you covered. Follow these steps, and it *should* work.

1. Install the `telepot` package through `pip`.
2. Get a Telegram API key from Botfather on Telegram.
3. Get your current User ID for Telegram. @AwooBot's /getinfo command can help you with this.
4. Copy the `core.example.json` file in the `config/` folder to `core.json`.
5. Replace all necessary values with your settings.
6. Run WolfBot by running the `AwooCore.py` file.
