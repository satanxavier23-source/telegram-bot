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
        "Instagram Downloader Bot 🤖\n\n"
        "Send:\n"
        "Reel 🎬\n"
        "Photo 📷\n"
        "Video 🎥\n"
        "Carousel 📂\n"
        "Story 📱\n"
        "Highlights ⭐"
    )


def download_instagram(url, chat_id):

    status_msg = bot.send_message(chat_id, "⬇️ Downloading...")

    unique_id = str(time.time()).replace(".", "")

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
        'outtmpl': f'insta_{unique_id}_%(title)s.%(ext)s',
        'format': 'best[ext=mp4]/best',
        'quiet': True,
        'noplaylist': False,
        'progress_hooks': [progress_hook],
        'cookiefile': 'cookies.txt',
        'nocheckcertificate': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        bot.edit_message_text("⬆️ Uploading...", chat_id, status_msg.message_id)

        files = []

        for file in os.listdir():
            if file.startswith(f"insta_{unique_id}"):
                files.append(file)

        caption = ""

        if info.get("description"):
            caption = info["description"][:1000]

        for file in files:

            with open(file, 'rb') as f:

                if file.endswith(".mp4"):
                    bot.send_video(chat_id, f, caption=caption)

                elif file.endswith(".jpg") or file.endswith(".png"):
                    bot.send_photo(chat_id, f, caption=caption)

                else:
                    bot.send_document(chat_id, f)

            os.remove(file)  # auto delete

        bot.delete_message(chat_id, status_msg.message_id)

    except Exception as e:
        bot.send_message(chat_id, "❌ Download failed / Cookies expired")


@bot.message_handler(func=lambda message: True)
def main(message):

    url = message.text

    if "instagram.com" in url:

        threading.Thread(
            target=download_instagram,
            args=(url, message.chat.id)
        ).start()

    else:
        bot.reply_to(message, "❌ Send Instagram link")


print("Bot running...")
bot.infinity_polling()
