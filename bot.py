import os
import telebot
from telebot import types

BOT_TOKEN = os.getenv("BOT_TOKEN") or "YOUR_BOT_TOKEN"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# =========================
# CHANNEL SETTINGS
# =========================
SOURCE_CHANNEL = -1003590340901
TARGET_CHANNEL = -1003932803968

# =========================
# ADMIN SETTINGS
# =========================
ADMIN_IDS = [6630347046, 7194569468]

# =========================
# CAPTION SETTINGS
# =========================
CAPTION_TEXT = "കിന്നാരത്തുമ്പികൾ പ്രീമിയം ❤️📈🔥"
caption_enabled = True


# =========================
# HELPERS
# =========================
def is_admin(user_id):
    return user_id in ADMIN_IDS


def keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🟢 Caption ON", "🔴 Caption OFF")
    markup.row("📊 Status", "🧪 Test Target")
    return markup


# =========================
# START
# =========================
@bot.message_handler(commands=["start"])
def start(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "Access denied ❌")
        return

    bot.reply_to(
        message,
        "Private Channel Auto Forward Bot Ready ✅",
        reply_markup=keyboard()
    )


# =========================
# BUTTONS
# =========================
@bot.message_handler(func=lambda m: is_admin(m.from_user.id) and m.text == "🟢 Caption ON")
def caption_on(message):
    global caption_enabled
    caption_enabled = True
    bot.reply_to(message, "Caption ON ayi ✅")


@bot.message_handler(func=lambda m: is_admin(m.from_user.id) and m.text == "🔴 Caption OFF")
def caption_off(message):
    global caption_enabled
    caption_enabled = False
    bot.reply_to(message, "Caption OFF ayi ✅")


@bot.message_handler(func=lambda m: is_admin(m.from_user.id) and m.text == "📊 Status")
def status(message):
    bot.reply_to(
        message,
        f"Source Channel: {SOURCE_CHANNEL}\n"
        f"Target Channel: {TARGET_CHANNEL}\n"
        f"Caption: {'ON ✅' if caption_enabled else 'OFF ❌'}\n"
        f"Caption Text: {CAPTION_TEXT}"
    )


@bot.message_handler(func=lambda m: is_admin(m.from_user.id) and m.text == "🧪 Test Target")
def test_target(message):
    try:
        bot.send_message(TARGET_CHANNEL, "Test message ✅")
        bot.reply_to(message, "Target channel working ✅")
    except Exception as e:
        bot.reply_to(message, f"Target failed ❌\n{e}")
        print("TARGET ERROR:", e)


# =========================
# AUTO FORWARD
# =========================
@bot.channel_post_handler(func=lambda m: True)
def auto_forward(message):
    try:
        print("POST RECEIVED ✅")
        print("CHAT ID:", message.chat.id)
        print("TYPE:", message.content_type)
        print("MESSAGE ID:", message.message_id)

        if message.chat.id != SOURCE_CHANNEL:
            print("Ignored: not source channel")
            return

        # TEXT POSTS
        if message.content_type == "text":
            if caption_enabled:
                bot.send_message(TARGET_CHANNEL, CAPTION_TEXT)
            else:
                bot.forward_message(
                    TARGET_CHANNEL,
                    SOURCE_CHANNEL,
                    message.message_id
                )

        # PHOTO / VIDEO / DOC / GIF / STICKER / MOST MEDIA
        else:
            bot.forward_message(
                TARGET_CHANNEL,
                SOURCE_CHANNEL,
                message.message_id
            )

            if caption_enabled:
                bot.send_message(TARGET_CHANNEL, CAPTION_TEXT)

        print("FORWARD SUCCESS ✅")

    except Exception as e:
        print("FORWARD ERROR ❌", e)
        for admin_id in ADMIN_IDS:
            try:
                bot.send_message(admin_id, f"Forward error ❌\n{e}")
            except:
                pass


print("Bot Running ✅")
bot.infinity_polling(
    timeout=60,
    long_polling_timeout=60,
    skip_pending=True,
    allowed_updates=["message", "channel_post"]
)
