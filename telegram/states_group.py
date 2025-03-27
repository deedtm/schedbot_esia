from aiogram.fsm.state import StatesGroup, State


class Waiting(StatesGroup):
    login = State("login")
    password = State("password")
    removeme_confirmation = State("removeme_confirmation")
    