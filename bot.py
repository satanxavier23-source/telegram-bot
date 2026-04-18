import os
import telebot
from telebot.apihelper import ApiTelegramException

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN missing")

if ":" not in BOT_TOKEN:
    raise ValueError("Token must contain a colon")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# =========================
# SETTINGS
# =========================

# ഇവിടെ source chat/channel id ഇടൂ
SOURCE_CHAT_ID = -1003590340901

# ഇവിടെ target chat/channel id ഇടൂ
TARGET_CHAT_ID = -1003932803968

# True ആണെങ്കിൽ copy_message ഉപയോഗിക്കും (forward tag കാണിക്കില്ല)
USE_COPY_MODE = True

# admins only commands
ADMIN_IDS = [6630347046, 7194569468]

# bot ON/OFF
bot_enabled = True


# =========================
# HELPERS
# =========================

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


def chat_allowed(chat_id: int) -> bool:
    return chat_id == SOURCE_CHAT_ID


# =========================
# COMMANDS
# =========================

@bot.message_handler(commands=["start"])
def start_cmd(message):
    bot.reply_to(
        message,
        "🤖 <b>Auto Forward Bot Running</b>\n\n"
        "Source chatയിൽ വരുന്ന messages target chatിലേക്ക് auto copy ചെയ്യും ✅"
    )


@bot.message_handler(commands=["id"])
def get_chat_id(message):
    bot.reply_to(message, f"🆔 Chat ID: <code>{message.chat.id}</code>")


@bot.message_handler(commands=["on"])
def turn_on(message):
    global bot_enabled
    if not is_admin(message.from_user.id):
        return
    bot_enabled = True
    bot.reply_to(message, "🟢 Bot ON")


@bot.message_handler(commands=["off"])
def turn_off(message):
    global bot_enabled
    if not is_admin(message.from_user.id):
        return
    bot_enabled = False
    bot.reply_to(message, "🔴 Bot OFF")


@bot.message_handler(commands=["status"])
def status_cmd(message):
    status = "ON 🟢" if bot_enabled else "OFF 🔴"
    bot.reply_to(
        message,
        f"🤖 Status: <b>{status}</b>\n"
        f"Source: <code>{SOURCE_CHAT_ID}</code>\n"
        f"Target: <code>{TARGET_CHAT_ID}</code>\n"
        f"Mode: <b>{'COPY' if USE_COPY_MODE else 'FORWARD'}</b>"
    )


# =========================
# AUTO FORWARD / COPY
# =========================

@bot.message_handler(
    func=lambda m: True,
    content_types=[
        "text",
        "photo",
        "video",
        "document",
        "audio",
        "voice",
        "sticker",
        "animation",
        "video_note",
        "contact",
        "location",
        "venue",
        "poll",
        "dice"
    ]
)
def handle_all(message):
    global bot_enabled

    if not bot_enabled:
        return

    if not chat_allowed(message.chat.id):
        return

    try:
        if USE_COPY_MODE:
            bot.copy_message(
                chat_id=TARGET_CHAT_ID,
                from_chat_id=message.chat.id,
                message_id=message.message_id
            )
            print(f"✅ Copied message {message.message_id}")
        else:
            bot.forward_message(
                chat_id=TARGET_CHAT_ID,
                from_chat_id=message.chat.id,
                message_id=message.message_id
            )
            print(f"✅ Forwarded message {message.message_id}")

    except ApiTelegramException as e:
        print("❌ Telegram API Error:", e)
    except Exception as e:
        print("❌ General Error:", e)


# =========================
# RUN
# =========================

print("🔥 Bot is running...")
bot.infinity_polling(skip_pending=True, timeout=30, long_polling_timeout=30)
