from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, ChatMemberUpdated
from aiogram.enums import ChatType, ChatMemberStatus

from .. import login
from ..states_group import Waiting
from ..constants import SKIP_IN_MIDDLEWARES
from config.database import USERS_TABLE_NAME, GROUPS_TABLE_NAME
from database.utils import is_chat_in, add_chat, is_credentials_added


class DatabaseMissingInMiddleware(BaseMiddleware):
    def __init__(self, *args, **kwargs):
        pass

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        update: Message | ChatMemberUpdated,
        data: Dict[str, Any],
    ):

        command = data.get("command")
        context = data.get("state")
        if context:
            state = await context.get_state()

        if isinstance(update, Message):
            is_command_skipping = update.text in SKIP_IN_MIDDLEWARES or (
                command and command.command in SKIP_IN_MIDDLEWARES
            )
        else:
            is_command_skipping = False
        is_state_skipping = context and state in SKIP_IN_MIDDLEWARES
        if is_command_skipping or is_state_skipping:
            return await handler(update, data)

        is_private = update.chat.type == ChatType.PRIVATE
        kwargs = {}
        if is_private:
            table = USERS_TABLE_NAME
        else:
            table = GROUPS_TABLE_NAME
            kwargs.update(
                {
                    "invited_id": update.from_user.id,
                    "invited_name": update.from_user.full_name,
                }
            )

        if not is_chat_in(table, update.chat.id):
            add_chat(table, update.chat.id, **kwargs)

        if (
            not is_credentials_added(table, update.chat.id)
            and state != Waiting.login.state
            and state != Waiting.password.state
            and isinstance(update, ChatMemberUpdated)
            and update.new_chat_member.status != ChatMemberStatus.KICKED
            and update.new_chat_member.status != ChatMemberStatus.LEFT
        ):
            await (
                login.private(update, data) if is_private else login.group(update, data)
            )
            return

        return await handler(update, data)
