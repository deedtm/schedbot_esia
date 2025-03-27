from . import _config
from datetime import timezone, timedelta

TZ_OFFSET = _config.getint("time", "timezone_offset")
TZ = timezone(timedelta(hours=TZ_OFFSET))
