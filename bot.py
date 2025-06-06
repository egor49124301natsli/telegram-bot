import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError("Missing TELEGRAM_TOKEN")

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)

# Языки
LANGUAGES = {
    "ru": "Русский",
    "en": "English",
    "ua": "Українська",
    "pl": "Polski"
}
USER_LANG = {}

# Меню
def get_main_menu(lang="ru"):
    menu = {
        "ru": ["Крипта", "Прогноз", "Подписка", "Язык"],
        "en": ["Crypto", "Forecast", "Subscribe", "Language"],
        "ua": ["Крипта", "Прогноз", "Підписка", "Мова"],
        "pl": ["Krypto", "Prognoza", "Subskrypcja", "Język"]
    }
    buttons = [KeyboardButton(text) for text in menu.get(lang, menu["ru"])]
    return ReplyKeyboardMarkup(resize_keyboard=True).add(*buttons)

@dp.message_handler(commands=["start"])
async def start_cmd(msg: types.Message):
    lang = USER_LANG.get(msg.from_user.id, "ru")
    await msg.answer("🤖 Добро пожаловать!" if lang == "ru" else "🤖 Welcome!",
                     reply_markup=get_main_menu(lang))

@dp.message_handler(commands=["help"])
async def help_cmd(msg: types.Message):
    await msg.reply("Команды: /start, /help, /predict, /subscribe")

@dp.message_handler(commands=["predict"])
async def predict_cmd(msg: types.Message):
    await msg.answer("📊 Сегодня прогнозов нет. Попробуйте позже.")

@dp.message_handler(commands=["subscribe"])
async def subscribe_cmd(msg: types.Message):
    await msg.answer("🔔 Подписка оформлена! (фиктивно)")

@dp.message_handler(lambda m: m.text in LANGUAGES.values())
async def set_language(msg: types.Message):
    for code, name in LANGUAGES.items():
        if msg.text == name:
            USER_LANG[msg.from_user.id] = code
            await msg.answer(f"✅ Язык установлен: {name}", reply_markup=get_main_menu(code))
            break

@dp.message_handler(lambda m: m.text.lower() in ["крипта", "crypto"])
async def crypto_info(msg: types.Message):
    await msg.answer("📈 Bitcoin: $100546\nEthereum: $506.68\nRipple: $2.15")

@dp.message_handler(lambda m: m.text.lower() in ["прогноз", "forecast"])
async def forecast(msg: types.Message):
    await msg.answer("📊 Сегодня прогнозов нет.")

@dp.message_handler(lambda m: m.text.lower() in ["подписка", "subscribe"])
async def subs(msg: types.Message):
    await msg.answer("🔔 Вы подписались.")

@dp.message_handler(lambda m: m.text.lower() in ["язык", "language", "мова", "język"])
async def lang_select(msg: types.Message):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(*[KeyboardButton(v) for v in LANGUAGES.values()])
    await msg.answer("🌍 Выберите язык:", reply_markup=kb)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)