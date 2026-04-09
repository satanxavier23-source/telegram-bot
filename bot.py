import telebot
import yt_dlp
import os
import time
import threading
from concurrent.futures import ThreadPoolExecutor

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    print("BOT_TOKEN missing")
    exit()

bot = telebot.TeleBot(BOT_TOKEN)
executor = ThreadPoolExecutor(max_workers=5)

DOWNLOAD_STICKER = "CAACAgIAAxkBAAEc4N1p1LTZmb8i6oASRfW-ZMKWFgYSNwACLAADJHFiGsUg5gPvePzkOwQ"
UPLOAD_STICKER = "CAACAgUAAxkBAAEc4OJp1LWYEjUSwApZlfkeg71X8fF98QACgQgAAngBKFSg3YsqMnYcsTsE"
COMPLETE_STICKER = "CAACAgUAAxkBAAEc6YRp1g1Hs3dImubILNBijx9Lc-5MYgACiRIAAvvIyFT3g23-b9WjpjsE"
DELETE_STICKER = "CAACAgUAAxkBAAEc6Ypp1g3oUEly079a3JebtyoYO8zUCQACryEAAkcLsFbGcJe3XAXz-zsE"


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(
        message,
        "Hello 🙋‍♂️\n\n"
        "📥 Instagram Downloader Bot 📥\n\n"
        "➪ Send Instagram Reel/Post/Story link 🖇\n"
        "➪ ⚡ Fast Download\n"
        "➪ ⏱ Auto delete after 1 hour\n\n"
        "Developer : 𝐕𝐊 👨🏻‍💻"
    )


def auto_delete(chat_id, message_id):
    time.sleep(3600)
    try:
        bot.delete_message(chat_id, message_id)
        bot.send_sticker(chat_id, DELETE_STICKER)
        bot.send_message(chat_id, "🗑 Automatic Delete After 1 Hour 🫂")
    except:
        pass


def download_instagram(url, chat_id):
    try:
        download_sticker = bot.send_sticker(chat_id, DOWNLOAD_STICKER)
        progress = bot.send_message(chat_id, "📥 Downloading...")

        unique = str(int(time.time()))

        ydl_opts = {
            'outtmpl': f'insta_{unique}_%(index)s.%(ext)s',
            'format': 'best',
            'quiet': True,
            'nocheckcertificate': True,
            'retries': 10,
            'fragment_retries': 10,
            'noplaylist': True,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0',
                'Referer': 'https://www.instagram.com/'
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)

        bot.delete_message(chat_id, progress.message_id)

        bot.send_sticker(chat_id, COMPLETE_STICKER)
        upload_sticker = bot.send_sticker(chat_id, UPLOAD_STICKER)

        caption = "Download by @inssavetome_bot\nAutomatic Delete After 1 Hour 🫂"

        files = []

        for file in os.listdir():
            if file.startswith(f"insta_{unique}"):
                files.append(file)

        files.sort()

        sent_messages = []

        for file in files:
            with open(file, 'rb') as f:

                if file.endswith(".mp4"):
                    msg = bot.send_video(chat_id, f, caption=caption)

                elif file.endswith(".jpg") or file.endswith(".jpeg") or file.endswith(".png"):
                    msg = bot.send_photo(chat_id, f, caption=caption)

                else:
                    continue

                sent_messages.append(msg)

            os.remove(file)

        bot.delete_message(chat_id, upload_sticker.message_id)
        bot.delete_message(chat_id, download_sticker.message_id)

        for msg in sent_messages:
            threading.Thread(
                target=auto_delete,
                args=(chat_id, msg.message_id)
            ).start()

        if not sent_messages:
            bot.send_message(chat_id, "❌ No media found")

    except Exception as e:
        print("ERROR:", e)
        bot.send_message(chat_id, "❌ Download failed")


@bot.message_handler(func=lambda message: True)
def main(message):

    url = message.text.strip()

    if "?" in url:
        url = url.split("?")[0]

    if "instagram.com" in url:
        executor.submit(download_instagram, url, message.chat.id)
    else:
        bot.reply_to(message, "❌ Send Instagram link only")


print("Bot running...")
bot.infinity_polling()
