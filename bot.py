import os
import telebot
from telebot import types

BOT_TOKEN = os.getenv("BOT_TOKEN") or "YOUR_BOT_TOKEN"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# =========================
# CHANNEL SETTINGS
# =========================
SOURCE_CHANNEL = 1003590340901
TARGET_CHANNEL = -1003932803968

# =========================
# ADMIN
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
    markup.row("📊 Status")
    return markup


def get_caption():
    if caption_enabled:
        return CAPTION_TEXT
    return None


# =========================
# START
# =========================
@bot.message_handler(commands=['start'])
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
    txt = "ON ✅" if caption_enabled else "OFF ❌"
    bot.reply_to(message, f"Caption Status: {txt}")


# =========================
# AUTO FORWARD
# =========================
@bot.channel_post_handler(func=lambda m: True)
def auto_forward(message):
    try:
        if message.chat.id != SOURCE_CHANNEL:
            return

        cap = get_caption()

        # TEXT
        if message.content_type == "text":
            if cap:
                bot.send_message(TARGET_CHANNEL, cap)

        # PHOTO
        elif message.content_type == "photo":
            bot.send_photo(
                TARGET_CHANNEL,
                message.photo[-1].file_id,
                caption=cap
            )

        # VIDEO
        elif message.content_type == "video":
            bot.send_video(
                TARGET_CHANNEL,
                message.video.file_id,
                caption=cap,
                supports_streaming=True
            )

        # DOCUMENT
        elif message.content_type == "document":
            bot.send_document(
                TARGET_CHANNEL,
                message.document.file_id,
                caption=cap
            )

        # AUDIO
        elif message.content_type == "audio":
            bot.send_audio(
                TARGET_CHANNEL,
                message.audio.file_id,
                caption=cap
            )

        # GIF
        elif message.content_type == "animation":
            bot.send_animation(
                TARGET_CHANNEL,
                message.animation.file_id,
                caption=cap
            )

        # STICKER
        elif message.content_type == "sticker":
            bot.send_sticker(
                TARGET_CHANNEL,
                message.sticker.file_id
            )

        # VOICE
        elif message.content_type == "voice":
            bot.send_voice(
                TARGET_CHANNEL,
                message.voice.file_id
            )

        # VIDEO NOTE
        elif message.content_type == "video_note":
            bot.send_video_note(
                TARGET_CHANNEL,
                message.video_note.file_id
            )

        else:
            bot.forward_message(
                TARGET_CHANNEL,
                SOURCE_CHANNEL,
                message.message_id
            )

        print("Forward success ✅")

    except Exception as e:
        print("Error:", e)


print("Bot Running ✅")
bot.infinity_polling(skip_pending=True)
