import telebot
import yt_dlp
import os
import time
import threading
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(
        message,
        "Multi Downloader Bot 🤖\n\n"
        "Send:\n"
        "Instagram link 📷\n"
        "YouTube link 🎥\n"
        "TeraBox link 📂"
    )


def download_video(url, chat_id):

    status = bot.send_message(chat_id, "⬇️ Downloading...")

    unique = str(time.time()).replace(".", "")

    def progress_hook(d):
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%')
            try:
                bot.edit_message_text(
                    f"⬇️ Downloading {percent}",
                    chat_id,
                    status.message_id
                )
            except:
                pass

    ydl_opts = {
        'outtmpl': f'download_{unique}_%(title)s.%(ext)s',
        'format': 'best[ext=mp4]/best',
        'quiet': True,
        'progress_hooks': [progress_hook],
        'cookiefile': 'cookies.txt',
        'nocheckcertificate': True,
        'geo_bypass': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        bot.edit_message_text("⬆️ Uploading...", chat_id, status.message_id)

        for file in os.listdir():
            if file.startswith(f"download_{unique}"):

                with open(file, 'rb') as f:

                    if file.endswith(".mp4"):
                        bot.send_video(chat_id, f)
                    elif file.endswith(".jpg"):
                        bot.send_photo(chat_id, f)
                    else:
                        bot.send_document(chat_id, f)

                os.remove(file)

        bot.delete_message(chat_id, status.message_id)

    except:
        bot.send_message(chat_id, "❌ Download failed")


# 🔥 TeraBox simple downloader
def terabox_download(url, chat_id):

    msg = bot.send_message(chat_id, "🔗 Fetching TeraBox file...")

    try:
        api = f"https://terabox-api.vercel.app/api?url={url}"
        res = requests.get(api).json()

        if res["status"]:

            download_link = res["download"]

            bot.edit_message_text(
                "⬇️ Downloading TeraBox...",
                chat_id,
                msg.message_id
            )

            file = requests.get(download_link)

            filename = f"terabox_{time.time()}.mp4"

            with open(filename, "wb") as f:
                f.write(file.content)

            bot.send_video(chat_id, open(filename, "rb"))

            os.remove(filename)

            bot.delete_message(chat_id, msg.message_id)

        else:
            bot.send_message(chat_id, "❌ TeraBox link error")

    except:
        bot.send_message(chat_id, "❌ TeraBox failed")


@bot.message_handler(func=lambda message: True)
def main(message):

    url = message.text

    if "instagram.com" in url or "youtube.com" in url or "youtu.be" in url:

        threading.Thread(
            target=download_video,
            args=(url, message.chat.id)
        ).start()

    elif "terabox" in url or "1024tera" in url:

        threading.Thread(
            target=terabox_download,
            args=(url, message.chat.id)
        ).start()

    else:
        bot.reply_to(message, "❌ Send valid link")


print("Bot running...")
bot.infinity_polling()
