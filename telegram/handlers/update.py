from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.enums import ChatType
from aiogram.utils.deep_linking import create_start_link

from ..objects import router
from ..states_group import Waiting
from ..constants import COMMANDS, ERRS, TEMPLATES

from database.utils import update_login, update_password, get_invited_id


@router.message(Command("update"))
async def update_handler(msg: Message, state: FSMContext, wmsg: Message, table: str):
    if msg.chat.type != ChatType.PRIVATE:
        invited_id = get_invited_id(table, msg.chat.id)
        if invited_id != msg.from_user.id:
            return
        link = await create_start_link(msg.bot, f"login:{msg.chat.id}", encode=True)
        text = COMMANDS["update_group"].format(link)
    else:
        text = COMMANDS["update"]
        
    await wmsg.edit_text(text=text)
    await state.set_state(Waiting.login)


@router.message(Waiting.login)
async def login_handler(msg: Message, state: FSMContext, table: str, wmsg: Message):
    data = await state.get_data()
    chat_id = data.get("chat_id")
    if chat_id is None:
        chat_id = msg.from_user.id
    else:
        invited_id = get_invited_id(table, chat_id)
        if invited_id != msg.from_user.id:
            text = ERRS["no_permission"]
            await wmsg.edit_text(text)
            return

    update_login(table, chat_id, msg.text)
    text = TEMPLATES["login_saved"].format(msg.text)

    await state.set_state(Waiting.password)
    await wmsg.edit_text(text)


@router.message(Waiting.password)
async def password_handler(msg: Message, state: FSMContext, table: str, wmsg: Message):
    data = await state.get_data()
    chat_id = data.get("chat_id")
    if chat_id is None:
        chat_id = msg.from_user.id

    update_password(table, chat_id, msg.text)
    text = TEMPLATES["password_saved"]

    await state.clear()
    await wmsg.edit_text(text)
