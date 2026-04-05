import telebot
import yt_dlp
import os
import time
import threading

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    print("BOT_TOKEN missing")
    exit()

bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(
        message,
        "Send Instagram Reel/Post link 📥\nBot will download and send video 🎬"
    )


def download_video(url, chat_id):
    status_msg = bot.send_message(chat_id, "⬇️ Downloading...")

    # 🔥 unique filename
    unique_id = str(time.time()).replace(".", "")
    filename = f"video_{unique_id}.mp4"

    def progress_hook(d):
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%')
            try:
                bot.edit_message_text(
                    f"⬇️ Downloading {percent}",
                    chat_id,
                    status_msg.message_id
                )
            except:
                pass

    ydl_opts = {
        'outtmpl': f'video_{unique_id}.%(ext)s',
        'format': 'best',
        'progress_hooks': [progress_hook],
        'quiet': True,
        'cookiefile': 'cookies.txt'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        file_name = None
        for file in os.listdir():
            if file.startswith(f"video_{unique_id}"):
                file_name = file
                break

        if file_name:
            bot.edit_message_text("⬆️ Uploading...", chat_id, status_msg.message_id)

            with open(file_name, 'rb') as video:
                bot.send_video(chat_id, video)

            os.remove(file_name)
            bot.delete_message(chat_id, status_msg.message_id)

        else:
            bot.send_message(chat_id, "❌ Download failed")

    except Exception as e:
        bot.send_message(chat_id, "❌ Instagram blocked / Login required")


@bot.message_handler(func=lambda message: True)
def downloader(message):
    url = message.text

    if "instagram.com" in url:
        # 🔥 threading for multiple users
        threading.Thread(
            target=download_video,
            args=(url, message.chat.id)
        ).start()
    else:
        bot.reply_to(message, "❌ Send valid Instagram link")


print("Bot running...")
bot.infinity_polling()
