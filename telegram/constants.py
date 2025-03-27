import json
from .states_group import Waiting
from aiogram.enums.chat_type import ChatType

CLOCK_EMOJI = "🕛🕐🕑🕒🕓🕔🕕🕖🕗🕘🕙🕚🕜🕝🕞🕟🕠🕡🕢🕣🕤🕥🕦🕧"
DATE_FORMATS = [
    "%d",
    "%d.%m",
    "%d %m",
    "%d-%m",
]
DATE_SEPARATORS = [
    s.lower().strip("%d").strip("%m").strip("%y") for s in DATE_FORMATS if len(s) > 2
]

with open("telegram/templates.json", encoding="utf8") as f:
    TEMPLATES: dict[str, str | dict[str, str]] = json.load(f)
COMMANDS: dict[str, str] = TEMPLATES.get("commands")
ERRS: dict[str, str] = TEMPLATES.get("errors")

with open("ns_data.json", "r", encoding="utf8") as f:
    NS_DATA: dict = json.load(f)

CREDENTIALS_PATTERNS = {
    ChatType.PRIVATE: r"^\S+ \S+$",
    ChatType.GROUP: r"^\S+ \S+ \S+ \S+$",
    ChatType.SUPERGROUP: r"^\S+ \S+ \S+ \S+$",
}

LINK_USERNAME = "https://t.me/{username}"
LINK_USER_ID = "tg://user?id={id}"
HYPERLINK_FORMAT = '<a href="{link}">{text}</a>'

SKIP_COMMANDS = "/removeme", "/cancel", "/yes", "/no"
SKIP_STATES = Waiting.removeme_confirmation.state,
SKIP_IN_MIDDLEWARES = (*SKIP_COMMANDS, *SKIP_STATES)