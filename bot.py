import logging
import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from google_sheet import add_order_to_sheet
from pdf_generator import generate_pdf

TOKEN = os.getenv('8060264514:AAFvnWV6DoSueOS4yV68SUNwJ-_rpSZxNYE')
bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Здравствуйте! Чтобы заказать воду, напишите количество и адрес.")

@dp.message()
async def handle_order(message: Message):
    user_data = {
        "Имя": message.from_user.full_name,
        "Телефон": message.from_user.id,
        "Сообщение": message.text,
    }
    add_order_to_sheet(user_data)
    pdf_path = generate_pdf(user_data)
    await message.answer_document(types.FSInputFile(pdf_path), caption="Ваш чек")
    os.remove(pdf_path)

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
