from . import _config

TOKEN = _config.get('telegram', 'token')
PARSE_MODE = _config.get("telegram", "parse_mode")
DISABLE_LINK_PREVIEW = _config.getboolean("telegram", "disable_link_preview")
