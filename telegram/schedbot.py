import logging

from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from .old_handlers import *
from config.database import USERS_TABLE_NAME, GROUPS_TABLE_NAME, USERS_TABLE_COLUMNS, GROUPS_TABLE_COLUMNS
from database.utils import create_tables
from .objects import router
from .handlers import *


class Schedbot:
    def __init__(self, token: str):
        self.bot = Bot(token=token, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        self.dp = Dispatcher(storage=MemoryStorage())
        self.dp.include_router(router)
        self.__create_db_tables()

    def __create_db_tables(self):
        tables = [USERS_TABLE_NAME, GROUPS_TABLE_NAME]
        create_tables(tables, [USERS_TABLE_COLUMNS, GROUPS_TABLE_COLUMNS])
        logging.debug(f'Were created tables: {", ".join(tables)}')

    async def start(self):
        bot, dp = self.bot, self.dp
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
