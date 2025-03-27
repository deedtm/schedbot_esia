from . import _config
import os

DB = _config.get("database", "path")
DB_PATH = os.sep.join(DB.split(".")) + ".db"
USERS_TABLE_NAME = _config.get("database", "users_table_name")
USERS_TABLE_COLUMNS = [
    '"id"	INTEGER',
    '"chat_id"	INTEGER',
    '"login"	TEXT',
    '"password"	TEXT',
    'PRIMARY KEY("id" AUTOINCREMENT)',
]
GROUPS_TABLE_NAME = _config.get("database", "groups_table_name")
GROUPS_TABLE_COLUMNS = [
    '"id"	INTEGER',
    '"chat_id"	INTEGER',
    '"invited_id"	INTEGER',
    '"invited_name" TEXT',
    '"login" TEXT',
    '"password" TEXT',
    'PRIMARY KEY("id" AUTOINCREMENT)',
]
