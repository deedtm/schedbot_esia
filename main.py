import asyncio
import logging
import netschoolapi.selenium_netschool

from config.telegram import TOKEN
from telegram.schedbot import Schedbot

from log.utils import disable_loggers
import argparse

async def main():
    schedbot = Schedbot(TOKEN)
    await schedbot.start()


if __name__ == "__main__":  
    parser = argparse.ArgumentParser(description='Schedbot ESIA')
    parser.add_argument('--log-level', 
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], 
                        default='INFO',
                        help='Set the logging level')
    args = parser.parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level))
    disable_loggers(('websockets.client', 'httpx._client', 'uc.connection', 'nodriver.core'))
    asyncio.run(main())
