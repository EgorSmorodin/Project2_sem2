from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .builders import create_time_slider_builder

def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Изменить город", callback_data="change_city")],
        [InlineKeyboardButton(text="⏳ Выбрать эпоху", callback_data="choose_era")],
        [InlineKeyboardButton(text="📜 Получить событие сейчас", callback_data="get_event")],
        [InlineKeyboardButton(text="📅 Получать события ежедневно", callback_data="subscribe")],
        [InlineKeyboardButton(text="ℹ️ Помощь", callback_data="help")]
    ])

def eras() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏰 Древняя Русь (IX-XVI вв.)", callback_data="era_ancient_rus")],
        [InlineKeyboardButton(text="👑 Царская Россия (XVI-XVIII вв.)", callback_data="era_tsar_rus")],
        [InlineKeyboardButton(text="⚜️ Императорская Россия (XVIII-XX вв.)", callback_data="era_imperial")],
        [InlineKeyboardButton(text="☭ Советский период (1917-1991)", callback_data="era_soviet")],
        [InlineKeyboardButton(text="🏛 Наше время (с 1991)", callback_data="era_modern")],
        [InlineKeyboardButton(text="↩️ Назад", callback_data="back")]
    ])

def time_slider(current_hour: int = 10) -> InlineKeyboardMarkup:
    builder = create_time_slider_builder(current_hour)
    return builder.as_markup()

def cancel() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
    ])

def after_event() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔁 Еще событие", callback_data="get_event")],
        [InlineKeyboardButton(text="↩️ В главное меню", callback_data="back")]
    ])

def subscribe_back() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="↩️ Назад", callback_data="back")]
    ])