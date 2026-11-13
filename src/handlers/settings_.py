from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from src.states import StateMenu
from src.keyboards import settings_kb, settings_kb_language, settings_kb_premium

router = Router()

@router.message(StateMenu.settings, F.text == "Изменить язык")
async def settings_language(message, state: FSMContext):
    await message.answer(
        "Выберите язык:\n"
        "1. Русский\n"
        "2. English\n"
        "3. Українська\n"
        "4. Назад\n", reply_markup=settings_kb_language)

@router.message(StateMenu.settings, F.text == "Купить Премиум")
async def settings_premium(message, state: FSMContext):
    await message.answer("Активируй Premium и будь в топе ✨""\n"
                          "\n"
                         "Выделяйся среди других:\n"
                         "📈 Больше показов анкеты\n"
                         "🚀 Больше лайков\n"
                         "👀 Твои лайки видят первыми\n"
                         "⭐️ Твоя анкета выше остальных\n"
                         "\n"
                         "Больше внимания. Больше взаимных. Больше знакомств 💫\n"
                         "\n"
                         "Выбери срок действия Premium:\n"
                         "\n"
                         "• 2 дня • ⭐ 150\n"
                         "\n"
                         "• 10 дней • ⭐ 350\n"
                         "\n"\
                         "• 30 дней • ⭐ 500\n"
                         "\n"
                         "• 90 дней • ⭐ 1000\n"
                         "\n"
                         "*Оплачивая Premium, ты принимаешь условия покупки", reply_markup=settings_kb_premium)

@router.message(StateMenu.settings, F.text == "Написать в поддержку")
async def settings_support(message, state: FSMContext):
    await message.answer(
        "Если у вас возникли вопросы или проблемы, вы можете связаться с нашей поддержкой. "
        "Пожалуйста, опишите вашу проблему или вопрос, и мы постараемся помочь вам как можно скорее.\n"
        "\n"
        "Вы можете написать на:\n")
    await message.answer(
        "Telegram: @YourSupportUsername\n"
        "Email: supportdatingapp@gmail.com\n")
    

@router.message(StateMenu.settings, F.text == "Назад")
async def settings_back(message, state: FSMContext):
    await message.answer(
        "1. Изменить язык\n"
        "2. Купить Премиум\n"
        "3. Написать в поддержку\n"
        "4. Назад\n", reply_markup=settings_kb)