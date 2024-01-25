import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.utils.markdown import hbold

from settings import BOT_TOKEN
from messages import MESSAGES
from database import db


dp = Dispatcher()
bot = Bot(BOT_TOKEN, parse_mode=ParseMode.HTML)


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    lang = db.get_language_by_id(message.from_user.id)
    await message.answer(MESSAGES["START_MESSAGE"][lang])


@dp.message(Command("language"))
async def command_language_handler(message: Message) -> None:
    lang = db.get_language_by_id(message.from_user.id)

    await message.answer(MESSAGES["START_MESSAGE"][lang])


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
    asyncio.run(main())




