import os
import telebot
from telebot.apihelper import ApiTelegramException

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN missing")

if ":" not in BOT_TOKEN:
    raise ValueError("Token must contain a colon")

bot = telebot.TeleBot(BOT_TOKEN)

SOURCE_CHAT_ID = -1003590340901
TARGET_CHAT_ID = -1003932803968


def clean_caption(text: str):
    if not text:
        return None

    lines = [x.strip() for x in text.splitlines() if x.strip()]

    for line in lines:
        low = line.lower()
        if "video call" in low:
            return line

    return None


@bot.message_handler(commands=["start"])
def start_cmd(message):
    bot.reply_to(message, "Bot running ✅")


@bot.channel_post_handler(content_types=[
    "text",
    "photo",
    "video",
    "document",
    "animation",
    "audio",
    "voice"
])
def handle_channel_post(message):
    try:
        if message.chat.id != SOURCE_CHAT_ID:
            return

        original_text = message.caption or message.text or ""
        new_caption = clean_caption(original_text)

        if message.photo:
            bot.send_photo(
                TARGET_CHAT_ID,
                message.photo[-1].file_id,
                caption=new_caption
            )
            print("✅ Photo sent")

        elif message.video:
            bot.send_video(
                TARGET_CHAT_ID,
                message.video.file_id,
                caption=new_caption
            )
            print("✅ Video sent")

        elif message.document:
            bot.send_document(
                TARGET_CHAT_ID,
                message.document.file_id,
                caption=new_caption
            )
            print("✅ Document sent")

        elif message.animation:
            bot.send_animation(
                TARGET_CHAT_ID,
                message.animation.file_id,
                caption=new_caption
            )
            print("✅ Animation sent")

        elif message.audio:
            bot.send_audio(
                TARGET_CHAT_ID,
                message.audio.file_id,
                caption=new_caption
            )
            print("✅ Audio sent")

        elif message.voice:
            bot.send_voice(
                TARGET_CHAT_ID,
                message.voice.file_id,
                caption=new_caption
            )
            print("✅ Voice sent")

        elif message.text:
            if new_caption:
                bot.send_message(TARGET_CHAT_ID, new_caption)
                print("✅ Text sent")

    except ApiTelegramException as e:
        print("❌ Telegram API Error:", e)
    except Exception as e:
        print("❌ General Error:", e)


print("🔥 Bot is running...")
bot.infinity_polling(skip_pending=True, timeout=30, long_polling_timeout=30)
