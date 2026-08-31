from aiogram.fsm.state import StatesGroup, State

class StateRegistration(StatesGroup):
    name = State()
    age = State()
    gender = State()
    city = State()
    description = State()
    looking_for = State()
    photo = State()
    confirm = State()

class StateMenu(StatesGroup):
    menu = State()
    show_profile = State()
    check_profiles = State()
    settings = State()
    anketa = State


