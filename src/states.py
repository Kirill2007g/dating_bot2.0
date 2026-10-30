from aiogram.fsm.state import StatesGroup, State

class StateRegistration(StatesGroup):
    name = State()
    age = State()
    gender = State()
    city = State()
    description = State()
    looking_for = State()
    media = State()
    confirm = State()



class StateMenu(StatesGroup):
    menu = State()
    show_profile = State()
    check_profiles = State()
    settings = State()
    anketa = State()
    edit_anketa = State()
    edit_media = State()
    edit_description = State()



#StateMenu
# menu ->Смотреть анкеты, мой профиль, настройки, заполнить анкету заново
#check_profiles, my_profile, settings, edit_anketa
#для check_profiles отдельный роутер сделать вообще лучше всего будет
#settings отдельный роутер тоже мб сделать чекну
#edit anketa аналогично еще роутер