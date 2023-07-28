import asyncio
import os

import utils
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor, exceptions
from bot_interface import BotInterface
from scrape import scrape
from database_interface import DatabaseInterface
from dotenv import load_dotenv
from tabulate import tabulate


class AsyncTelegramBot(BotInterface):
    def __init__(self, token: str, db_handler: DatabaseInterface, link: str, scrapeinterval: str, scrapenum=None):
        self.bot = Bot(token)
        self.chat_id = os.getenv("CHAT_ID")
        load_dotenv()
        self.watchlist_id = os.getenv("WATCHLIST_ID")
        self.link = link
        self.db_handler = db_handler
        if scrapenum is not None:
            self.scrapenum = int(scrapenum)
        else:
            self.scrapenum = scrapenum
        self.scrapeinterval = int(scrapeinterval)

        # Initialize dispatcher
        self.dp = Dispatcher(self.bot)

        @self.dp.message_handler(commands=['setup'])
        async def setuo(message: types.Message):
            print(message.chat.id)
            await message.reply(f"Hello. Your chat id is {message.chat.id}")

        @self.dp.message_handler(commands=['start'])
        async def start_scraping(message: types.Message):
            try:
                if utils.continue_scraping is False:
                    await message.reply("Starting Up rrrrrrr")
                    asyncio.create_task(scrape(link, self, self.db_handler, self.scrapeinterval, self.scrapenum))
                    utils.continue_scraping = True
            except Exception as e:
                print(f"Exception: {e}")

        @self.dp.message_handler(commands=['stop'])
        async def stop_scraping(message: types.Message):
            try:
                if utils.continue_scraping is True:
                    await message.reply("Shutting Down...")
                    utils.continue_scraping = False
            except Exception as e:
                print(f"Exception {e}")

        @self.dp.message_handler(commands=['scrapenum'])
        async def set_scrapenum(message: types.Message):
            try:
                self.scrapenum = int(message.text.split()[1:][0])
                await message.reply("scrapenum set, please restart")
            except Exception as e:
                print(f"Exception {e}")

        @self.dp.message_handler(commands=['scrapeinterval'])
        async def set_scrapeinterval(message: types.Message):
            try:
                self.scrapeinterval = int(message.text.split()[1:][0])
                await message.reply("scrapeinterval set, please restart")
            except Exception as e:
                print(f"Exception {e}")

        @self.dp.message_handler(commands=['catalog'])
        async def add_to_catalog(message: types.Message):
            try:
                model = message.text.split()[1:][0]
                self.db_handler.insert_model(model)
                await message.reply(f"{model} added to catalog")
            except Exception as e:
                print(f"Exception {e}")

        @self.dp.message_handler(commands=['get'])
        async def get_table(message: types.Message):
            try:
                table_type = message.text.split()[1:][0]
                await self.send_table(table_type)
            except Exception as e:
                print(f"Exception {e}")
                await message.reply("Empty")

        @self.dp.message_handler(commands=['clear'])
        async def clear_catalog(message: types.Message):
            try:
                self.db_handler.clear_catalog()
                await message.reply(f"catalog cleared")
            except Exception as e:
                print(f"Exception {e}")

        @self.dp.message_handler(commands=['watch', 'unwatch'])
        async def manual_watch(message: types.Message):
            data = message.text.split()

            if data[0] == "/watch":
                if self.db_handler.search_watchlist(int(data[1])) is None:
                    self.db_handler.insert_watchlist(int(data[1]), data[2], int(data[3]))
                    await message.reply(f"Item {data[1]} watched")
                else:
                    await message.reply("Item already watched")
            else:
                if self.db_handler.search_watchlist(int(data[1])) is not None:
                    self.db_handler.remove_from_watchlist(int(data[1]))
                    await message.reply(f"Item {data[1]} unwatched")
                else:
                    await message.reply("Item not in watchlist")

        @self.dp.callback_query_handler(
            lambda call: (call.data.startswith("Watch")) or (call.data.startswith("Unwatch")))
        async def watch_button_handler(callback_query: types.CallbackQuery):
            print("handling")

            callback_data = callback_query.data.split(':')
            action = callback_data[0]
            item_id = int(callback_data[1])
            item_model = callback_data[2]
            item_price = int(callback_data[3])

            # Add/remove from watchlist accordingly
            try:
                if action == "Watch":
                    self.db_handler.insert_watchlist(item_id, item_model, item_price)
                    await self.bot.send_message(self.chat_id, f"Item {item_id} watched")
                    new_status = "Unwatch"
                else:
                    self.db_handler.remove_from_watchlist(item_id)
                    await self.bot.send_message(self.chat_id, f"Item {item_id} unwatched")
                    new_status = "Watch"

                # Update watch button text
                await self.bot.edit_message_reply_markup(callback_query.message.chat.id,
                                                         callback_query.message.message_id,
                                                         reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[[
                                                             types.InlineKeyboardButton(
                                                                 new_status,
                                                                 callback_data=f"{new_status}:{item_id}:{item_model}:{item_price}")]]), )
            except Exception as e:
                print(f"Exception: {e}")

    def start_bot(self):
        executor.start_polling(self.dp, skip_updates=True)

    def stop_bot(self):
        self.dp.stop_polling()

    async def send_message(self, message: str):
        if self.chat_id is not None:
            await self.bot.send_message(self.chat_id, message)

    async def send_listing_notification(self, model: str, price: int, link: str, watched: bool, image=None):
        try:
            item_id = utils.extract_id_from_link(link)
            price_str = str(price)

            # Create inline keyboard watchlist button
            if self.db_handler.search_watchlist(item_id) is not None:
                button_status = "Unwatch"
                c_data = f"Unwatch:{item_id}:{model}:{price}"
            else:
                button_status = "Watch"
                c_data = f"Watch:{item_id}:{model}:{price}"
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            watch_button = types.InlineKeyboardButton(button_status, callback_data=c_data)
            keyboard.insert(watch_button)

            # Create clickable link
            link_markup = f'<a href="{link}">Product Page</a>'

            # HTML formatting for message, set channel for sending notification
            if watched:
                message = f"Watched item price change\nModel: {model}\nPrice: {price_str}\n\n{link_markup}"
                channel = self.watchlist_id
            else:
                message = f"New listing\nModel: {model}\nPrice: {price_str}\n\n{link_markup}"
                channel = self.chat_id

            # Send listing with photo
            if image is not None:
                await self.bot.send_photo(channel, image, caption=message, parse_mode='HTML',
                                          reply_markup=keyboard)
            else:
                await self.bot.send_message(channel, message, parse_mode='HTML', reply_markup=keyboard)

        except exceptions.MessageError as e:
            print(f"Exception has occurred: {e}")

    async def send_table(self, table_type: str):
        table = tabulate(self.db_handler.get_all_from_table(table_type), headers='keys', tablefmt='grid')
        if len(table) <= 4096:
            await self.bot.send_message(self.chat_id, table)
        else:
            message_chunks = utils.split_text(table, 4096)

            # Send each chunk as a separate message
            for chunk in message_chunks:
                await self.bot.send_message(self.chat_id, chunk)
