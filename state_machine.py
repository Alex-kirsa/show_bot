from aiogram.fsm.state import State, StatesGroup
class MailingForm(StatesGroup):
    message = State()
    delay = State()


    