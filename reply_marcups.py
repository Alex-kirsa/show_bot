from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.types.inline_keyboard_button import InlineKeyboardButton

from aiogram.types.reply_keyboard_markup import ReplyKeyboardMarkup
from aiogram.types.keyboard_button import KeyboardButton

from icecream import ic

from messages import MESSAGES, LANGUAGES
from database import db
import callback_data as cb_data


class ReplyMarcups:
    def command_start_marcup(self):
        buttons_list = list()
        for lang in LANGUAGES:
            buttons_list.append(\
                InlineKeyboardButton(\
                    text=MESSAGES["LANGUAGE"][lang],\
                    callback_data=cb_data.ChooseLanguage(language=lang).pack())\
                )
            
        return InlineKeyboardMarkup(inline_keyboard=[buttons_list])

    def chosen_language_marcup(self, lang:str):
        #return InlineKeyboardMarkup(inline_keyboard=[[self._main_menu_button("MAIN_MENU", lang)]])
        button = KeyboardButton(text=MESSAGES["MAIN_MENU"][lang])
        return ReplyKeyboardMarkup(keyboard=[[button]], resize_keyboard=True)
        
    def main_menu_marcup(self, lang:str):
        buttons_list = list()
        for el in MESSAGES["MAIN_MENU"]:
                if(len(el)>2):
                    buttons_list.append(self._main_menu_button(el, lang))

        return InlineKeyboardMarkup(inline_keyboard=[[el] for el in buttons_list])
                
    def site_job_marcup(self, lang:str):
        button = InlineKeyboardButton(\
                    text=MESSAGES["MAIN_MENU"]["SITE_JOB"]["FILL_THE_FORM"][lang],\
                    url="https://shorturl.at/isBOV",\
                )

        return InlineKeyboardMarkup(inline_keyboard=[[button]])

    def _main_menu_button(self, section:str, lang:str):
        if section=="MAIN_MENU":
            text = MESSAGES[section][lang]
        else:
            text = MESSAGES["MAIN_MENU"][section][lang]

        return InlineKeyboardButton(\
                    text=text,\
                    callback_data=cb_data.MainMenu(section=section).pack()\
                )
    
    def main_menu_reply_keyboard_marcup_button(self, lang):
        button = KeyboardButton(text=MESSAGES["MAIN_MENU"][lang])

        return ReplyKeyboardMarkup(keyboard=[[button]])

rp_marcups = ReplyMarcups()












