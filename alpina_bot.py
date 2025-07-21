
# Обновлённый код Telegram-бота ALPINA с автонапоминанием и готовностью к деплою на Render
import logging
import os
from datetime import datetime, timedelta

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ConversationHandler, ContextTypes, JobQueue
)

# Заглушки для интеграции (Google Sheets)
def save_order_to_sheets(data):
    print("[Mock] Saving to Google Sheets:", data)

# Константы
ADMIN_CHANNEL = '@Alpina_Orders'
MIN_ORDER_SUM = 48000
LANGUAGES = {
    'ru': {
        'greeting': "Выберите язык обслуживания:",
        'ask_name': "Введите ваше имя:",
        'ask_phone': "Введите номер телефона:",
        'ask_address': "Введите адрес доставки:",
        'ask_amount': "Введите сумму заказа в сумах:",
        'less_than_min': f"Сумма меньше {MIN_ORDER_SUM} сумов. Будет добавлена доставка.",
        'thanks': "Спасибо за заказ! Мы скоро свяжемся с вами.",
        'only_number': "Пожалуйста, введите сумму числом.",
        'cancelled': "Операция отменена.",
        'reminder': "💧 Напоминаем: вы можете снова заказать воду ALPINA. Просто введите /start."
    },
    'uz': {
        'greeting': "Xizmat tilini tanlang:",
        'ask_name': "Ismingizni kiriting:",
        'ask_phone': "Telefon raqamingizni kiriting:",
        'ask_address': "Yetkazib berish manzilini kiriting:",
        'ask_amount': "Buyurtma summasini so'mda kiriting:",
        'less_than_min': f"Buyurtma {MIN_ORDER_SUM} so'mdan kam. Yetkazib berish qo‘shiladi.",
        'thanks': "Buyurtma uchun rahmat! Tez orada bog'lanamiz.",
        'only_number': "Iltimos, summani raqam bilan kiriting.",
        'cancelled': "Amal bekor qilindi.",
        'reminder': "💧 Eslatib o'tamiz: siz ALPINA suvini yana buyurtma qilishingiz mumkin. Faqat /start ni yozing."
    }
}

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Состояния
LANG, NAME, PHONE, ADDRESS, AMOUNT = range(5)
user_data_store = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[
        InlineKeyboardButton("Русский 🇷🇺", callback_data="ru"),
        InlineKeyboardButton("O'zbekcha 🇺🇿", callback_data="uz")
    ]]
    await update.message.reply_text(LANGUAGES['ru']['greeting'], reply_markup=InlineKeyboardMarkup(keyboard))
    return LANG

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = query.data
    user_id = query.from_user.id
    context.user_data['lang'] = lang
    user_data_store[user_id] = {'lang': lang}
    await query.edit_message_text(text=LANGUAGES[lang]['ask_name'])
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data_store[user_id]['name'] = update.message.text
    await update.message.reply_text(LANGUAGES[context.user_data['lang']]['ask_phone'])
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data_store[user_id]['phone'] = update.message.text
    await update.message.reply_text(LANGUAGES[context.user_data['lang']]['ask_address'])
    return ADDRESS

async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data_store[user_id]['address'] = update.message.text
    await update.message.reply_text(LANGUAGES[context.user_data['lang']]['ask_amount'])
    return AMOUNT

async def get_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = context.user_data['lang']
    try:
        amount = int(update.message.text)
        user_data_store[user_id]['amount'] = amount

        if amount < MIN_ORDER_SUM:
            await update.message.reply_text(LANGUAGES[lang]['less_than_min'])

        await update.message.reply_text(LANGUAGES[lang]['thanks'], reply_markup=ReplyKeyboardRemove())

        data = user_data_store[user_id]
        save_order_to_sheets(data)

        msg = (f"📦 Новый заказ
"
               f"ФИО: {data['name']}
"
               f"Телефон: {data['phone']}
"
               f"Адрес: {data['address']}
"
               f"Сумма: {amount} сум")

        await context.bot.send_message(chat_id=ADMIN_CHANNEL, text=msg)

        context.job_queue.run_once(reminder_callback, when=timedelta(days=7), data={
            'chat_id': update.effective_chat.id,
            'lang': lang
        })

    except ValueError:
        await update.message.reply_text(LANGUAGES[lang]['only_number'])
        return AMOUNT

    return ConversationHandler.END

async def reminder_callback(context: ContextTypes.DEFAULT_TYPE):
    data = context.job.data
    chat_id = data['chat_id']
    lang = data['lang']
    await context.bot.send_message(chat_id=chat_id, text=LANGUAGES[lang]['reminder'])

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get('lang', 'ru')
    await update.message.reply_text(LANGUAGES[lang]['cancelled'], reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main():
    token = os.getenv("BOT_TOKEN") or "PASTE_YOUR_TOKEN_HERE"
    app = Application.builder().token(token).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LANG: [CallbackQueryHandler(set_language)],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_address)],
            AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_amount)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == '__main__':
    main()
