from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from services.wikidata_client import get_city_wikidata_id
from keyboards.inline import main_menu
from states.user_states import UserStates
from storage.user_data import user_data
from utils.formatters import format_era_name
import logging

router = Router()
logger = logging.getLogger(__name__)


@router.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    city_name = "Санкт-Петербург"
    city_id = await get_city_wikidata_id(city_name)

    user_data[user_id] = {
        'city': city_name,
        'city_id': city_id,
        'era': 'imperial',
        'shown_events': set()
    }

    await message.answer(
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        "Я - бот «Дневной Петербург». Я буду присылать тебе интересные "
        "исторические события.\n\n"
        "Сейчас настроено:\n"
        f"📍 Город: {city_name}\n"
        f"⏳ Эпоха: {format_era_name('imperial')}",
        reply_markup=main_menu()
    )
    await state.set_state(UserStates.MAIN_MENU)


@router.message(F.text == "/help")
async def cmd_help(message: Message):
    help_text = (
        "ℹ️ Помощь по боту:\n\n"
        "/start - Начать работу с ботом\n"
        "/help - Показать справку\n"
        "/subscribe - Подписаться на ежедневные события\n"
        "/unsubscribe - Отписаться от ежедневных событий\n\n"
        "Используйте кнопки меню для настройки бота и получения событий"
    )
    await message.answer(
        help_text,
        reply_markup=main_menu()
    )


@router.message(F.text == "/unsubscribe")
async def cmd_unsubscribe(message: Message):
    user_id = message.from_user.id
    if user_id in user_data.get('subscribers', {}):
        del user_data['subscribers'][user_id]
        await message.answer(
            "❌ Вы отписались от ежедневных исторических событий",
            reply_markup=main_menu()
        )
    else:
        await message.answer(
            "ℹ️ Вы не подписаны на ежедневные события",
            reply_markup=main_menu()
        )