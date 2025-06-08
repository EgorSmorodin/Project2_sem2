from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states.user_states import UserStates
from services.wikidata_client import get_city_wikidata_id
from keyboards.inline import main_menu, cancel
from storage.user_data import user_data
import logging

router = Router()
logger = logging.getLogger(__name__)


@router.message(UserStates.SELECT_CITY)
async def process_city(message: Message, state: FSMContext):
    city = message.text
    user_id = message.from_user.id
    city_id = await get_city_wikidata_id(city)

    if not city_id:
        await message.answer(
            f"❌ Город '{city}' не найден. Попробуйте снова.",
            reply_markup=cancel()
        )
        return

    if user_id not in user_data:
        user_data[user_id] = {}

    user_data[user_id]['city'] = city
    user_data[user_id]['city_id'] = city_id
    user_data[user_id]['shown_events'] = set()

    await message.answer(
        f"✅ Город изменён на {city}",
        reply_markup=main_menu()
    )
    await state.set_state(UserStates.MAIN_MENU)