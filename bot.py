import telebot
import yt_dlp
import os
import time
import threading

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)

DOWNLOAD_STICKER = "AAMCAgADGQEAARzg3WnUtNmZvyLqgBJF9b5kwpYWBhI3AAIsAAMkcWIaxSDmA-94_OQBAAdtAAM7BA"
UPLOAD_STICKER = "AAMCBQADGQEAARzg4mnUtZgSNRLAClmV-R6DvVfx8X3xAAKBCAACeAEoVKDdiyoydhyxAQAHbQADOwQ"


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(
        message,
        "📥 Instagram Downloader Bot\n\nSend Instagram link\n⏱ Auto delete after 1 hour"
    )


def auto_delete(chat_id, message_id):
    time.sleep(3600)
    try:
        bot.delete_message(chat_id, message_id)
        bot.send_message(chat_id, "🗑 File deleted after 1 hour")
    except:
        pass


def download_instagram(url, chat_id):

    # downloading sticker
    status = bot.send_sticker(chat_id, DOWNLOAD_STICKER)

    unique = str(int(time.time()))

    ydl_opts = {
        'outtmpl': f'insta_{unique}_%(title)s.%(ext)s',
        'format': 'best',
        'cookiefile': 'instagram_cookies.txt',
        'quiet': True,
        'nocheckcertificate': True,
        'geo_bypass': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0'
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)

        # uploading sticker
        bot.send_sticker(chat_id, UPLOAD_STICKER)

        files_found = False

        for file in os.listdir():

            if file.startswith(f"insta_{unique}"):

                files_found = True

                size = os.path.getsize(file)

                with open(file, 'rb') as f:

                    if file.endswith(".mp4"):

                        if size < 50 * 1024 * 1024:
                            sent = bot.send_video(chat_id, f)
                        else:
                            sent = bot.send_document(chat_id, f)

                    elif file.endswith(".jpg") or file.endswith(".png"):
                        sent = bot.send_photo(chat_id, f)

                    else:
                        sent = bot.send_document(chat_id, f)

                threading.Thread(
                    target=auto_delete,
                    args=(chat_id, sent.message_id)
                ).start()

                os.remove(file)

        bot.delete_message(chat_id, status.message_id)

        if not files_found:
            bot.send_message(chat_id, "❌ Download failed")

    except Exception as e:
        bot.send_message(chat_id, "❌ Download failed")
        print(e)


@bot.message_handler(func=lambda message: True)
def main(message):

    url = message.text.strip()

    if "instagram.com" in url:

        threading.Thread(
            target=download_instagram,
            args=(url, message.chat.id)
        ).start()

    else:
        bot.reply_to(message, "❌ Send Instagram link")


print("Bot running...")
bot.infinity_polling()
