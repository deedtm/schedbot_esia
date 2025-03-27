from aiogram.filters import Command, CommandObject, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.enums import ChatType

from ..objects import router
from ..states_group import Waiting
from ..constants import COMMANDS

from database.utils import remove_chat, get_invited_id


@router.message(Command("removeme"))
async def removeme_handler(msg: Message, state: FSMContext, wmsg: Message, table: str):
    if msg.chat.type != ChatType.PRIVATE:
        invited_id = get_invited_id(table, msg.chat.id)
        if invited_id != msg.from_user.id:
            return
    await state.set_state(Waiting.removeme_confirmation)
    await wmsg.edit_text(text=COMMANDS["removeme_confirmation"])

@router.message(Command("yes"), StateFilter(Waiting.removeme_confirmation))
async def removeme_confirmation_handler(msg: Message, command: CommandObject, state: FSMContext, table: str, wmsg: Message):
    if msg.chat.type != ChatType.PRIVATE:
        invited_id = get_invited_id(table, msg.chat.id)
        if invited_id != msg.from_user.id:
            return
    
    await state.set_state()
    if msg.text == "ДА" or command.command == "yes":
        remove_chat(table, msg.chat.id)
        await wmsg.edit_text(text=COMMANDS["removeme_success"])
    else:
        await wmsg.edit_text(text=COMMANDS["removeme_cancel"])
