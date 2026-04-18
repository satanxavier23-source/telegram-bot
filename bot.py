import os
import telebot
from telebot.apihelper import ApiTelegramException

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN missing")

if ":" not in BOT_TOKEN:
    raise ValueError("Token must contain a colon")

bot = telebot.TeleBot(BOT_TOKEN)

# =========================
# YOUR CHANNEL IDS
# =========================
SOURCE_CHAT_ID = -1003590340901
TARGET_CHAT_ID = -1003932803968

USE_COPY_MODE = True


def send_to_target(from_chat_id, message_id):
    if USE_COPY_MODE:
        bot.copy_message(
            chat_id=TARGET_CHAT_ID,
            from_chat_id=from_chat_id,
            message_id=message_id
        )
    else:
        bot.forward_message(
            chat_id=TARGET_CHAT_ID,
            from_chat_id=from_chat_id,
            message_id=message_id
        )


@bot.message_handler(commands=["start"])
def start_cmd(message):
    bot.reply_to(
        message,
        "Bot running ✅\n"
        f"Source: {SOURCE_CHAT_ID}\n"
        f"Target: {TARGET_CHAT_ID}"
    )


@bot.message_handler(commands=["id"])
def id_cmd(message):
    bot.reply_to(message, f"Chat ID: {message.chat.id}")


@bot.channel_post_handler(content_types=[
    "text",
    "photo",
    "video",
    "document",
    "audio",
    "voice",
    "sticker",
    "animation",
    "video_note"
])
def handle_channel_post(message):
    try:
        print(f"CHANNEL POST RECEIVED | chat={message.chat.id} | msg={message.message_id} | type={message.content_type}")

        if message.chat.id != SOURCE_CHAT_ID:
            print("⏩ Not source channel, skipped")
            return

        send_to_target(message.chat.id, message.message_id)
        print(f"✅ Sent successfully to target | msg={message.message_id}")

    except ApiTelegramException as e:
        print("❌ Telegram API Error:", e)
    except Exception as e:
        print("❌ General Error:", e)


print("🔥 Bot is running...")
bot.infinity_polling(skip_pending=True, timeout=30, long_polling_timeout=30)
