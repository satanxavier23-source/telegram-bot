import telebot
import yt_dlp
import os
import time
import threading

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(
        message,
        "Instagram link ayakkuka 📥\nReel / Photo / Video / Carousel download cheyyam 🎬📷"
    )


def download_instagram(url, chat_id):
    status = bot.send_message(chat_id, "⬇️ Downloading...")

    unique = str(time.time()).replace(".", "")

    ydl_opts = {
        'outtmpl': f'download_{unique}_%(title)s.%(ext)s',
        'format': 'best',
        'quiet': True,
        'cookiefile': 'cookies.txt',
        'noplaylist': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        bot.edit_message_text("⬆️ Uploading...", chat_id, status.message_id)

        files = []

        for file in os.listdir():
            if file.startswith(f"download_{unique}"):
                files.append(file)

        caption = ""

        if 'description' in info and info['description']:
            caption = info['description'][:1000]

        for file in files:
            with open(file, 'rb') as f:
                if file.endswith(".mp4"):
                    bot.send_video(chat_id, f, caption=caption)
                else:
                    bot.send_photo(chat_id, f, caption=caption)

            os.remove(file)

        bot.delete_message(chat_id, status.message_id)

    except Exception as e:
        bot.send_message(chat_id, "❌ Instagram blocked or cookies expired")


@bot.message_handler(func=lambda message: True)
def main(message):
    url = message.text

    if "instagram.com" in url:
        threading.Thread(
            target=download_instagram,
            args=(url, message.chat.id)
        ).start()
    else:
        bot.reply_to(message, "❌ Instagram link ayakkuka")


print("Bot running...")
bot.infinity_polling()
