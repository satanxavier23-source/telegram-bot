import telebot
import yt_dlp
import os
import time
import threading
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)


# start
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(
        message,
        "Multi Downloader Bot 🤖\n\n"
        "Send:\n"
        "Instagram link 📷\n"
        "YouTube link 🎥\n"
        "TeraBox link 📂\n\n"
        "⚠️ Files auto delete after 1 hour"
    )


# auto delete
def auto_delete(chat_id, message_id):

    time.sleep(3600)

    try:
        bot.delete_message(chat_id, message_id)

        bot.send_message(
            chat_id,
            "🗑 File deleted automatically after 1 hour ⏰"
        )

    except:
        pass


# download video (instagram + youtube)
def download_video(url, chat_id):

    status = bot.send_message(chat_id, "⬇️ Downloading...")

    unique = str(int(time.time()))

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
        'geo_bypass': True,
        'no_warnings': True,
        'ignoreerrors': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0'
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)

        bot.edit_message_text("⬆️ Uploading...", chat_id, status.message_id)

        for file in os.listdir():

            if file.startswith(f"download_{unique}"):

                with open(file, 'rb') as f:

                    if file.endswith(".mp4"):

                        sent = bot.send_video(chat_id, f)

                        bot.send_message(
                            chat_id,
                            "⚠️ File will be deleted after 1 hour ⏰"
                        )

                        threading.Thread(
                            target=auto_delete,
                            args=(chat_id, sent.message_id)
                        ).start()

                    elif file.endswith(".jpg"):

                        sent = bot.send_photo(chat_id, f)

                        threading.Thread(
                            target=auto_delete,
                            args=(chat_id, sent.message_id)
                        ).start()

                    else:

                        sent = bot.send_document(chat_id, f)

                        threading.Thread(
                            target=auto_delete,
                            args=(chat_id, sent.message_id)
                        ).start()

                os.remove(file)

        bot.delete_message(chat_id, status.message_id)

    except:
        bot.send_message(chat_id, "❌ Download failed")


# TeraBox downloader
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

            filename = f"terabox_{int(time.time())}.mp4"

            with open(filename, "wb") as f:
                f.write(file.content)

            sent = bot.send_video(chat_id, open(filename, "rb"))

            bot.send_message(
                chat_id,
                "⚠️ File will be deleted after 1 hour ⏰"
            )

            threading.Thread(
                target=auto_delete,
                args=(chat_id, sent.message_id)
            ).start()

            os.remove(filename)

            bot.delete_message(chat_id, msg.message_id)

        else:
            bot.send_message(chat_id, "❌ TeraBox link error")

    except:
        bot.send_message(chat_id, "❌ TeraBox failed")


# main handler
@bot.message_handler(func=lambda message: True)
def main(message):

    url = message.text.strip()

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
        bot.reply_to(message, "❌ Send valid Instagram / YouTube / TeraBox link")


print("Bot running...")
bot.infinity_polling()
