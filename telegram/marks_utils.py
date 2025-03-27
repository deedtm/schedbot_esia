from .utils import get_day_by_date, get_weekday, get_task_type, Day
from .constants import NS_DATA
from .datetime_utils import format_date, get_need_date_and_week_start
from datetime import datetime
from database.exceptions import MissingCredentials
from database.utils import get_credentials
from .objects import ns


async def get_marks(table, date: datetime, chat_id: int, is_next: bool):
    login, password = get_credentials(table, chat_id)
    if login is None or password is None:
        raise MissingCredentials(f"{login=}, {password=}")
    schedule = await __get_marks_schedule(chat_id, date, is_next, login, password)

    return schedule


async def __get_marks_schedule(
    chat_id: int, date: datetime, is_next: bool, login: str, password: str
):
    await ns.login(chat_id, login, password)

    need_date, start_date = get_need_date_and_week_start(date, is_next)
    diary = await ns.get_diary(start_date)

    day = await get_day_by_date(need_date, diary)
    marks = await __get_schedule(day)

    await ns.logout(chat_id)
    return marks


async def __get_schedule(day: Day):
    schedule = []

    for lesson in day.lessons:
        assignments = lesson.assignments
        tasks_types = [ass.type for ass in assignments]
        marks = [ass.mark for ass in assignments]
        schedule.append(__format_lesson(lesson.subject, tasks_types, marks))

    weekday = get_weekday(day.day)
    day_date = format_date(day.day)
    schedule = "\n".join(schedule)
    text = f"<b>{weekday} ({day_date}):</b>\n\n" + schedule

    return text


def __format_lesson(
    subject: str, tasks_types: list[str] | None = None, marks: list[int] | None = None
):
    lesson = []

    formatted_subject = NS_DATA["lessons"].get(subject)
    lesson.append(formatted_subject if formatted_subject else subject)

    if tasks_types:
        types = "".join(
            [
                "(",
                *[
                    f"{get_task_type(type)},"
                    for type in tasks_types
                    if type is not None
                ],
                ")",
            ]
        )
        types = "<i>" + types[:-2] + types[-1] + "</i>"
        lesson.append(types)
    if marks:
        marks = list(filter(None.__ne__, marks))
    if marks:
        lesson.insert(0, "<b>•</b>")
        lesson.append("—")
        formatted_marks = "".join([f"{mark}/" for mark in marks if mark is not None])
        formatted_marks = "<b>" + formatted_marks[:-1] + "</b>"
        lesson.append(formatted_marks)

    return " ".join(lesson)
