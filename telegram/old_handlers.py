from configparser import ConfigParser
from random import choice
from aiogram import F
from aiogram.types import (
    Message,
    CallbackQuery,
    BufferedInputFile,
    ChatMemberUpdated,
)
from aiogram.filters import Command, CommandObject
from aiogram.exceptions import TelegramForbiddenError
from aiogram.enums import ChatMemberStatus
from aiogram.fsm.context import FSMContext
from database.utils import is_chat_in, remove_chat
from .datetime_utils import format_date, get_date_from_text, get_today, parse_date
from .homework_utils import get_schedules_and_pics
from .marks_utils import get_marks
from .constants import TEMPLATES, ERRS, COMMANDS
from .objects import router, kb

__all__ = [
    "cancel_handler",
    "tomorrow_com",
    "forward",
    "send_pictures",
    "marks_handler",
]

config = ConfigParser()
config.read("config.ini")
bot_id = int(config.get("telegram", "token").split(":")[0])


@router.message(Command("cancel"))
async def cancel_handler(msg: Message, state: FSMContext, wmsg: Message):
    await state.set_state()
    await wmsg.edit_text(COMMANDS[msg.text[1:]])


# @router.messsage(Command('edit_credentials'))
# async def edit_creds_handler(msg)


# async def first_appearance(update: ChatMemberUpdated, table: str):
#     chat_id = update.chat.id
#     if not is_chat_in(table, chat_id):
#         add_chat(table, chat_id, invited_id=str(update.from_user.id), invited_name=update.from_user.full_name)
#         template = COMMANDS["start_group_logout"]
#         hyperlink = get_user_hyperlink(update.from_user)
#         text = template.format(hyperlink, )
#         await update.answer(text=text)


async def kick(update: ChatMemberUpdated, table: str):
    if is_chat_in(table, update.chat.id):
        remove_chat(table, update.chat.id)


@router.my_chat_member()
async def my_chat_member_handler(update: ChatMemberUpdated, table: str):
    member_status = update.new_chat_member.status
    if member_status == ChatMemberStatus.LEFT:
        await kick(update, table)
    # elif member_status == ChatMemberStatus.MEMBER:
    #     await first_appearance(update, table)


@router.message(Command("tomorrow"))
async def tomorrow_com(msg: Message, table: str, state: FSMContext, wmsg: Message):
    date = get_today()
    try:
        data = await get_schedules_and_pics(table, date, msg.chat.id, True)
        schedule = data[0]
        if msg.chat.id > 0:
            reply_markup = kb.private_homework_pic if data[1] else kb.private_homework
        else:
            reply_markup = (
                kb.group_homework_pic if data[1] or data[2] else kb.group_homework
            )

        await wmsg.edit_text(
            text=COMMANDS["schedule"].format(schedule=schedule),
            disable_web_page_preview=True,
            reply_markup=reply_markup,
        )
    except AttributeError as err:
        reply_markup = kb.group_homework if msg.chat.id < 0 else kb.private_homework
        if err.__str__() == "'NoneType' object has no attribute 'day'":
            await msg.answer(
                text=ERRS["no_info_for_next_day"].format(date=format_date(date, True)),
                reply_markup=reply_markup,
            )


@router.message(Command("day"))
async def day_com(
    msg: Message, command: CommandObject, table: str, state: FSMContext, wmsg: Message
):
    dt = parse_date(command.args)
    data = await get_schedules_and_pics(table, dt.date(), msg.chat.id)
    schedule = data[0]
    if msg.chat.id > 0:
        reply_markup = kb.private_homework_pic if data[1] else kb.private_homework
    else:
        reply_markup = kb.group_homework_pic if data[1] else kb.group_homework

    await wmsg.edit_text(
        text=COMMANDS["schedule"].format(schedule=schedule),
        disable_web_page_preview=True,
        reply_markup=reply_markup,
    )


@router.callback_query(
    (F.data == "forward_hw") | (F.data == "back_hw") | (F.data == "to_homework")
)
async def forward(q: CallbackQuery, table: str):
    next = True if q.data == "forward_hw" else False if q.data == "back_hw" else None
    date = get_date_from_text(q.message.text)
    try:
        data = await get_schedules_and_pics(table, date, q.message.chat.id, next)
        schedule = data[0]
        if q.message.chat.id > 0:
            reply_markup = kb.private_homework_pic if data[1] else kb.private_homework
        else:
            reply_markup = kb.group_homework_pic if data[1] else kb.group_homework

        await q.message.edit_text(
            text=COMMANDS["schedule"].format(schedule=schedule),
            reply_markup=reply_markup,
            disable_web_page_preview=True,
        )

    except AttributeError as err:
        reply_markup = (
            kb.group_homework if q.message.chat.id < 0 else kb.private_homework
        )
        if err.__str__() == "'NoneType' object has no attribute 'day'":
            await q.message.edit_text(
                text=ERRS["no_info_for_next_day"].format(date=format_date(date, next)),
                reply_markup=reply_markup,
            )


@router.callback_query(F.data == "send_pics")
async def send_pictures(q: CallbackQuery, table: str):
    date = get_date_from_text(q.message.text)
    data = await get_schedules_and_pics(table, date, q.message.chat.id, None)

    await q.answer(caption=TEMPLATES["sending_files"])

    documents1 = [BufferedInputFile(byte, name) for byte, name in data[1]]
    documents2 = None
    if q.message.chat.id < 0 and len(data) > 2:
        documents2 = [BufferedInputFile(byte, name) for byte, name in data[2]]

    try:
        msgs = []
        for d in documents1:
            msgs.append(await q.bot.send_document(chat_id=q.from_user.id, document=d))
        await msgs[0].edit_caption(caption=f"1\n{str(date)}")

        if q.message.chat.id < 0 and documents2:
            msgs = []
            for d in documents2:
                msgs.append(
                    await q.bot.send_document(chat_id=q.from_user.id, document=d)
                )
            await msgs[0].edit_caption(caption=f"2\n{str(date)}")

    except TelegramForbiddenError as err:
        error_str = err.__str__()
        if "Bot can't initiate conversation with a user" in error_str:
            await q.answer(ERRS["user_has_not_chat"])
        elif "Bot was blocked by the user" in error_str:
            await q.answer(ERRS["user_blocked_bot"])
        else:
            await q.answer(error_str)
    except BaseException as err:
        await q.answer(err.__str__())


@router.callback_query(
    (F.data == "to_marks") | (F.data == "back_marks") | (F.data == "forward_marks")
)
async def marks_handler(q: CallbackQuery, table: str):
    next = (
        True if q.data == "forward_marks" else False if q.data == "back_marks" else None
    )
    date = get_date_from_text(q.message.text)
    try:
        schedule = await get_marks(table, date, q.message.chat.id, next)
        await q.message.edit_text(
            text=COMMANDS["schedule"].format(schedule=schedule),
            reply_markup=kb.marks,
        )
    except AttributeError as err:
        reply_markup = (
            kb.group_homework if q.message.chat.id < 0 else kb.private_homework
        )
        if err.__str__() == "'NoneType' object has no attribute 'day'":
            await q.message.edit_text(
                text=ERRS["no_info_for_next_day"].format(date=format_date(date, next)),
                reply_markup=reply_markup,
            )
