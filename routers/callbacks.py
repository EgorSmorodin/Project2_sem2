from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from states.user_states import UserStates
from keyboards.inline import main_menu, eras, time_slider, after_event, cancel, subscribe_back
from services.wikidata_client import get_historical_event
from storage.user_data import user_data, subscribers
from utils.formatters import format_era_name
import logging

router = Router()
logger = logging.getLogger(__name__)


# Универсальный обработчик "Назад" для всех состояний
@router.callback_query(F.data.in_(["back", "cancel"]))
async def process_back(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Главное меню:",
        reply_markup=main_menu()
    )
    await state.set_state(UserStates.MAIN_MENU)


# Обработчик для кнопки "Помощь"
@router.callback_query(F.data == "help", UserStates.MAIN_MENU)
async def show_help(callback: CallbackQuery):
    help_text = (
        "ℹ️ Помощь по боту:\n\n"
        "Используйте кнопки меню для:\n"
        "📍 Изменения города\n"
        "⏳ Выбора исторического периода\n"
        "📜 Получения события\n"
        "📅 Подписки на ежедневные события\n\n"
        "Команды:\n"
        "/start - Начать работу с ботом\n"
        "/help - Показать справку\n"
        "/subscribe - Подписаться на ежедневные события\n"
        "/unsubscribe - Отписаться от ежедневных событий"
    )
    await callback.message.edit_text(
        help_text,
        reply_markup=main_menu()
    )


# Обработчик для кнопки "Изменить город"
@router.callback_query(F.data == "change_city", UserStates.MAIN_MENU)
async def change_city(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Введите название города:",
        reply_markup=cancel()
    )
    await state.set_state(UserStates.SELECT_CITY)


# Обработчик для кнопки "Выбрать эпоху"
@router.callback_query(F.data == "choose_era", UserStates.MAIN_MENU)
async def choose_era(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Выберите интересующую эпоху:",
        reply_markup=eras()
    )
    await state.set_state(UserStates.SELECT_ERA)


# Обработчик выбора конкретной эпохи
@router.callback_query(F.data.startswith("era_"), UserStates.SELECT_ERA)
async def select_era(callback: CallbackQuery, state: FSMContext):
    era = callback.data.split('_')[1]
    user_id = callback.from_user.id

    if user_id not in user_data:
        user_data[user_id] = {}

    user_data[user_id]['era'] = era
    user_data[user_id]['shown_events'] = set()

    await callback.message.edit_text(
        f"✅ Выбрана эпоха: {format_era_name(era)}",
        reply_markup=main_menu()
    )
    await state.set_state(UserStates.MAIN_MENU)


# Обработчик для кнопки "Получить событие"
@router.callback_query(F.data == "get_event", UserStates.MAIN_MENU)
async def get_event(callback: CallbackQuery):
    user_id = callback.from_user.id

    # Проверка, что пользователь настроил бота
    if user_id not in user_data or 'city' not in user_data[user_id]:
        await callback.answer("Сначала настройте город и эпоху!", show_alert=True)
        return

    event = await get_historical_event(user_id)
    await callback.message.edit_text(
        f"📜 Историческое событие:\n\n{event}",
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=after_event()
    )


# Обработчик для кнопки "Подписаться"
@router.callback_query(F.data == "subscribe", UserStates.MAIN_MENU)
async def subscribe(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id

    # Проверка, что пользователь настроил бота
    if user_id not in user_data or 'city' not in user_data[user_id]:
        await callback.answer("Сначала настройте город и эпоху!", show_alert=True)
        return

    if user_id in subscribers:
        current_time = subscribers[user_id].get('time', '10:00')
        await callback.message.edit_text(
            "Вы уже подписаны на ежедневные события!\n"
            f"Время получения: {current_time}\n"
            "Используйте /unsubscribe для отмены подписки.",
            reply_markup=subscribe_back()
        )
    else:
        await state.update_data(hour=10)
        await callback.message.edit_text(
            "Выберите время, в которое хотите получать ежедневные события:",
            reply_markup=time_slider(10)
        )
        await state.set_state(UserStates.SELECT_TIME)


# Обработчик слайдера времени
@router.callback_query(F.data.in_(["time_prev", "time_next", "time_confirm"]), UserStates.SELECT_TIME)
async def process_time_slider(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    data = await state.get_data()
    current_hour = data.get('hour', 10)

    if callback.data == "time_prev":
        current_hour = (current_hour - 1) % 24
    elif callback.data == "time_next":
        current_hour = (current_hour + 1) % 24
    elif callback.data == "time_confirm":
        subscribers[user_id] = {
            'city': user_data[user_id]['city'],
            'era': user_data[user_id]['era'],
            'time': f"{current_hour:02d}:00"
        }
        await callback.message.edit_text(
            f"✅ Вы подписались на ежедневные исторические события!\n"
            f"Время получения: {current_hour:02d}:00",
            reply_markup=main_menu()
        )
        await state.set_state(UserStates.MAIN_MENU)
        return

    await state.update_data(hour=current_hour)
    await callback.message.edit_text(
        "Выберите время, в которое хотите получать ежедневные события:",
        reply_markup=time_slider(current_hour)
    )