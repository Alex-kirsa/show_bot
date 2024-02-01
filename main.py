import asyncio
import logging
import sys

from icecream import ic

from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import json_response

from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.enums import ParseMode
from aiogram.enums.content_type import ContentType
from aiogram.filters import CommandStart, Command, MagicData
from aiogram.types import Message, CallbackQuery
from aiogram.methods.answer_web_app_query import AnswerWebAppQuery
from aiogram.utils.markdown import hbold
from aiogram.utils.web_app import safe_parse_webapp_init_data, WebAppInitData
from aiogram.fsm.context import FSMContext
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application


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
get_info_gs = Router()
special_abilities = Router()
empty = Router()

dp = Dispatcher()
dp.include_routers(site_job, mailing, user_info, sheets, message_analysis, get_info_gs, special_abilities, empty)

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

@dp.message(F.text==MESSAGES["MAIN_MENU"]["UA"])
@dp.message(F.text==MESSAGES["MAIN_MENU"]["RU"])
async def main_memu_message(message:Message):
    lang = db.get_language_by_id(message.from_user.id)
    await message.delete()
    await message.answer(\
        text=MESSAGES["MAIN_MENU"][lang],\
        reply_markup=rp_marcups.main_menu_marcup(lang))


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
            await message.answer(\
                MESSAGES["MAIN_MENU"]["MAILING"]["SHOW_RESULT"][lang]%message.text,\
                reply_markup=rp_marcups.chosen_language_marcup(lang)\
            )
            await bot.copy_message(\
                chat_id=message.from_user.id,\
                from_chat_id=message.from_user.id,\
                message_id=data["message_id"]\
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
async def message_analysis_handler(message: Message, state:FSMContext) -> None:
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



@get_info_gs.callback_query(cb_data.MainMenu.filter(F.section=="GET_VALUES_FROM_GS"))
async def get_info_gs_query(query: CallbackQuery):
    lang = db.get_language_by_id(query.from_user.id)
    await query.message.delete()
    values = gs.wks.get_all_values()
    text = '\n'.join(['. '.join(item) for item in values])
    text += "\n"+MESSAGES["MAIN_MENU"]["GET_VALUES_FROM_GS"]["LINK_TO_SPREADSHEET"][lang]%SPREADSHEET_URL
    await query.message.answer(text)



@special_abilities.callback_query(cb_data.MainMenu.filter(F.section=="SPECIAL_ABILITIES"))
async def special_abilities_query(query: CallbackQuery):
    lang = db.get_language_by_id(query.from_user.id)
    #await query.message.delete()
    for i in range(len(MESSAGES["MAIN_MENU"]["SPECIAL_ABILITIES"])+1):
        await query.message.edit_text(MESSAGES["MAIN_MENU"]["SPECIAL_ABILITIES"]["MESSAGES"][f"MES_{i}"][lang])
        await asyncio.sleep(2.5)
    await query.message.delete()



@dp.message(content_types=types.ContentType.WEB_APP_DATA)
async def web_send_message(request):
    print("HGRFHRSBVFGHBSRF")
    bot: Bot = request.app["bot"]

    data = await request.post()  # application/x-www-form-urlencoded
    try:
        data = safe_parse_webapp_init_data(token=bot.token, init_data=data["/send_message"])
    except ValueError:
        return json_response({"ok": False, "err": "Unauthorized"}, status=401)
    ic(json_response({"ok": True, "data": data.user.dict()}))
    asyncio.sleep(0)



@empty.message()
async def echo_handler(message: types.Message) -> None:
    lang = db.get_language_by_id(message.from_user.id)
    await message.answer(MESSAGES["START_MESSAGE"]["PRESS_START_TO_START"][lang])



async def main() -> None:
    await dp.start_polling(bot)



#app = web.Application()
#app["bot"] = bot
#app["dispatcher"] = dp
#app.add_routes([web.post('/send-message', web_send_message)])
#SimpleRequestHandler(
#        dispatcher=dp,
#        bot=bot,
#    ).register(app, path="/send-message")
#setup_application(app, dp, bot=bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    loop = asyncio.new_event_loop()
    #asyncio.run(loop.create_task(web_send_message()))
    try:
    
        #loop = asyncio.new_event_loop()
        #loop.create_task()
        #web.run_app(app, host="127.0.0.1", port=8080)
        #asyncio.run(bot.set_webhook(url="https://chimerical-axolotl-a80fde.netlify.app/"))
        asyncio.run(loop.create_task(main()))
        
    except:
        pass




