import telebot
import yt_dlp
import os
import uuid
import threading
import time
from concurrent.futures import ThreadPoolExecutor

BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

bot = telebot.TeleBot(BOT_TOKEN)

# stickers
DOWNLOADING_STICKER = "CAACAgUAAxkBAAEc6YRp1g1Hs3dImubILNBijx9Lc-5MYgACiRIAAvvIyFT3g23-b9WjpjsE"
FAILED_STICKER = "CAACAgUAAxkBAAEc6Ypp1g3oUEly079a3JebtyoYO8zUCQACryEAAkcLsFbGcJe3XAXz-zsE"

# thread pool (multiple download)
executor = ThreadPoolExecutor(max_workers=5)


# auto delete
def auto_delete(chat_id, msg_ids):
    time.sleep(3600)
    for msg in msg_ids:
        try:
            bot.delete_message(chat_id, msg)
        except:
            pass


# start message
@bot.message_handler(commands=['start'])
def start(message):
    text = """Hello 🙋‍♂️

📥 Instagram Reel Downloader Bot 📥

➪ Send Instagram Reel link 🖇
➪ ⚡ Fast Download
➪ ⏱ Auto delete after 1 hour

Developer : 𝐕𝐊 👨🏻‍💻
"""
    bot.send_message(message.chat.id, text)


# download function
def process_download(message, url):

    try:
        bot.send_sticker(message.chat.id, DOWNLOADING_STICKER)
        downloading_msg = bot.send_message(message.chat.id, "📥 Downloading Reel...")

        unique = str(uuid.uuid4())

        ydl_opts = {
            'format': 'best',
            'outtmpl': f'insta_{unique}.mp4',
            'quiet': True,
            'noplaylist': True,
            'retries': 10,
            'fragment_retries': 10,
            'nocheckcertificate': True,
            'ignoreerrors': True,
            'sleep_interval': 2,
            'max_sleep_interval': 5,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0',
                'Referer': 'https://www.instagram.com/'
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)

        file_name = f"insta_{unique}.mp4"

        if not os.path.exists(file_name):
            bot.send_sticker(message.chat.id, FAILED_STICKER)
            bot.send_message(message.chat.id, "❌ Download failed")
            return

        sent_video = bot.send_video(
            message.chat.id,
            open(file_name, 'rb'),
            caption="Downloaded by @inssavetome_bot\nAutomatic Delete After 1 Hour 🫂"
        )

        os.remove(file_name)

        msg_ids = [
            message.message_id,
            downloading_msg.message_id,
            sent_video.message_id
        ]

        threading.Thread(
            target=auto_delete,
            args=(message.chat.id, msg_ids)
        ).start()

    except Exception as e:
        bot.send_sticker(message.chat.id, FAILED_STICKER)
        bot.send_message(message.chat.id, "❌ Download failed")
        print(e)


# message handler
@bot.message_handler(func=lambda m: True)
def download(message):
    url = message.text.strip()

    if "instagram.com" not in url:
        bot.send_message(message.chat.id, "Send Instagram link")
        return

    if "/stories/" in url:
        bot.send_message(message.chat.id, "❌ Story download not supported")
        return

    executor.submit(process_download, message, url)


print("Bot Running...")
bot.infinity_polling()
