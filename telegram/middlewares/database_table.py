from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Update, Message
from aiogram.enums import ChatType
from config.database import USERS_TABLE_NAME, GROUPS_TABLE_NAME

from ..constants import ERRS


class DatabaseTableMiddleware(BaseMiddleware):
    def __init__(self):
        pass

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        update: Update,
        data: Dict[str, Any],
    ):
        if "table" in data["handler"].params:
            chat_type = update.chat.type if isinstance(update, Message) else update.message.chat.type
            is_users = chat_type == ChatType.PRIVATE

            context = data.get("state")
            if context:
                state_data = await context.get_data()
                is_users = is_users and state_data.get("chat_id") is None
            data["table"] = USERS_TABLE_NAME if is_users else GROUPS_TABLE_NAME

        return await handler(update, data)
