# bot.py
import os
import aiohttp
import requests              
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ODDS_API_KEY = os.getenv("ODDS_API_KEY")

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

# Главное меню
MAIN_MENU = {
    "ru": ["Крипта", "Прогноз", "Подписка", "AI прогноз", "Язык"],
    "en": ["Crypto", "Forecast", "Subscribe", "AI Forecast", "Language"],
    "ua": ["Крипта", "Прогноз", "Підписка", "AI прогноз", "Мова"],
    "pl": ["Krypto", "Prognoza", "Subskrypcja", "AI prognoza", "Język"]
}

USER_LANG = {}
SUBSCRIBERS = set()

def is_subscribed(user_id):
    return user_id in SUBSCRIBERS

def get_lang(user_id):
    return USER_LANG.get(user_id, "ru")

def main_menu(lang):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for btn in MAIN_MENU.get(lang, MAIN_MENU["ru"]):
        kb.add(KeyboardButton(btn))
    return kb

@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    user_id = msg.from_user.id
    lang = get_lang(user_id)
    await msg.answer("👋 Добро пожаловать!", reply_markup=main_menu(lang))

@dp.message_handler(commands=["admin"])
async def admin_panel(msg: types.Message):
    await msg.answer(f"📋 Список пользователей: {', '.join(map(str, USER_LANG.keys()))}")

@dp.message_handler(lambda m: m.text.lower() in ["крипта", "crypto"])
async def crypto_info(msg: types.Message):
    await msg.answer("🪙 Bitcoin: $100546\nEthereum: $506.68\nRipple: $2.15")

@dp.message_handler(lambda m: m.text.lower() in ["прогноз", "forecast", "prognoza"])
async def forecast(msg: types.Message):
    await msg.answer("📉 Сегодня прогнозов нет.")

@dp.message_handler(lambda m: m.text.lower() in ["подписка", "subscribe", "subskrypcja"])
async def subs(msg: types.Message):
    SUBSCRIBERS.add(msg.from_user.id)
    await msg.answer("✅ Вы подписались.")

@dp.message_handler(lambda m: m.text.lower() in ["язык", "language", "мова", "język"])
async def lang_select(msg: types.Message):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(*[KeyboardButton(LANGUAGES[k]) for k in LANGUAGES])
    await msg.answer("🌐 Выберите язык:", reply_markup=kb)

@dp.message_handler(lambda m: m.text in LANGUAGES.values())
async def set_language(msg: types.Message):
    code = next((k for k, v in LANGUAGES.items() if v == msg.text), "ru")
    USER_LANG[msg.from_user.id] = code
    await msg.answer(f"✅ Язык установлен: {msg.text}", reply_markup=main_menu(code))

def get_ai_prediction():
    url = "https://api.the-odds-api.com/v4/sports/soccer_epl/odds"
    params = {
        "apiKey": ODDS_API_KEY,
        "regions": "eu",
        "markets": "h2h",
        "oddsFormat": "decimal"
    }

    try:
        res = requests.get(url, params=params)
        if res.status_code != 200:
            return "⚠️ Прогноз временно недоступен."

        data = res.json()
        if not data:
            return "⚠️ Матчи не найдены."

        match = data[0]
        teams = match["teams"]
        odds = match["bookmakers"][0]["markets"][0]["outcomes"]
        best = max(odds, key=lambda x: x["price"])
        confidence = round(1 / best["price"] * 100, 2)

        return (
            f"🧠 AI прогноз:\n"
            f"⚽ {teams[0]} vs {teams[1]}\n"
            f"📅 {match['commence_time'][:10]} {match['commence_time'][11:16]}\n"
            f"✅ Победа: {best['name']}\n"
            f"📊 Уверенность: {confidence}%"
        )
    except Exception:
        return "⚠️ Ошибка получения прогноза."

@dp.message_handler(lambda m: m.text.lower() in ["ai прогноз", "ai forecast", "ai prognoza"])
async def ai_forecast(msg: types.Message):
    user_id = msg.from_user.id
    if not is_subscribed(user_id):
        await msg.answer("❌ Эта функция доступна только подписчикам.\nНажмите /subscribe.")
async def check_subscription(user_id):
    # Пока логика фиктивная — ты можешь здесь запрос к базе Firebase или другое API
    return user_id in SUBSCRIBERS

    prediction = get_ai_prediction()
    await msg.answer(prediction)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)@dp.message_handler(lambda m: m.text.lower() == 'ai прогноз')
async def ai_forecast(msg: types.Message):
    if not await check_subscription(msg.from_user.id):
        await msg.answer("❌ Доступно только подписчикам.")
        return

    headers = {"X-API-Key": os.getenv("ODDS_API_KEY")}
    params = {"regions": "eu", "markets": "h2h", "oddsFormat": "decimal"}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.the-odds-api.com/v4/sports/soccer_epl/odds", params=params, headers=headers) as resp:
                data = await resp.json()

        if not data:
            await msg.answer("⚠️ Нет подходящих матчей на сегодня.")
            return

        match = data[0]
        home = match["home_team"]
        away = match["away_team"]
        odds = match["bookmakers"][0]["markets"][0]["outcomes"]
        home_odds = odds[0]["price"]
        away_odds = odds[1]["price"]
        favorite = home if home_odds < away_odds else away
        confidence = round(100 / min(home_odds, away_odds))

        text = f"🤖 *AI Прогноз*\nМатч: *{home} vs {away}*\n📈 Победит: *{favorite}*\nУверенность: *{confidence}%*"
        await msg.answer(text, parse_mode="Markdown")

    except Exception as e:
        await msg.answer(f"Ошибка при получении прогноза: {str(e)}")
