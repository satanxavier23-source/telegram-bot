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


def get_caption():
    return CAPTION_TEXT if caption_enabled else None


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
        f"SOURCE_CHANNEL: {SOURCE_CHANNEL}\n"
        f"TARGET_CHANNEL: {TARGET_CHANNEL}\n"
        f"Caption: {'ON ✅' if caption_enabled else 'OFF ❌'}"
    )


@bot.message_handler(func=lambda m: is_admin(m.from_user.id) and m.text == "🧪 Test Target")
def test_target(message):
    try:
        bot.send_message(TARGET_CHANNEL, "Test message ✅")
        bot.reply_to(message, "Target channelilekku test message poyi ✅")
    except Exception as e:
        bot.reply_to(message, f"Target send failed ❌\n{e}")
        print("TARGET ERROR:", e)


@bot.channel_post_handler(func=lambda m: True)
def auto_forward(message):
    try:
        print("CHANNEL POST RECEIVED ✅")
        print("CHAT ID:", message.chat.id)
        print("CONTENT TYPE:", message.content_type)

        if message.chat.id != SOURCE_CHANNEL:
            print("Wrong source, ignored")
            return

        cap = get_caption()

        if message.content_type == "text":
            send_text = cap if cap else message.text
            if send_text:
                bot.send_message(TARGET_CHANNEL, send_text)

        elif message.content_type == "photo":
            bot.send_photo(
                TARGET_CHANNEL,
                message.photo[-1].file_id,
                caption=cap
            )

        elif message.content_type == "video":
            bot.send_video(
                TARGET_CHANNEL,
                message.video.file_id,
                caption=cap,
                supports_streaming=True
            )

        elif message.content_type == "document":
            bot.send_document(
                TARGET_CHANNEL,
                message.document.file_id,
                caption=cap
            )

        elif message.content_type == "audio":
            bot.send_audio(
                TARGET_CHANNEL,
                message.audio.file_id,
                caption=cap
            )

        elif message.content_type == "animation":
            bot.send_animation(
                TARGET_CHANNEL,
                message.animation.file_id,
                caption=cap
            )

        elif message.content_type == "voice":
            bot.send_voice(TARGET_CHANNEL, message.voice.file_id)

        elif message.content_type == "sticker":
            bot.send_sticker(TARGET_CHANNEL, message.sticker.file_id)

        elif message.content_type == "video_note":
            bot.send_video_note(TARGET_CHANNEL, message.video_note.file_id)

        else:
            bot.forward_message(TARGET_CHANNEL, SOURCE_CHANNEL, message.message_id)

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
