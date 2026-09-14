import os
import re

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# =========================
# تنظیمات
# =========================

TOKEN = os.getenv("BOT_TOKEN")

QUESTIONS = [
    {
        "question": "داریم چه زبانی رو برای مهاجرت کردن می‌خونیم؟",
        "answer": "آلمانی",
    },
    {
        "question": "چه ماهی شروع به قرار گذاشتن کردیم؟",
        "answer": "مرداد",
    },
    {
        "question": "چه کلمه‌ای رو اولا خیلی میگفتم که میگفتی اشکال نداره بگو منم تعدادشونو می‌شمرم؟",
        "answer": "وای",
    },
    {
        "question": "من چه اسم رمزی برات گذاشته بودم که بهت لو دادم؟",
        "answer": "زنجبیل",
    },
    {
        "question": "معادل زیبا؟",
        "answer": "خوشگل",
    },
    {
        "question": "چه کلمه‌ای باعث شد من بیام پیویت؟",
        "answer": "لیبرا",
    },
    {
        "question": "ما برای چه کسی می‌خواستیم یه اتاق جداگونه توی خونه‌مون داشته باشیم؟",
        "answer": "دن",
    },
    {
        "question": "وقتی چی صدام میزنی خیلی خوشم میاد؟",
        "answer": "شیرین",
    },
]

# اطلاعات هر بازیکن
players = {}


def new_player():
    return {
        "coins": 15,
        "current_question": 0,
        "hints_used": [0] * 8,
        "answered": [False] * 8,
        "skipped": [False] * 8,
        "question_message_id": None,
    }


def get_player(user_id):
    if user_id not in players:
        players[user_id] = new_player()
    return players[user_id]


# =========================
# متن‌ها
# =========================

START_TEXT = """عیال خوشگل من،
تولدت مبارک باشه💕
آماده‌ای کادوی تولدتو بگیری؟
اگه آماده‌ای، دکمه‌ی زیر رو فشار بده."""

RULES_TEXT = """قبل از گرفتن کادوی اصلی، باید یه جدول رو کامل کنی.🧩

این جدول از **هشت‌تا سوال** تشکیل شده.
هر جواب درستی که بدی، چندتا **سکه 🪙** به کیف پولت اضافه میشه. (از اول بازی کیف پولت **پونزده‌تا سکه** اعتبار داره.)

این سکه‌ها به چه دردی میخورن👀؟ میتونی باهاشون **هینت** بخری.

اینطوری که با خرج کردن **پنج‌تا سکه** میتونی حرف اول یه جواب رو نمایان کنی.
اما حواست باشه، اگه پنج‌تا سکه بدی و حرف اول رو نمایان کنی، برای دوباره هینت گرفتن و نمایان کردن حرف دوم باید **هشت سکه** بپردازی.

تعداد سکه‌هایی که از جواب دادن سوال‌ها میگیری هم به تعداد هینت‌هایی که استفاده کردی بستگی داره!✨

اگه **هیچ هینتی** استفاده نکرده باشی ← **چهار سکه** جایزه‌ته! 🪙
اگه **یدونه از حروف** رو با هینت باز کرده باشی ← **سه سکه** جایزه‌ته! 🪙
اگه **دوتا از حروف** رو با هینت باز کرده باشی ← **دوتا سکه** جایزه‌ته! 🪙

‼️اماااا‼️

اگه سوالی رو رد کنی و جوابشو ندونی، **ده تا سکه** به عنوان جریمه از کیف پولت کم میشه.
پس رد کردن سوال خیلی هم به نفعت نیست...

در نهایت، **تعداد سکه‌های باقی مونده جایزه‌ی اضافه‌ای برات دارن!** 🪙"""


