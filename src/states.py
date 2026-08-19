from aiogram.fsm.state import StatesGroup, State

class StateRegistration(StatesGroup):
    age = State()
    gender = State()
    name = State()
    city = State()
    description = State()
    looking_for = State()
    photo = State()
    confirm = State()

