import re
from datetime import datetime
from netschoolapi.schemas import Day, Diary
from database.utils import update_login, update_password
from aiogram.types import User
from aiogram.enums.chat_type import ChatType
from .constants import (
    NS_DATA,
    TEMPLATES,
    CREDENTIALS_PATTERNS,
    HYPERLINK_FORMAT,
    LINK_USER_ID,
    LINK_USERNAME,
)
from .exceptions import CredentialsNotFound


def __get_days(diary: Diary):
    return [day for day in diary.schedule]


async def get_day_by_date(date: datetime, diary: Diary):
    days = __get_days(diary)

    for day in days:
        if day.day == date:
            return day


def get_weekday(date: datetime):
    return NS_DATA["weekdays"][date.weekday()]


def get_task_type(task_type: str):
    try:
        formatted = NS_DATA["tasks_types"][task_type]
        return formatted
    except KeyError:
        return task_type.lower()


def get_tasks_types_reductions():
    return "\n".join(
        [f"{full} = {red}" for full, red in NS_DATA["tasks_types"].items()]
    )


def get_credentials(chat_type: ChatType, text: str):
    pattern = CREDENTIALS_PATTERNS.get(chat_type)
    if pattern is None:
        raise ValueError("chat_type must be only private or group or supergroup")

    match = re.search(pattern, text, re.M)
    if match is None:
        raise CredentialsNotFound(f"Credentials weren't found in: {text}")
    return match.string.split()


def get_user_hyperlink(user: User):
    name = user.full_name
    if user.username:
        link = LINK_USERNAME.format(username=user.username)
    else:
        link = LINK_USER_ID.format(id=user.id)
    return HYPERLINK_FORMAT.format(link=link, text=name)


def add_credentials(table: str, chat_id: int, credentials: list[str]):
    update_login(table, chat_id, credentials[0])
    update_password(table, chat_id, credentials[1])


# async def add_chat(msg: Message):
#     arguments = msg.text[1:].split()
#     chat_id = arguments[0]
#     is_group = chat_id.startswith("-")

#     if is_group:
#         arguments_amount = 5
#         table = get_chats_table()
#         invited_id = get_invited_id(table, chat_id)
#         if msg.from_user.id != invited_id:
#             await msg.answer(text=bot_errors["no_permission"])
#             return
#     else:
#         arguments_amount = 3
#         table = get_directs_table()

#     if len(arguments) != arguments_amount:
#         await msg.answer(text=bot_errors["not_enough_arguments"])
#     else:
#         login = arguments[1]
#         password = arguments[2]
#         login2 = arguments[3] if is_group else None
#         password2 = arguments[4] if is_group else None

#         add_ns_credentials(table, chat_id, login, password, login2, password2)
#         await msg.answer(text=bot_text["credentials_added"])
