from typing import Any

from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.utils.deep_linking import create_start_link

from .constants import COMMANDS, HYPERLINK_FORMAT
from .states_group import Waiting
from .utils import get_user_hyperlink


async def private(msg: Message, data: dict[str, Any]):
    text = COMMANDS[f"start_private_logout"]
    await msg.answer(text=text)
    await data["state"].set_state(Waiting.login)


async def group(msg: Message, data: dict[str, Any]):
    hyperuser = get_user_hyperlink(msg.from_user)
    
    link = await create_start_link(msg.bot, f"login:{msg.chat.id}", True)
    hyperlink = HYPERLINK_FORMAT.format(link=link, text=link[:19] + '...')

    template = COMMANDS[f"start_group_logout"]
    text = template.format(hyperuser, hyperlink)
    await msg.answer(text=text)

    # key = StorageKey(msg.bot.id, msg.from_user.id, msg.from_user.id)
    # context = FSMContext(data["state"].storage, key)
    # await context.set_state(Waiting.login)
