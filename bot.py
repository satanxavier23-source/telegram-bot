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

# Stickers
DOWNLOAD_STICKER = "CAACAgIAAxkBAAEc4N1p1LTZmb8i6oASRfW-ZMKWFgYSNwACLAADJHFiGsUg5gPvePzkOwQ"
UPLOAD_STICKER = "CAACAgUAAxkBAAEc4OJp1LWYEjUSwApZlfkeg71X8fF98QACgQgAAngBKFSg3YsqMnYcsTsE"
COMPLETE_STICKER = "CAACAgUAAxkBAAEc6YRp1g1Hs3dImubILNBijx9Lc-5MYgACiRIAAvvIyFT3g23-b9WjpjsE"
DELETE_STICKER = "CAACAgUAAxkBAAEc6Ypp1g3oUEly079a3JebtyoYO8zUCQACryEAAkcLsFbGcJe3XAXz-zsE"


# Start Message
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(
        message,
        "Hello 🙋‍♂️\n\n"
        "📥 Instagram Reel Downloader Bot 📥\n\n"
        "➪ Send Instagram Reel link 🖇\n"
        "➪ ⚡ Fast Download\n"
        "➪ ⏱ Auto delete after 1 hour\n\n"
        "Developer : 𝐕𝐊 👨🏻‍💻"
    )


# Auto Delete Video
def auto_delete(chat_id, message_id):
    time.sleep(3600)
    try:
        bot.delete_message(chat_id, message_id)
        bot.send_sticker(chat_id, DELETE_STICKER)
        bot.send_message(chat_id, "🗑 Automatic Delete After 1 Hour 🫂")
    except:
        pass


# Download Reel
def download_reel(url, chat_id):
    try:
        download_sticker_msg = bot.send_sticker(chat_id, DOWNLOAD_STICKER)
        progress_msg = bot.send_message(chat_id, "📥 Downloading Reel...")

        unique = str(int(time.time()))

        def progress_hook(d):
            if d['status'] == 'downloading':
                percent_str = d.get('_percent_str', '0%').strip()

                try:
                    percent = int(percent_str.replace('%', '').strip())
                except:
                    percent = 0

                bars = percent // 5
                bar = "█" * bars + "░" * (20 - bars)

                text = (
                    "📥 Downloading Reel\n\n"
                    f"{bar} {percent}%"
                )

                try:
                    bot.edit_message_text(
                        text,
                        chat_id,
                        progress_msg.message_id
                    )
                except:
                    pass

            if d['status'] == 'finished':
                try:
                    bot.edit_message_text(
                        "████████████████████ 100%\n\n✅ Download Complete",
                        chat_id,
                        progress_msg.message_id
                    )

                    bot.send_sticker(chat_id, COMPLETE_STICKER)

                    time.sleep(3)

                    bot.delete_message(chat_id, progress_msg.message_id)
                    bot.delete_message(chat_id, download_sticker_msg.message_id)

                except:
                    pass

        ydl_opts = {
            'outtmpl': f'reel_{unique}.%(ext)s',
            'format': 'mp4/best',
            'quiet': True,
            'nocheckcertificate': True,
            'concurrent_fragment_downloads': 5,
            'retries': 5,
            'noplaylist': True,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0',
                'Accept-Language': 'en-US,en;q=0.9'
            },
            'extractor_args': {
                'instagram': {
                    'skip': ['dash', 'hls']
                }
            },
            'progress_hooks': [progress_hook]
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        upload_sticker_msg = bot.send_sticker(chat_id, UPLOAD_STICKER)

        caption_text = info.get("description", "")

        caption = (
            "Download by @inssavetome_bot\n"
            "Automatic Delete After 1 Hour 🫂\n\n"
            f"{caption_text[:900]}"
        )

        sent_message = None

        for file in os.listdir():
            if file.startswith(f"reel_{unique}"):

                size = os.path.getsize(file)
                with open(file, 'rb') as f:
                    if size < 50 * 1024 * 1024:
                        sent_message = bot.send_video(chat_id, f, caption=caption)
                    else:
                        sent_message = bot.send_document(chat_id, f, caption=caption)

                os.remove(file)

        bot.delete_message(chat_id, upload_sticker_msg.message_id)

        if sent_message:
            threading.Thread(
                target=auto_delete,
                args=(chat_id, sent_message.message_id)
            ).start()
        else:
            bot.send_message(chat_id, "❌ Reel not found or private")

    except Exception as e:
        print(e)
        bot.send_message(chat_id, "❌ Download failed")


# Handler
@bot.message_handler(func=lambda message: True)
def main(message):

    url = message.text.strip()

    if "instagram.com/reel" in url:
        executor.submit(download_reel, url, message.chat.id)
    else:
        bot.reply_to(message, "❌ Send Instagram Reel link only")


print("Bot running...")
bot.infinity_polling()
