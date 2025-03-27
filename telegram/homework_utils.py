from netschoolapi.schemas import Day, Assignment, Lesson
from datetime import datetime
from .datetime_utils import format_date, get_need_date_and_week_start
from .utils import get_day_by_date, get_weekday
from .constants import NS_DATA
from database.exceptions import MissingCredentials
from database.utils import get_credentials
from .objects import ns


async def get_schedules_and_pics(table, date: datetime, chat_id: int, is_next: bool = None):
    login, password = get_credentials(table, chat_id)
    if login is None or password is None:
        raise MissingCredentials(f"{login=}, {password=}")
    schedule, bytes_pics = await __get_homework_and_pics(chat_id, date, is_next, login, password)
    output = [schedule, bytes_pics]

    # if chat_id < 0:
    #     schedule, bytes_pics = await __get_homework_and_pics(
    #         date, is_next, login, password
    #     )

    #     output.insert(0, __format_schedules(output[0], schedule))
    #     output.pop(1)
    #     output.insert(2, bytes_pics)

    return output


async def __get_homework_and_pics(
    chat_id: int, date: datetime, is_next: bool, login: str, password: str
):
    await ns.login(chat_id, login, password)

    need_date, start_date = get_need_date_and_week_start(date, is_next)
    diary = await ns.get_diary(start_date)

    day = await get_day_by_date(need_date, diary)
    homework, bytes_pics = await __get_homework_and_pics_data(day)

    await ns.logout(chat_id)
    
    return homework, bytes_pics


async def __get_homework_and_pics_data(day: Day):
    day_date = day.day
    homework = []
    pics_datas = []

    for lesson in day.lessons:
        assignment = __get_homework_assignment(lesson)
        content = ""

        if assignment:
            content = assignment.content
            data = await __get_pics(assignment)
            pics_datas.extend(data)

        homework.append(__format_lesson(content, lesson.subject))

    weekday = get_weekday(day_date)
    day_date = format_date(day_date)
    homework = "\n".join(homework)
    text = f"<b>{weekday} ({day_date}):</b>\n\n" + homework

    return text, pics_datas


async def __get_pics(assignment: Assignment):
    attachments = await ns.get_attachments(assignment)
    return [(bytes, name) async for bytes, name in ns.pics_generator(attachments)]


def __format_schedules(schedule1: str, schedule2: str):
    lessons1 = schedule1.split("\n")
    dif = list(set(schedule2.split("\n")).difference(set(lessons1)))
    if dif:
        dif.insert(0, "\n👥  <b>Другая группа:</b>")
    lessons1.extend(dif)
    return "\n".join(lessons1)


def __format_lesson(lesson_hw: str, subject: str):
    hw = ": " + lesson_hw if lesson_hw else ""
    hw = __replace_links(hw)
    hw = f"{hw}" if hw else hw
    subject_formatted = NS_DATA["lessons"].get(subject)
    subject = subject_formatted if subject_formatted else subject
    subject = f"• {subject}" if hw else subject

    return f"{subject}{hw}"


def __replace_links(text: str):
    words = text.split()
    is_link = False
    links = []

    for word in words:
        if word.startswith(("http://", "https://", "www.")):
            is_link = True
            links.append(word)

    if is_link:
        prev_end_ind = 0
        for link in links:
            start_ind = text.find(link, prev_end_ind)
            end_ind = start_ind + len(link)
            text = text[:start_ind] + f'<a href="{link}">ссылка</a>' + text[end_ind:]
            prev_end_ind = end_ind

    return text


def __get_homework_assignment(lesson: Lesson):
    for assignment in lesson.assignments:
        if assignment.type == "Домашнее задание":
            return assignment
