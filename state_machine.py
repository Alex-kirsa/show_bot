from aiogram.fsm.state import State, StatesGroup
class MailingForm(StatesGroup):
    message = State()
    delay = State()


class WorkWithSheetsForm(StatesGroup):
    message = State()


class MessageAnalysisForm(StatesGroup):
    message = State()