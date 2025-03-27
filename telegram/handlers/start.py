from aiogram.filters import CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.deep_linking import decode_payload

from ..objects import router
from ..states_group import Waiting
from ..utils import get_tasks_types_reductions
from ..constants import COMMANDS


@router.message(CommandStart(deep_link=True))
async def deep_link_handler(msg: Message, state: FSMContext, command: CommandObject, wmsg: Message):
    args = command.args
    data = decode_payload(args).split(":")
    await state.update_data(chat_id=int(data[1]))
    await state.set_state(Waiting.login)
    await wmsg.edit_text(text=COMMANDS["update"])


@router.message(CommandStart())
async def start_handler(msg: Message, wmsg: Message):
    reductions = get_tasks_types_reductions()
    await wmsg.edit_text(text=COMMANDS["start_login"].format(reductions=reductions))
