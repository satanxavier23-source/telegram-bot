import os
import telebot
from telebot import types

BOT_TOKEN = os.getenv("BOT_TOKEN") or "YOUR_BOT_TOKEN"

bot = telebot.TeleBot(BOT_TOKEN)

SOURCE_CHANNEL = -1003590340901
TARGET_CHANNEL = -1003932803968

ADMIN_IDS = [6630347046, 7194569468]

CAPTION_TEXT = "കിന്നാരത്തുമ്പികൾ പ്രീമിയം ❤️📈🔥"
caption_enabled = True


def is_admin(uid):
    return uid in ADMIN_IDS


def keyboard():
    k = types.ReplyKeyboardMarkup(resize_keyboard=True)
    k.row("🟢 Caption ON", "🔴 Caption OFF")
    k.row("📊 Status")
    return k


@bot.message_handler(commands=['start'])
def start(m):
    if not is_admin(m.from_user.id):
        return

    bot.reply_to(m, "Bot Ready ✅", reply_markup=keyboard())


@bot.message_handler(func=lambda m: is_admin(m.from_user.id) and m.text == "🟢 Caption ON")
def on(m):
    global caption_enabled
    caption_enabled = True
    bot.reply_to(m, "Caption ON ✅")


@bot.message_handler(func=lambda m: is_admin(m.from_user.id) and m.text == "🔴 Caption OFF")
def off(m):
    global caption_enabled
    caption_enabled = False
    bot.reply_to(m, "Caption OFF ❌")


@bot.message_handler(func=lambda m: is_admin(m.from_user.id) and m.text == "📊 Status")
def st(m):
    bot.reply_to(
        m,
        f"Caption: {'ON' if caption_enabled else 'OFF'}"
    )


@bot.channel_post_handler(func=lambda m: True)
def auto_forward(message):
    try:
        if message.chat.id != SOURCE_CHANNEL:
            return

        # TEXT POST = normal forward
        if message.content_type == "text":
            bot.forward_message(
                TARGET_CHANNEL,
                SOURCE_CHANNEL,
                message.message_id
            )

        # ALL MEDIA
        else:
            bot.forward_message(
                TARGET_CHANNEL,
                SOURCE_CHANNEL,
                message.message_id
            )

            if caption_enabled:
                bot.send_message(
                    TARGET_CHANNEL,
                    CAPTION_TEXT
                )

        print("Success ✅")

    except Exception as e:
        print("Error:", e)


print("Bot Running ✅")
bot.infinity_polling(skip_pending=True)
