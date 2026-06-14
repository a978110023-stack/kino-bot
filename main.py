import json
import random
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = "8861590532:AAHzSXGviJLBazHIF7Oj-Fg-UhgVjPh525o"
ADMIN_ID = 8756316671

CHANNEL_USERNAME = "@kino_024"

DB_FILE = "movies.json"
USERS_FILE = "users.json"

try:
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        users = set(json.load(f))
except:
    users = set()

try:
    with open(DB_FILE, "r", encoding="utf-8") as f:
        movies = json.load(f)
except:
    movies = {}

waiting_for_movie = set()


def save_users():
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(list(users), f)


def save_movies():
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(movies, f)


def generate_code():
    while True:
        code = str(random.randint(1000, 9999))
        if code not in movies:
            return code


async def check_sub(update, context):
    try:
        member = await context.bot.get_chat_member(
            CHANNEL_USERNAME,
            update.effective_user.id
        )

        return member.status in [
            "member",
            "administrator",
            "creator",
            "owner",
        ]
    except:
        return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in users:
        users.add(user_id)
        save_users()

    if not await check_sub(update, context):
        await update.message.reply_text(
            "❌ Avval @kino_024 kanaliga obuna bo'ling!"
        )
        return

    await update.message.reply_text(
        "🎬 Kino botga xush kelibsiz!\n\nKino kodini yuboring."
    )


async def addmovie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    waiting_for_movie.add(update.effective_user.id)

    await update.message.reply_text(
        "📤 Endi kinoni video ko'rinishida yuboring."
    )


async def video_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id != ADMIN_ID:
        return

    if user_id not in waiting_for_movie:
        return

    file_id = update.message.video.file_id

    code = generate_code()

    movies[code] = file_id
    save_movies()

    waiting_for_movie.remove(user_id)

    await update.message.reply_text(
        f"✅ Kino saqlandi!\n🎟 Kod: {code}"
    )


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    await update.message.reply_text(
        f"👥 Foydalanuvchilar soni: {len(users)}"
    )


async def search_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_sub(update, context):
        await update.message.reply_text(
            "❌ Avval @kino_024 kanaliga obuna bo'ling!"
        )
        return

    code = update.message.text.strip()

    if code in movies:
        await update.message.reply_video(movies[code])
    else:
        await update.message.reply_text(
            "❌ Bunday kodli kino topilmadi."
        )


app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("addmovie", addmovie))
app.add_handler(CommandHandler("stats", stats))
app.add_handler(MessageHandler(filters.VIDEO, video_handler))
app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, search_movie)
)

print("Bot ishga tushdi...")
app.run_polling()
