from typing import Optional

from . import tables
from .__utils import (
    is_data_in,
    add_data,
    get_all_data,
    get_data,
    update_data,
    remove_from_table,
)
from .log import logger
from .objects import coder

# [(str1, data), (str2, data)]


def create_table(table_name: str, table_columns: list):
    tables.create(table_name, table_columns, "IF NOT EXISTS")
    logger.debug(f"Table {table_name} was created")


def create_tables(tables_names: list, tables_columns: list[list]):
    for table_name, table_columns in zip(tables_names, tables_columns):
        create_table(table_name, table_columns)


def is_chat_in(table: str, chat_id: int):
    return is_data_in(table, {"chat_id": chat_id})


def is_credentials_added(table: str, chat_id: int):
    credentials = get_credentials(table, chat_id)
    return credentials != (None, None)


def add_chat(
    table: str,
    chat_id: int,
    login: Optional[str] = None,
    password: Optional[str] = None,
    invited_id: Optional[int] = None,
    invited_name: Optional[str] = None,
):
    chat_data = {"chat_id": chat_id}
    if login:
        login = coder.encrypt(login)
        chat_data.setdefault("login", login)
    if password:
        password = coder.encrypt(password)
        chat_data.setdefault("password", password)
    if invited_id:
        chat_data.setdefault("invited_id", invited_id)
    if invited_name:
        chat_data.setdefault("invited_name", invited_name)
    add_data(table, chat_data)
    logger.debug(f"{chat_id} was added to database")


def get_chats_data(table: str, data: list):
    return get_data(table, data)


def get_all_chats(table: str):
    return get_chats_data(table, ["*"])


def get_chat(table: str, chat_id: int):
    return get_all_data(table, {"chat_id": chat_id})[1:]


def get_login(table: str, chat_id: int):
    encrypted_login = get_data(table, ["login"], {"chat_id": chat_id})[0]
    return coder.decrypt(encrypted_login)


def get_password(table: str, chat_id: int):
    encrypted_password = get_data(table, ["password"], {"chat_id": chat_id})[0]
    return coder.decrypt(encrypted_password)


def get_invited_id(table: str, chat_id: int):
    return get_data(table, ["invited_id"], {"chat_id": chat_id})[0]


def get_invited_name(table: str, chat_id: int):
    return get_data(table, ["invited_name"], {"chat_id": chat_id})[0]


def get_invited_data(table: str, chat_id: int):
    return get_data(table, ["invited_id", "invited_name"], {"chat_id": chat_id})


def get_credentials(table: str, chat_id: int):
    encrypted_login, encrypted_password = get_data(
        table, ["login", "password"], {"chat_id": chat_id}
    )
    login = coder.decrypt(encrypted_login, None)
    password = coder.decrypt(encrypted_password, None)
    return login, password


def update_login(table: str, chat_id: int, login: str):
    login = coder.encrypt(login)
    update_data(table, {"login": login}, {"chat_id": chat_id})
    logger.debug(f"{chat_id}'s login updated")


def update_password(table: str, chat_id: int, password: str):
    password = coder.encrypt(password)
    update_data(table, {"password": password}, {"chat_id": chat_id})
    logger.debug(f"{chat_id}'s password updated")


def update_invited_id(table: str, chat_id: int, invited_id: int):
    update_data(table, {"invited_id": invited_id}, {"chat_id": chat_id})
    logger.debug(f"{chat_id}'s invited id updated to {invited_id}")


def update_invited_name(table: str, chat_id: int, invited_name: str):
    update_data(table, {"invited_name": invited_name}, {"chat_id": chat_id})
    logger.debug(f"{chat_id}'s invited name updated to {invited_name}")


def remove_chat(table: str, chat_id: int):
    remove_from_table(table, {"chat_id": chat_id})
    logger.debug(f"{chat_id} was removed")
