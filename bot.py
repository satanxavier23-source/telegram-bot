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

# stickers
DOWNLOAD_STICKER = "CAACAgIAAxkBAAEc4N1p1LTZmb8i6oASRfW-ZMKWFgYSNwACLAADJHFiGsUg5gPvePzkOwQ"
UPLOAD_STICKER = "CAACAgUAAxkBAAEc4OJp1LWYEjUSwApZlfkeg71X8fF98QACgQgAAngBKFSg3YsqMnYcsTsE"


# start message
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(
        message,
        "Hello 🙋‍♂️\n\n"
        "📥 Instagram Reel Downloader Bot 📥\n\n"
        "➪ Send Instagram Reel link 🖇\n"
        "➪ ⚡ Fast Download\n"
        "➪ 📊 Progress Bar\n"
        "➪ 👥 Multiple Users\n"
        "➪ ⏱ Auto delete after 1 hour\n\n"
        "➪ Developer : 𝐕𝐊 👨🏻‍💻"
    )


# auto delete function
def auto_delete(chat_id, message_id):
    time.sleep(3600)
    try:
        bot.delete_message(chat_id, message_id)
        bot.send_message(chat_id, "🗑 File deleted after 1 hour")
    except:
        pass


# download reel
def download_reel(url, chat_id):
    try:
        sticker = bot.send_sticker(chat_id, DOWNLOAD_STICKER)
        progress_msg = bot.send_message(chat_id, "📥 Downloading: 0%")

        unique = str(int(time.time()))

        def progress_hook(d):
            if d['status'] == 'downloading':
                percent = d.get('_percent_str', '0%').strip()
                try:
                    bot.edit_message_text(
                        f"📥 Downloading: {percent}",
                        chat_id,
                        progress_msg.message_id
                    )
                except:
                    pass

            if d['status'] == 'finished':
                try:
                    bot.edit_message_text(
                        "✅ Download complete",
                        chat_id,
                        progress_msg.message_id
                    )
                except:
                    pass

        ydl_opts = {
            'outtmpl': f'reel_{unique}.%(ext)s',
            'format': 'best[ext=mp4]',
            'quiet': True,
            'nocheckcertificate': True,
            'concurrent_fragment_downloads': 5,
            'retries': 3,
            'progress_hooks': [progress_hook],
            'http_headers': {
                'User-Agent': 'Mozilla/5.0'
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        bot.send_sticker(chat_id, UPLOAD_STICKER)

        username = info.get("uploader", "Instagram User")
        caption_text = info.get("description", "")

        caption = (
            "Thank you for use me 😊\n\n"
            f"👤 {username}\n\n"
            f"{caption_text[:900]}"
        )

        sent_message = None

        for file in os.listdir():

            if file.startswith(f"reel_{unique}"):

                size = os.path.getsize(file)

                with open(file, 'rb') as f:

                    if size < 50 * 1024 * 1024:
                        sent_message = bot.send_video(
                            chat_id,
                            f,
                            caption=caption
                        )
                    else:
                        sent_message = bot.send_document(
                            chat_id,
                            f,
                            caption=caption
                        )

                os.remove(file)

        bot.delete_message(chat_id, sticker.message_id)

        if sent_message:
            threading.Thread(
                target=auto_delete,
                args=(chat_id, sent_message.message_id)
            ).start()
        else:
            bot.send_message(chat_id, "❌ Reel not found")

    except Exception as e:
        print(e)
        bot.send_message(chat_id, "❌ Download failed")


# handler
@bot.message_handler(func=lambda message: True)
def main(message):

    url = message.text.strip()

    if "instagram.com/reel" in url:
        executor.submit(download_reel, url, message.chat.id)

    else:
        bot.reply_to(message, "❌ Send Instagram Reel link only")


print("Bot running...")
bot.infinity_polling()
