import os
import asyncio

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)


# =========================================================
# TOKEN
# =========================================================

BOT_TOKEN = os.getenv("BOT_TOKEN")


# =========================================================
# QUESTIONS
# =========================================================

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


# =========================================================
# PLAYER DATA
# =========================================================

players = {}
player_locks = {}


def get_lock(user_id):
    if user_id not in player_locks:
        player_locks[user_id] = asyncio.Lock()

    return player_locks[user_id]


def new_player():
    return {
        "coins": 15,
        "current_question": 0,

        "hints_used": [0] * 8,
        "answered": [False] * 8,
        "skipped": [False] * 8,

        "question_message_id": None,

        "stats": {
            "no_hint": 0,
            "one_hint": 0,
            "two_hints": 0,
            "skipped": 0,
        },

        "finished": False,
    }


# =========================================================
# ANSWER NORMALIZATION
# =========================================================

def normalize(text):
    return " ".join(text.strip().lower().split())


def is_correct(user_answer, correct_answer):
    return normalize(user_answer) == normalize(correct_answer)


# =========================================================
# START
# =========================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    players[user_id] = new_player()

    keyboard = [
        [
            InlineKeyboardButton(
                "آماده‌ام!",
                callback_data="ready"
            )
        ]
    ]

    await update.message.reply_text(
        "عیال خوشگل من،\n"
        "تولدت مبارک باشه💕\n"
        "آماده‌ای کادوی تولدتو بگیری؟\n"
        "اگه آماده‌ای، دکمه‌ی زیر رو فشار بده.",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# =========================================================
# READY
# =========================================================

async def ready(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    text = (
        "قبل از گرفتن کادوی اصلی، باید یه جدول رو کامل کنی.🧩\n\n"

        "این جدول از **هشت‌تا سوال** تشکیل شده.\n"
        "هر جواب درستی که بدی، چندتا **سکه 🪙** به کیف پولت اضافه میشه. "
        "(از اول بازی کیف پولت **پونزده‌تا سکه** اعتبار داره.)\n\n"

        "این سکه‌ها به چه دردی میخورن👀؟ "
        "میتونی باهاشون **راهنمایی** بخری.\n\n"

        "اینطوری که با خرج کردن **پنج‌تا سکه** "
        "میتونی حرف اول یه جواب رو نمایان کنی.\n"
        "اما حواست باشه، اگه پنج‌تا سکه بدی و حرف اول رو نمایان کنی، "
        "برای دوباره راهنمایی گرفتن و نمایان کردن حرف دوم "
        "باید **هشت سکه** بپردازی.\n\n"

        "تعداد سکه‌هایی که از جواب دادن سوال‌ها میگیری هم "
        "به تعداد راهنمایی‌هایی که استفاده کردی بستگی داره!✨\n\n"

        "اگه **هیچ راهنمایی** استفاده نکرده باشی "
        "← **چهار سکه** جایزه‌ته! 🪙\n"

        "اگه **یدونه از حروف** رو با راهنمایی باز کرده باشی "
        "← **سه سکه** جایزه‌ته! 🪙\n"

        "اگه **دوتا از حروف** رو با راهنمایی باز کرده باشی "
        "← **دوتا سکه** جایزه‌ته! 🪙\n\n"

        "‼️اماااا‼️\n\n"

        "اگه سوالی رو رد کنی و جوابشو ندونی، "
        "**ده تا سکه** به عنوان جریمه از کیف پولت کم میشه.\n"
        "پس رد کردن سوال خیلی هم به نفعت نیست...\n\n"

        "در نهایت، **تعداد سکه‌های باقی مونده جایزه‌ی اضافه‌ای برات دارن!** 🪙"
    )

    keyboard = [
        [
            InlineKeyboardButton(
                "شروع مأموریت 🧩",
                callback_data="start_mission"
            )
        ]
    ]

    await query.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# =========================================================
# START MISSION
# =========================================================

async def start_mission(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    user_id = query.from_user.id

    async with get_lock(user_id):

        await query.answer()

        players[user_id] = new_player()

        await query.message.reply_text(
            "**مأموریت شروع شد!** 🫡🫚",
            parse_mode="Markdown",
        )

        await show_question(context, user_id)


# =========================================================
# SHOW QUESTION
# =========================================================

async def show_question(
    context: ContextTypes.DEFAULT_TYPE,
    user_id: int
):

    player = players.get(user_id)

    if not player:
        return

    index = player["current_question"]

    if index >= len(QUESTIONS):
        await finish_questions(context, user_id)
        return

    question = QUESTIONS[index]

    text = (
        f"🧩 **سوال {index + 1} از ۸**\n\n"
        f"{question['question']}\n\n"
        "جوابت رو روی این پیام ریپلای کن!\n\n"
        f"🪙 **کیف پول: {player['coins']} سکه**"
    )

    keyboard = [
        [
            InlineKeyboardButton(
                "راهنمایی 🪙",
                callback_data=f"hint:{index}"
            ),
            InlineKeyboardButton(
                "رد کردن ⏭️",
                callback_data=f"skip:{index}"
            ),
        ]
    ]

    message = await context.bot.send_message(
        chat_id=user_id,
        text=text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

    player["question_message_id"] = message.message_id


# =========================================================
# CHECK ANSWER
# =========================================================

async def check_answer(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    message = update.message
    user_id = update.effective_user.id

    player = players.get(user_id)

    if not player:
        return

    if not message.reply_to_message:
        return

    if message.reply_to_message.message_id != player["question_message_id"]:
        return

    async with get_lock(user_id):

        # دوباره state را بعد از گرفتن lock بررسی می‌کنیم
        player = players.get(user_id)

        if not player:
            return

        index = player["current_question"]

        if index >= len(QUESTIONS):
            return

        if player["answered"][index]:
            return

        if player["skipped"][index]:
            return

        correct_answer = QUESTIONS[index]["answer"]

        if not is_correct(message.text, correct_answer):

            await message.reply_text(
                "❌ جواب درست نیست! دوباره تلاش کن."
            )

            return

        # علامت‌گذاری قبل از ارسال پیام
        # تا جواب‌های تکراری نتوانند دوباره پردازش شوند.
        player["answered"][index] = True

        hints = player["hints_used"][index]

        if hints == 0:

            reward = 4
            player["stats"]["no_hint"] += 1

        elif hints == 1:

            reward = 3
            player["stats"]["one_hint"] += 1

        else:

            reward = 2
            player["stats"]["two_hints"] += 1

        player["coins"] += reward

        keyboard = [
            [
                InlineKeyboardButton(
                    "سوال بعدی",
                    callback_data=f"next:{index}"
                )
            ]
        ]

        await message.reply_text(
            f"🎉 هورااا جوابت درست بود!\n\n"
            f"+{reward} 🪙\n\n"
            f"کیف پولت: {player['coins']} 🪙\n\n"
            "بریم سراغ سؤال بعدی؟ 👀",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )


# =========================================================
# NEXT QUESTION
# =========================================================

async def next_question(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    user_id = query.from_user.id

    async with get_lock(user_id):

        player = players.get(user_id)

        if not player:

            await query.answer()
            return

        try:
            button_index = int(
                query.data.split(":")[1]
            )

        except (IndexError, ValueError):

            await query.answer()
            return

        # دکمه باید متعلق به سؤال فعلی باشد.
        if button_index != player["current_question"]:

            await query.answer(
                "این دکمه دیگه قابل استفاده نیست."
            )

            return

        # سؤال باید قبلاً درست جواب داده شده باشد.
        if not player["answered"][button_index]:

            await query.answer(
                "اول باید به این سوال جواب بدی."
            )

            return

        await query.answer()

        # فقط یک سؤال جلو می‌رویم.
        player["current_question"] += 1

        player["question_message_id"] = None

        await show_question(
            context,
            user_id
        )


# =========================================================
# HINT BUTTON
# =========================================================

async def hint_button(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    user_id = query.from_user.id

    async with get_lock(user_id):

        player = players.get(user_id)

        if not player:

            await query.answer()
            return

        try:
            index = int(
                query.data.split(":")[1]
            )

        except (IndexError, ValueError):

            await query.answer()
            return

        if index != player["current_question"]:

            await query.answer(
                "این سوال دیگه فعال نیست."
            )

            return

        used = player["hints_used"][index]

        if used >= 2:

            await query.answer()

            await query.message.reply_text(
                "اوپس، تو همه‌ی راهنمایی‌هات رو استفاده کردی! "
                "دیگه برای این سوال نمیتونی راهنمایی بخری."
            )

            return

        cost = 5 if used == 0 else 8

        keyboard = [
            [
                InlineKeyboardButton(
                    "بله",
                    callback_data=f"buy_hint:{index}"
                ),
                InlineKeyboardButton(
                    "خیر",
                    callback_data="cancel_hint"
                ),
            ]
        ]

        await query.answer()

        await query.message.reply_text(
            f"برای راهنمایی باید **{cost} سکه** پرداخت کنی. "
            "از خرید راهنمایی مطمئنی؟",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )


# =========================================================
# BUY HINT
# =========================================================

async def buy_hint(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    user_id = query.from_user.id

    async with get_lock(user_id):

        player = players.get(user_id)

        if not player:

            await query.answer()
            return

        try:
            index = int(
                query.data.split(":")[1]
            )

        except (IndexError, ValueError):

            await query.answer()
            return

        if index != player["current_question"]:

            await query.answer(
                "این سوال دیگه فعال نیست."
            )

            return

        used = player["hints_used"][index]

        if used >= 2:

            await query.answer()
            return

        cost = 5 if used == 0 else 8

        if player["coins"] < cost:

            await query.answer(
                "سکه‌هات برای این راهنمایی کافی نیست!",
                show_alert=True,
            )

            return

        player["coins"] -= cost

        player["hints_used"][index] += 1

        revealed = player["hints_used"][index]

        answer = QUESTIONS[index]["answer"]

        displayed = " ".join(
            char if i < revealed else "＿"
            for i, char in enumerate(answer)
        )

        await query.answer()

        await query.message.reply_text(
            f"🔎 **راهنمایی {revealed}:**\n\n"
            f"{displayed}\n\n"
            f"🪙 **کیف پول: {player['coins']} سکه**",
            parse_mode="Markdown",
        )


# =========================================================
# CANCEL HINT
# =========================================================

async def cancel_hint(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.callback_query.answer(
        "راهنمایی نخریدی 👀"
    )


# =========================================================
# SKIP
# =========================================================

async def skip_button(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    user_id = query.from_user.id

    async with get_lock(user_id):

        player = players.get(user_id)

        if not player:

            await query.answer()
            return

        try:
            index = int(
                query.data.split(":")[1]
            )

        except (IndexError, ValueError):

            await query.answer()
            return

        if index != player["current_question"]:

            await query.answer(
                "این سوال دیگه فعال نیست."
            )

            return

        keyboard = [
            [
                InlineKeyboardButton(
                    "بله",
                    callback_data=f"confirm_skip:{index}"
                ),
                InlineKeyboardButton(
                    "خیر",
                    callback_data="cancel_skip"
                ),
            ]
        ]

        await query.answer()

        await query.message.reply_text(
            "مطمئنی می‌خوای این سوال رو رد کنی؟\n"
            "با رد کردن این سوال، **۱۰ سکه** "
            "از کیف پولت کم میشه.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )


# =========================================================
# CONFIRM SKIP
# =========================================================

async def confirm_skip(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    user_id = query.from_user.id

    async with get_lock(user_id):

        player = players.get(user_id)

        if not player:

            await query.answer()
            return

        try:
            index = int(
                query.data.split(":")[1]
            )

        except (IndexError, ValueError):

            await query.answer()
            return

        if index != player["current_question"]:

            await query.answer(
                "این سوال دیگه فعال نیست."
            )

            return

        # جریمه
        player["coins"] -= 10

        player["skipped"][index] = True

        player["stats"]["skipped"] += 1

        correct_answer = QUESTIONS[index]["answer"]

        await query.answer()

        await query.message.reply_text(
            f"⏭️ سوال رد شد.\n\n"
            f"جواب درست: **{correct_answer}**\n\n"
            f"🪙 **کیف پول: {player['coins']} سکه**",
            parse_mode="Markdown",
        )

        player["current_question"] += 1

        player["question_message_id"] = None

        await show_question(
            context,
            user_id
        )


# =========================================================
# CANCEL SKIP
# =========================================================

async def cancel_skip(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.callback_query.answer(
        "سوال رو رد نکردی 👀"
    )


# =========================================================
# FINISH
# =========================================================

async def finish_questions(
    context: ContextTypes.DEFAULT_TYPE,
    user_id: int
):

    player = players.get(user_id)

    if not player:
        return

    # جلوگیری از ارسال دوباره‌ی پایان
    if player["finished"]:
        return

    player["finished"] = True

    stats = player["stats"]

    text = (
        "آفرین خوشگلم، هشت‌تا سوال تموم شدن!🍭\n\n"

        f"🔸**تعداد سوالاتی که بدون راهنمایی جواب دادی:** "
        f"{stats['no_hint']}\n"

        f"🔸**تعداد سوالاتی که با استفاده از یک راهنمایی جواب دادی:** "
        f"{stats['one_hint']}\n"

        f"🔸**تعداد سوالاتی که با استفاده از دو راهنمایی جواب دادی:** "
        f"{stats['two_hints']}\n"

        f"🔸**تعداد سوالاتی که ردشون کردی:** "
        f"{stats['skipped']}\n"

        f"🪙**موجودی فعلی کیف پولت:** "
        f"{player['coins']} سکه\n\n"

        "هر موقع آماده بودی روی دکمه‌ی زیر بزن تا جدول "
        "با استفاده از جوابات پر بشه و بتونی "
        "کلمه‌ی مخفی شده رو پیدا کنی❗"
    )

    keyboard = [
        [
            InlineKeyboardButton(
                "دیدن جدول",
                callback_data="show_table"
            )
        ]
    ]

    await context.bot.send_message(
        chat_id=user_id,
        text=text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# =========================================================
# TABLE
# فعلاً جای تصویر جدول
# =========================================================

async def show_table(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    await query.message.reply_text(
        "🧩 جدول رو بعداً با تصویر نهایی اضافه می‌کنیم."
    )


# =========================================================
# MAIN
# =========================================================

def main():

    if not BOT_TOKEN:
        raise RuntimeError(
            "BOT_TOKEN is not set."
        )

    application = (
        Application
        .builder()
        .token(BOT_TOKEN)
        .build()
    )

    application.add_handler(
        CommandHandler("start", start)
    )

    application.add_handler(
        CallbackQueryHandler(
            ready,
            pattern=r"^ready$"
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            start_mission,
            pattern=r"^start_mission$"
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            hint_button,
            pattern=r"^hint:\d+$"
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            buy_hint,
            pattern=r"^buy_hint:\d+$"
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            cancel_hint,
            pattern=r"^cancel_hint$"
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            skip_button,
            pattern=r"^skip:\d+$"
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            confirm_skip,
            pattern=r"^confirm_skip:\d+$"
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            cancel_skip,
            pattern=r"^cancel_skip$"
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            next_question,
            pattern=r"^next:\d+$"
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            show_table,
            pattern=r"^show_table$"
        )
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            check_answer
        )
    )

    print("The Ginger Mission is running!")

    application.run_polling()


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    main()
