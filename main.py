import sys
import os
from telegram_bot import AsyncTelegramBot
from dotenv import load_dotenv

# get bot API key
load_dotenv()
API_KEY = os.getenv("API_KEY")


def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <link>")
    else:
        arg1 = sys.argv[1]
        bot = AsyncTelegramBot(API_KEY, arg1)
        bot.start_bot()


if __name__ == "__main__":
    main()
