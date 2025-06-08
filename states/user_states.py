from aiogram.fsm.state import State, StatesGroup

class UserStates(StatesGroup):
    MAIN_MENU = State()
    SELECT_CITY = State()
    SELECT_ERA = State()
    SELECT_TIME = State()