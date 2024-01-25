import asyncio
import logging
import sys

from icecream import ic

from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.markdown import hbold

from config.settings import BOT_TOKEN
from messages import MESSAGES
from database import db

from reply_marcups import rp_marcups
import callback_data as cb_data


site_job = Router()
mailing = Router()
info_about = Router()
sheets = Router()
analysis = Router()

dp = Dispatcher()
dp.include_routers(site_job, mailing, info_about, sheets, analysis)

bot = Bot(BOT_TOKEN, parse_mode=ParseMode.HTML)


@dp.message(CommandStart())
@dp.message(Command("language"))
async def command_start_handler(message:Message) -> None:
    db.check_user_in_db(message.from_user.id)
    lang = db.get_language_by_id(ic(message.from_user.id))
    await message.answer(\
        MESSAGES["START_MESSAGE"][lang],\
        reply_markup=rp_marcups.command_start_marcup())
    return


@dp.callback_query(cb_data.ChooseLanguage.filter())
async def choose_language_callback(query: CallbackQuery, callback_data:cb_data.ChooseLanguage) -> None:
    lang = callback_data.language
    await query.message.delete()
    db.update_language(query.from_user.id, lang)
    await query.message.answer(\
        text=MESSAGES["LANGUAGE"]["CHOSEN_LANGUAGE"][lang]%MESSAGES["MAIN_MENU"][lang],\
        reply_markup=rp_marcups.chosen_language_marcup(lang))
    return


@dp.callback_query(cb_data.MainMenu.filter(F.section=="MAIN_MENU"))
async def main_menu(query: CallbackQuery, callback_data:cb_data.MainMenu):
    lang = db.get_language_by_id(query.from_user.id)
    await query.message.delete()
    await query.message.answer(\
        text=MESSAGES["MAIN_MENU"][lang],\
        reply_markup=rp_marcups.main_menu_marcup(lang))
    

@site_job.callback_query(cb_data.MainMenu.filter(F.section=="SITE_JOB"))
async def site_job(query: CallbackQuery, callback_data:cb_data.MainMenu):
    lang = db.get_language_by_id(query.from_user.id)
    await query.message.delete()
    await query.message.answer(\
        text=MESSAGES["MAIN_MENU"]["SITE_JOB"]["PRESS_TO_FILL_THE_FORM"][lang],\
        reply_markup=rp_marcups.site_job_marcup(lang))


@mailing.callback_query(cb_data.MainMenu.filter(F.section=="SITE_JOB"))


@dp.message()
async def echo_handler(message: types.Message) -> None:
    try:
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        await message.answer("Nice try!")


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except:
        pass




