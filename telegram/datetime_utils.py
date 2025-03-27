from datetime import datetime
from datetime import datetime, timedelta
from .constants import DATE_FORMATS, DATE_SEPARATORS


def get_need_date_and_week_start(day: datetime, next: bool | None):
    if next is None:
        need_date = day
    else:
        need_date = day + timedelta(days=1) if next else day - timedelta(days=1)

    if need_date.weekday() >= 6 and next:
        need_date = need_date + timedelta(days=7 - need_date.weekday())

    if not next and need_date.weekday() == 6:
        need_date = need_date - timedelta(days=1)

    week_start = need_date - timedelta(days=need_date.weekday())
    return need_date, week_start


def format_date(date: datetime, next: bool | None = None):
    if next is not None:
        delta = timedelta(days=1)
        date = date + delta if next else date - delta

    return date.strftime("%d.%m.%y")


def get_date_from_text(text: str):
    date = text[text.find("(") + 1 : text.find(")")]
    return datetime.strptime(date, "%d.%m.%y").date()


def get_today():
    return datetime.today().date()


def parse_date(date_string: str):
    if not date_string:
        return datetime.today()
    
    for sep in DATE_SEPARATORS:
        if sep in date_string:
            date_string = sep.join(date_string.split(sep)[:2])
            break


    for date_format in DATE_FORMATS:
        try:
            dt = datetime.strptime(date_string, date_format)
            if "%m" not in date_format:
                dt = dt.replace(month=datetime.today().month)
            year = datetime.today().year
            if dt.month > 8 and datetime.today().month <= 8:
                year -= 1
            return dt.replace(year=year)
        except ValueError as e:
            continue
