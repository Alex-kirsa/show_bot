from aiogram.filters.callback_data import CallbackData

class ChooseLanguage(CallbackData, prefix="chlang"):
    language: str

class MainMenu(CallbackData, prefix="mainmenu"):
    pass




