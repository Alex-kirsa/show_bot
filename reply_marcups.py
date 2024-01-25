from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.types.inline_keyboard_button import InlineKeyboardButton

from icecream import ic

from messages import MESSAGES, LANGUAGES
from database import db
import callback_data as cb_data


def command_start_marcup():
    buttons_list = list()
    for lang in LANGUAGES:
        buttons_list.append(\
            InlineKeyboardButton(\
                text=MESSAGES["LANGUAGE"][lang],\
                callback_data=cb_data.ChooseLanguage(language=lang).pack())\
            )
        
    return InlineKeyboardMarkup(inline_keyboard=[buttons_list])


def chosen_language_marcup(lang:str):
    button = InlineKeyboardButton(\
                text=MESSAGES["MAIN_MENU"][lang],\
                callback_data=cb_data.MainMenu().pack()\
            )
    return InlineKeyboardMarkup(inline_keyboard=[[button]])