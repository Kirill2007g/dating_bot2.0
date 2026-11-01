from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from src.states import StateMenu

router = Router()

@router.message(StateMenu.settings, F.text ==)