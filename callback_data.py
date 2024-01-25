from aiogram.filters.callback_data import CallbackData

class ChooseLanguage(CallbackData, prefix="chlang"):
    lang: str
