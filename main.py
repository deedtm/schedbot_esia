import asyncio
import logging
import netschoolapi.selenium_netschool

from config.telegram import TOKEN
from telegram.schedbot import Schedbot

from log.utils import disable_loggers

async def main():
    schedbot = Schedbot(TOKEN)
    await schedbot.start()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    disable_loggers(('websockets', 'uc.connection'))
    asyncio.run(main())