# =========================
# /start
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    players[user_id] = new_player()

    keyboard = [
        [InlineKeyboardButton("آماده‌ام!", callback_data="ready")]
    ]

    await update.message.reply_text(
        START_TEXT,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# =========================
# شروع مأموریت
# =========================

async def ready(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("شروع مأموریت 🧩", callback_data="start_mission")]
    ]

    await query.message.reply_text(
        RULES_TEXT,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


# =========================
# نمایش سؤال
# =========================

async def show_question(update, context, user_id):
    player = get_player(user_id)
    index = player["current_question"]
    q = QUESTIONS[index]

    hidden = "_" * len(q["answer"])

    text = f"""🧩 **سؤال {index + 1} از ۸**

{q["question"]}

**جوابت رو روی این پیام ریپلای کن!**

{hidden}

🪙 **کیف پول: {player["coins"]} سکه**"""

    keyboard = [
        [
            InlineKeyboardButton("هینت 🪙", callback_data=f"hint:{index}"),
            InlineKeyboardButton("رد کردن ⏭️", callback_data=f"skip:{index}"),
        ]
    ]

    message = await context.bot.send_message(
        chat_id=user_id,
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )

    player["question_message_id"] = message.message_id


async def start_mission(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    player = get_player(user_id)

    player["current_question"] = 0

    await query.message.reply_text("مأموریت شروع شد! 🫡🫚")

    await show_question(update, context, user_id)


# =========================
# هینت
# =========================

async def hint_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    player = get_player(user_id)

    index = int(query.data.split(":")[1])

    # اگر سؤال فعلی نیست
    if index != player["current_question"]:
        await query.answer("این سؤال دیگه فعال نیست! 👀", show_alert=True)
        return

    used = player["hints_used"][index]

    if used >= 2:
        await query.message.reply_text(
            "اوپس، تو همه‌ی هینت‌هات رو استفاده کردی! "
            "دیگه برای این سوال نمیتونی هینتی بخری."
        )
        return

    cost = 5 if used == 0 else 8

    keyboard = [
        [
            InlineKeyboardButton("بله", callback_data=f"buy_hint:{index}"),
            InlineKeyboardButton("خیر", callback_data="cancel_hint"),
        ]
    ]

    await query.message.reply_text(
        f"برای هینت باید **{cost} سکه** پرداخت کنی.\n\n"
        "از خرید هینت مطمئنی؟",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


async def buy_hint(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    player = get_player(user_id)

    index = int(query.data.split(":")[1])
    used = player["hints_used"][index]

    cost = 5 if used == 0 else 8

    if player["coins"] < cost:
        await query.message.reply_text(
            "اوپس! 🥲\n"
            f"برای این هینت {cost} سکه لازم داری، "
            f"ولی فقط {player['coins']} سکه توی کیف پولته."
        )
        return

    player["coins"] -= cost
    player["hints_used"][index] += 1

    answer = QUESTIONS[index]["answer"]
    shown = answer[:player["hints_used"][index]]

    hidden = shown + "_" * (len(answer) - len(shown))

    await query.message.reply_text(
        f"✨ هینتت آماده‌ست!\n\n"
        f"**{hidden}**\n\n"
        f"🪙 کیف پول: **{player['coins']} سکه**",
        parse_mode="Markdown",
    )


async def cancel_hint(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.message.reply_text("باشه، هینت نمی‌خریم 👀")


# =========================
# رد کردن
# =========================

async def skip_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    player = get_player(user_id)

    index = int(query.data.split(":")[1])

    if index != player["current_question"]:
        await query.answer("این سؤال دیگه فعال نیست! 👀", show_alert=True)
        return

    keyboard = [
        [
            InlineKeyboardButton("بله", callback_data=f"confirm_skip:{index}"),
            InlineKeyboardButton("خیر", callback_data="cancel_skip"),
        ]
    ]

    await query.message.reply_text(
        "مطمئنی می‌خوای این سوال رو رد کنی؟\n"
        "با رد کردن این سوال، ۱۰ سکه از کیف پولت کم میشه.",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def confirm_skip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    player = get_player(user_id)

    index = int(query.data.split(":")[1])

    player["coins"] -= 10
    player["skipped"][index] = True

    answer = QUESTIONS[index]["answer"]

    await query.message.reply_text(
        f"⏭️ سوال رد شد.\n\n"
        f"جواب درست: **{answer}**\n\n"
        f"🪙 کیف پول: **{player['coins']} سکه**",
        parse_mode="Markdown",
    )

    await next_question(user_id, context)


async def cancel_skip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.message.reply_text("باشه، پس این سوال رو نگه می‌داریم! 👀")


# =========================
# بررسی جواب
# =========================

def normalize(text):
    text = text.strip().lower()
    text = text.replace("ي", "ی")
    text = text.replace("ك", "ک")
    return re.sub(r"\s+", "", text)


async def check_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return

    user_id = update.effective_user.id
    player = get_player(user_id)

    current = player["current_question"]
    question_message_id = player["question_message_id"]

    # فقط ریپلای به سؤال فعلی قبول می‌شود
    if update.message.reply_to_message.message_id != question_message_id:
        return

    correct_answer = QUESTIONS[current]["answer"]

    if normalize(update.message.text) != normalize(correct_answer):
        await update.message.reply_text("❌ جواب درست نیست! دوباره تلاش کن.")
        return

    # اگر قبلاً جواب داده شده
    if player["answered"][current]:
        return

    player["answered"][current] = True

    hints = player["hints_used"][current]

    if hints == 0:
        reward = 4
    elif hints == 1:
        reward = 3
    else:
        reward = 2

    player["coins"] += reward

    await update.message.reply_text(
        f"🎉 هورااا جوابت درست بود!\n\n"
        f"+{reward} 🪙\n\n"
        f"کیف پولت: {player['coins']} 🪙\n\n"
        f"بریم سراغ سؤال بعدی؟ 👀",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("سؤال بعدی", callback_data="next_question")]]
        ),
    )


# =========================
# سؤال بعدی
# =========================

async def next_question_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    await next_question(user_id, context)


async def next_question(user_id, context):
    player = get_player(user_id)

    player["current_question"] += 1

    if player["current_question"] >= len(QUESTIONS):
        await finish_questions(user_id, context)
        return

    await show_question(None, context, user_id)


# =========================
# پایان ۸ سؤال
# =========================

async def finish_questions(user_id, context):
    player = get_player(user_id)

    no_hint = 0
    one_hint = 0
    two_hint = 0
    skipped = 0

    for i in range(8):
        if player["skipped"][i]:
            skipped += 1
        elif player["answered"][i]:
            if player["hints_used"][i] == 0:
                no_hint += 1
            elif player["hints_used"][i] == 1:
                one_hint += 1
            else:
                two_hint += 1

    text = f"""آفرین خوشگلم، هشت‌تا سوال تموم شدن!🍭

🔸تعداد سوالاتی که بدون هینت جواب دادی: {no_hint}
🔸تعداد سوالاتی که با استفاده از یک هینت جواب دادی: {one_hint}
🔸تعداد سوالاتی که با استفاده از دو هینت جواب دادی: {two_hint}
🔸تعداد سوالاتی که ردشون کردی: {skipped}
🪙موجودی فعلی کیف پولت: {player["coins"]} سکه

هر موقع آماده بودی روی دکمه‌ی زیر بزن تا جدول با استفاده از جوابات پر بشه و بتونی کلمه‌ی مخفی شده رو پیدا کنی❗"""

    keyboard = [
        [InlineKeyboardButton("دیدن جدول", callback_data="show_table")]
    ]

    await context.bot.send_message(
        chat_id=user_id,
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# =========================
# جدول - فعلاً جای خالی
# =========================

async def show_table(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
        "🧩 جدول اینجا قرار می‌گیره!\n\n"
        "عکس جدول رو بعداً اضافه می‌کنیم. 👀"
    )


# =========================
# اجرای بات
# =========================

def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN is not set!")

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))

    application.add_handler(
        CallbackQueryHandler(ready, pattern="^ready$")
    )

    application.add_handler(
        CallbackQueryHandler(start_mission, pattern="^start_mission$")
    )

    application.add_handler(
        CallbackQueryHandler(hint_button, pattern="^hint:")
    )

    application.add_handler(
        CallbackQueryHandler(buy_hint, pattern="^buy_hint:")
    )

    application.add_handler(
        CallbackQueryHandler(cancel_hint, pattern="^cancel_hint$")
    )

    application.add_handler(
        CallbackQueryHandler(skip_button, pattern="^skip:")
    )

    application.add_handler(
        CallbackQueryHandler(confirm_skip, pattern="^confirm_skip:")
    )

    application.add_handler(
        CallbackQueryHandler(cancel_skip, pattern="^cancel_skip$")
    )

    application.add_handler(
        CallbackQueryHandler(next_question_button, pattern="^next_question$")
    )

    application.add_handler(
        CallbackQueryHandler(show_table, pattern="^show_table$")
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            check_answer
        )
    )

    print("The Ginger Mission is running!")

    application.run_polling()


if __name__ == "__main__":
    main()
