from aiogram.utils.keyboard import InlineKeyboardBuilder

def create_time_slider_builder(current_hour: int) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.button(text="◀️", callback_data="time_prev")
    builder.button(text=f"{current_hour:02d}:00", callback_data="time_confirm")
    builder.button(text="▶️", callback_data="time_next")
    builder.button(text="↩️ Назад", callback_data="back")
    builder.adjust(3, 1)
    return builder