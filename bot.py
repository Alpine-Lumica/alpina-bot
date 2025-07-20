import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "@alpina_water")

LANGUAGE, NAME, PHONE, ADDRESS, QUANTITY = range(5)

lang_texts = {
    'ru': {'start': 'Выберите язык', 'name': 'Введите ваше имя:', 'phone': 'Введите номер телефона:',
           'address': 'Введите адрес доставки:', 'qty': 'Сколько бутылей вам нужно?', 'thanks': 'Спасибо! Заказ отправлен.',
           'paid': 'Оплата при доставке. Минимальный заказ 48 000 сум.'},
    'uz': {'start': 'Tilni tanlang', 'name': 'Ismingizni kiriting:', 'phone': 'Telefon raqamingizni kiriting:',
           'address': 'Yetkazib berish manzilini kiriting:', 'qty': 'Nechta butilka kerak?', 'thanks': 'Rahmat! Buyurtma yuborildi.',
           'paid': 'To‘lov yetkazib berilganda. Minimal buyurtma 48 000 so‘m.'},
    'en': {'start': 'Choose your language', 'name': 'Enter your name:', 'phone': 'Enter your phone number:',
           'address': 'Enter your delivery address:', 'qty': 'How many bottles do you need?', 'thanks': 'Thanks! Order sent.',
           'paid': 'Payment upon delivery. Minimum order 48,000 UZS.'}
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [['🇷🇺 Русский', '🇺🇿 O‘zbek', '🇬🇧 English']]
    await update.message.reply_text("🌊 ALPINA - Premium Ichimlik Suvi Выберите язык / Tilni tanlang / Choose your language:",
                                    reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True))
    return LANGUAGE

async def choose_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if 'Русский' in text:
        lang = 'ru'
    elif 'O‘zbek' in text:
        lang = 'uz'
    else:
        lang = 'en'
    context.user_data['lang'] = lang
    await update.message.reply_text(lang_texts[lang]['name'])
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    lang = context.user_data['lang']
    await update.message.reply_text(lang_texts[lang]['phone'])
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone'] = update.message.text
    lang = context.user_data['lang']
    await update.message.reply_text(lang_texts[lang]['address'])
    return ADDRESS

async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['address'] = update.message.text
    lang = context.user_data['lang']
    await update.message.reply_text(lang_texts[lang]['qty'])
    return QUANTITY

async def get_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['qty'] = update.message.text
    lang = context.user_data['lang']
    data = context.user_data
    qty = int(''.join(filter(str.isdigit, data['qty'])))
    price = qty * 12000
    delivery_note = " if price >= 48000 else f 🚚 {lang_texts[lang]['paid']]}"

    msg = (
        f"🧾 Новый заказ:"
        
        f"Имя: {data['name']}"
        
        f"Телефон: {data['phone']}"
        
        f"Адрес: {data['address']}"
        
        f"Количество бутылей: {qty}" 
        
        f"💰 Сумма: {price} сум{delivery_note}"
    )
    await context.bot.send_message(chat_id=ADMIN_USERNAME, text=msg)
    await update.message.reply_text(lang_texts[lang]['thanks'])
    return ConversationHandler.END

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LANGUAGE: [MessageHandler(filters.TEXT, choose_language)],
            NAME: [MessageHandler(filters.TEXT, get_name)],
            PHONE: [MessageHandler(filters.TEXT, get_phone)],
            ADDRESS: [MessageHandler(filters.TEXT, get_address)],
            QUANTITY: [MessageHandler(filters.TEXT, get_quantity)],
        },
        fallbacks=[],
    )
    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == '__main__':
    main()
