import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from config.settings import TOKEN
from routers import commands, callbacks, states_handlers
from states.user_states import UserStates
from middlewares.throttling import ThrottlingMiddleware
from services.wikidata_client import get_city_wikidata_id
from keyboards.inline import main_menu, cancel
from storage.user_data import user_data


async def main():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)


    file_handler = logging.FileHandler("bot.log", encoding="utf-8", mode="a")
    file_handler.setLevel(logging.INFO)
    file_fmt = logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
        "%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_fmt)
    logger.addHandler(file_handler)

    # Инициализация бота
    bot = Bot(
        token=TOKEN,
        default=DefaultBotProperties(parse_mode="HTML")
    )
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Регистрация middleware
    dp.message.middleware(ThrottlingMiddleware(limit=0.5))

    # Регистрация роутеров
    dp.include_router(commands.router)
    dp.include_router(callbacks.router)
    dp.include_router(states_handlers.router)

    # Обработчик для состояния SELECT_CITY
    @dp.message(UserStates.SELECT_CITY)
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

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    logging.info("Starting bot...")
    asyncio.run(main())