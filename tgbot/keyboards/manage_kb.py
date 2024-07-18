from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from tgbot.create_bot import admins


def main_kb(user_telegram_id: int) -> ReplyKeyboardMarkup:
    pass
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Воспользуйтесь меню:"
    )
    return keyboard


def home_page_kb() -> ReplyKeyboardMarkup:
    pass
    return ReplyKeyboardMarkup(
        keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Воспользуйтесь меню:"
    )


def accept_or_reject(user_telegram_id: int) -> ReplyKeyboardMarkup:
    pass
    return ReplyKeyboardMarkup(
        keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Воспользуйтесь меню:"
    )


def manage_flow_kb():
    pass
    return ReplyKeyboardMarkup(
        keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Выберите действие:"
    )