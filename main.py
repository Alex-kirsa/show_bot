import asyncio
import logging
import sys

from icecream import ic

from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.markdown import hbold
from aiogram.fsm.context import FSMContext

from config.settings import BOT_TOKEN
from messages import MESSAGES
from database import db

from google_sheets.gspred import gs, SPREADSHEET_URL
from state_machine import MailingForm, WorkWithSheetsForm, MessageAnalysisForm
from reply_marcups import rp_marcups
import callback_data as cb_data


site_job = Router()
mailing:Router = Router()
user_info = Router()
sheets = Router()
message_analysis = Router()
empty = Router()

dp = Dispatcher()
dp.include_routers(site_job, mailing, user_info, sheets, message_analysis, empty)

bot = Bot(BOT_TOKEN, parse_mode=ParseMode.HTML)


@dp.message(CommandStart())
@dp.message(Command("language"))
async def command_start_handler(message:Message) -> None:
    db.check_user_in_db(message.from_user.id)
    lang = db.get_language_by_id(message.from_user.id)
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



@mailing.callback_query(cb_data.MainMenu.filter(F.section=="MAILING"))
async def choose_mailing(query: CallbackQuery, callback_data:cb_data.MainMenu, state:FSMContext):
    lang = db.get_language_by_id(query.from_user.id)
    await query.message.delete()
    await state.set_state(MailingForm.message)
    await query.message.answer(\
        text=MESSAGES["MAIN_MENU"]["MAILING"]["SEND_MESSAGE"][lang])
    
@mailing.message(MailingForm.message)
async def mailing_get_message(message:Message, state:FSMContext):
    lang = db.get_language_by_id(message.from_user.id)
    await state.set_data({"message_id": message.message_id})
    await state.set_state(MailingForm.delay)
    await message.answer(\
        text=MESSAGES["MAIN_MENU"]["MAILING"]["SEND_DELAY"][lang])
    
@mailing.message(MailingForm.delay)
async def mailing_get_message(message:Message, state:FSMContext):
    lang = db.get_language_by_id(message.from_user.id)

    try:
        if((1<=int(message.text)) and (int(message.text)<=60)):
            await asyncio.sleep(int(message.text))
            data = await state.get_data()
            await bot.copy_message(\
                chat_id=message.from_user.id,\
                from_chat_id=message.from_user.id,\
                message_id=data["message_id"]\
            )
            await message.answer(\
                MESSAGES["MAIN_MENU"]["MAILING"]["SHOW_RESULT"][lang]%message.text,\
                reply_markup=rp_marcups.chosen_language_marcup(lang)\
            )
            await state.clear()
        else:
            await message.answer(MESSAGES["MAIN_MENU"]["MAILING"]["NUM_IS_NOT_VALID"][lang])
    except:
        await message.answer(MESSAGES["MAIN_MENU"]["MAILING"]["SEND_DELAY"][lang])



@user_info.callback_query(cb_data.MainMenu.filter(F.section=="USER_INFO"))
async def user_info_callback(query: CallbackQuery, callback_data:cb_data.MainMenu, state:FSMContext):
    lang = db.get_language_by_id(query.from_user.id)
    await query.message.delete()
    await query.message.answer(\
        text=MESSAGES["MAIN_MENU"]["USER_INFO"]["ALL_INFO_I_OWE"][lang],\
        reply_markup=rp_marcups.chosen_language_marcup(lang))
    l = [el for el in query.from_user]
    l1 = list()
    for i in range(len(l)):
        l1.append(f"{l[i][0]}: {l[i][1]}")
    await query.message.answer(text="\n".join(l1))



@sheets.callback_query(cb_data.MainMenu.filter(F.section=="GOOGLE_SHEETS_WORK"))
async def work_with_sheets(query: CallbackQuery, state:FSMContext):
    lang = db.get_language_by_id(query.from_user.id)
    await query.message.delete()
    await query.message.answer(MESSAGES["MAIN_MENU"]["GOOGLE_SHEETS_WORK"]["SEND_ME_MESSAGE"][lang])
    
    await state.set_state(WorkWithSheetsForm.message)

@sheets.message(WorkWithSheetsForm.message)
async def work_with_sheets(message: Message, state:FSMContext):
    lang = db.get_language_by_id(message.from_user.id)
    try:
        count = len(gs.wks.get_all_values())
        gs.wks.insert_row([count-1, message.text], index=count+1)

        await message.answer(MESSAGES["MAIN_MENU"]["GOOGLE_SHEETS_WORK"]["I_HAVE_ENTERED_MESSAGE"][lang]%(count-1, SPREADSHEET_URL),\
                             reply_markup=rp_marcups.chosen_language_marcup(lang))
        await state.clear()
    except:
        await message.answer(MESSAGES["MAIN_MENU"]["GOOGLE_SHEETS_WORK"]["SEND_ME_MESSAGE"][lang])



@message_analysis.callback_query(cb_data.MainMenu.filter(F.section=="MESSAGE_ANALYSIS"))
async def message_analysis_callback(query: CallbackQuery, state:FSMContext):
    lang = db.get_language_by_id(query.from_user.id)
    await query.message.delete()
    await state.set_state(MessageAnalysisForm.message)
    await query.message.answer(MESSAGES["MAIN_MENU"]["MESSAGE_ANALYSIS"]["SEND_ME_MESSAGE"][lang])
    
    await state.set_state(MessageAnalysisForm.message)

@message_analysis.message(MessageAnalysisForm.message)
async def message_analysis_handlen(message: types.Message, state:FSMContext) -> None:
    lang = db.get_language_by_id(message.from_user.id)
    l = list()
    for el in message:
        if len(el)==2:
            if type(el[1])!=type(message.sender_chat):
                l.append(el[0])
    await state.clear()
    #await message.send_copy(chat_id=message.chat.id)
    await message.answer(MESSAGES["MAIN_MENU"]["MESSAGE_ANALYSIS"]["YOU_SENT_ME"][lang]%(l[4]),\
                         reply_markup=rp_marcups.chosen_language_marcup(lang))



@empty.message()
async def echo_handler(message: types.Message) -> None:
    #try:
    await message.send_copy(chat_id=message.chat.id)
    #await message.answer()
    #except TypeError:
    #    await message.answer("Nice try!")


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except:
        pass




