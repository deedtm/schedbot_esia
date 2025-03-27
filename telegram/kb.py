from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class Keyboards:
    def __init__(self):
        self.__create()
        self.group_homework = InlineKeyboardMarkup(
            inline_keyboard=self.__group_homework_kb
        )
        self.group_homework_pic = InlineKeyboardMarkup(
            inline_keyboard=self.__group_homework_pic_kb
        )
        self.private_homework = InlineKeyboardMarkup(
            inline_keyboard=self.__private_homework_kb
        )
        self.private_homework_pic = InlineKeyboardMarkup(
            inline_keyboard=self.__private_homework_pic_kb
        )
        self.marks = InlineKeyboardMarkup(inline_keyboard=self.__marks_kb)

    def __create(self):
        hw_arrows = [
            InlineKeyboardButton(text="◀️", callback_data="back_hw"),
            InlineKeyboardButton(text="▶️", callback_data="forward_hw"),
        ]
        marks_arrows = [
            InlineKeyboardButton(text="◀️", callback_data="back_marks"),
            InlineKeyboardButton(text="▶️", callback_data="forward_marks"),
        ]
        marks = [InlineKeyboardButton(text="Оценки", callback_data="to_marks")]

        self.__group_homework_kb = [hw_arrows]
        self.__private_homework_kb = [hw_arrows, marks]

        self.__group_homework_pic_kb = [
            hw_arrows,
            [
                InlineKeyboardButton(
                    text="Получить прикрепленные файлы в лс", callback_data="send_pics"
                )
            ],
        ]
        self.__private_homework_pic_kb = [
            hw_arrows,
            marks,
            [
                InlineKeyboardButton(
                    text="Получить фотографии в лс", callback_data="send_pics"
                )
            ],
        ]

        self.__marks_kb = [
            marks_arrows,
            [
                InlineKeyboardButton(
                    text="Домашнее задание", callback_data="to_homework"
                )
            ],
        ]
