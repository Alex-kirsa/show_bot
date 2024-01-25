from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.types.inline_keyboard_button import InlineKeyboardButton

from icecream import ic

from messages import MESSAGES
from database import db
import callback_data as cb_data

def command_start_marcup():
    buttons_list = list()
    for lang in MESSAGES["LANGUAGE_NAMES"]:
        buttons_list.append(
            InlineKeyboardButton(
                text=MESSAGES["LANGUAGE_NAMES"][lang],
                callback_data=cb_data.ChooseLanguage(lang=lang).pack())
            )
        
    return InlineKeyboardMarkup(inline_keyboard=[buttons_list])