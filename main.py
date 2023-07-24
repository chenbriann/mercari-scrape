import sys
import os
from telegram_bot import AsyncTelegramBot
from sqlite_database import SQLiteHandler
from dotenv import load_dotenv

# get bot API key
load_dotenv()
API_KEY = os.getenv("API_KEY")


def main():
    if len(sys.argv) == 4:
        arg1 = sys.argv[1]
        arg2 = sys.argv[2]
        arg3 = sys.argv[3]

        # Initialize database handler
        db_handler = SQLiteHandler()

        bot = AsyncTelegramBot(API_KEY, db_handler, arg1, arg2, arg3)
        bot.start_bot()
    elif len(sys.argv) == 3:
        arg1 = sys.argv[1]
        arg2 = sys.argv[2]

        # Initialize database handler
        db_handler = SQLiteHandler()

        bot = AsyncTelegramBot(API_KEY, db_handler, arg1, arg2)
        bot.start_bot()
    else:
        print("Usage: python main.py <link> <scrapeinterval> <scrapenum>")


if __name__ == "__main__":
    main()
