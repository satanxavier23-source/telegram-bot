import os
import telebot
from telebot import types

BOT_TOKEN = os.getenv("BOT_TOKEN") or "YOUR_BOT_TOKEN"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

SOURCE_CHANNEL = -1003590340901
TARGET_CHANNEL = -1003932803968

ADMIN_IDS = [6630347046, 7194569468]

CAPTION_TEXT = "കിന്നാരത്തുമ്പികൾ പ്രീമിയം ❤️📈🔥"
caption_enabled = True


def is_admin(user_id):
    return user_id in ADMIN_IDS


def keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🟢 Caption ON", "🔴 Caption OFF")
    markup.row("📊 Status", "🧪 Test Target")
    return markup


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
        f"Source: {SOURCE_CHANNEL}\n"
        f"Target: {TARGET_CHANNEL}\n"
        f"Caption: {'ON ✅' if caption_enabled else 'OFF ❌'}"
    )


@bot.message_handler(func=lambda m: is_admin(m.from_user.id) and m.text == "🧪 Test Target")
def test_target(message):
    try:
        bot.send_message(TARGET_CHANNEL, "Target test ok ✅")
        bot.reply_to(message, "Target channel working ✅")
    except Exception as e:
        bot.reply_to(message, f"Target failed ❌\n{e}")
        print("TARGET ERROR:", e)


@bot.channel_post_handler(func=lambda m: True)
def auto_forward(message):
    try:
        print("CHANNEL POST RECEIVED ✅")
        print("CHAT ID:", message.chat.id)
        print("TYPE:", message.content_type)

        if message.chat.id != SOURCE_CHANNEL:
            print("Ignored: not source channel")
            return

        # TEXT POSTS
        if message.content_type == "text":
            if caption_enabled:
                bot.send_message(TARGET_CHANNEL, CAPTION_TEXT)
            else:
                bot.copy_message(TARGET_CHANNEL, SOURCE_CHANNEL, message.message_id)

        # MEDIA / DOCUMENT / MOST OTHER POSTS
        else:
            if caption_enabled:
                bot.copy_message(
                    TARGET_CHANNEL,
                    SOURCE_CHANNEL,
                    message.message_id,
                    caption=CAPTION_TEXT
                )
            else:
                bot.copy_message(
                    TARGET_CHANNEL,
                    SOURCE_CHANNEL,
                    message.message_id
                )

        print("FORWARD SUCCESS ✅")

    except Exception as e:
        print("FORWARD ERROR ❌", e)
        for admin_id in ADMIN_IDS:
            try:
                bot.send_message(admin_id, f"Forward error ❌\n{e}")
            except:
                pass


print("Bot Running ✅")
bot.infinity_polling(skip_pending=True, allowed_updates=["message", "channel_post"])
