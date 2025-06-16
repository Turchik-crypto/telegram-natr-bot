import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import io
import ccxt
import asyncio

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: CallbackContext.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("💰 Поддержать", url="https://tronscan.org/#/address/TCmsD5utfKXP47hRGnS2L5Yx1yq4a98zQy")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    welcome_text = (
        "👋 Добро пожаловать в Turchik Crypto Bot!

"
        "Этот бот поможет тебе точно рассчитать параметры входа в сделку на фьючерсах Binance:

"
        "🔹 Учитывает волатильность монеты (NATR)
"
        "🔹 Автоматически рассчитывает:
"
        "  • Стоп в %
"
        "  • Тейк-профит в %
"
        "  • Размер позиции ($)
"
        "  • Потенциальный убыток и прибыль
"
        "🔹 Отправляет уведомления при изменении NATR на более чем 1%

"
        "🚀 Как начать:
"
        "Введи название монеты (например: BTC/USDT)
"
        "Выбери направление сделки (Лонг или Шорт)
"
        "Укажи свой депозит
"
        "Введи желаемый риск в $

"
        "💡 Комиссии учтены в расчётах.
"
    )
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def echo(update: Update, context: CallbackContext.DEFAULT_TYPE):
    symbol = update.message.text.strip().upper()
    await update.message.reply_text(f"📈 Запрашиваю график для {symbol}...")

    exchange = ccxt.binance()
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe='1h', limit=50)
        times = [x[0] for x in ohlcv]
        prices = [x[4] for x in ohlcv]

        plt.figure(figsize=(10, 4))
        plt.plot(times, prices, label=symbol)
        plt.title(f"{symbol} - 1h")
        plt.xlabel("Time")
        plt.ylabel("Price")
        plt.grid(True)
        plt.legend()
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        await update.message.reply_photo(photo=buf)
        buf.close()
    except Exception as e:
        logger.error(e)
        await update.message.reply_text("❌ Ошибка получения данных. Попробуйте позже.")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    app.run_polling()

if __name__ == "__main__":
    main()