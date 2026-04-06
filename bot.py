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


# start
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(
        message,
        "Instagram Downloader Bot 🤖\n\n"
        "Send Instagram:\n"
        "Reel 🎬\n"
        "Photo 📷\n"
        "Video 🎥\n"
        "Carousel 📂\n"
        "Story 📱\n"
        "Highlights ⭐\n\n"
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


# download
def download_instagram(url, chat_id):

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
        'outtmpl': f'insta_{unique}_%(title)s.%(ext)s',
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

            if file.startswith(f"insta_{unique}"):

                with open(file, 'rb') as f:

                    if file.endswith(".mp4"):

                        sent = bot.send_video(chat_id, f)

                        bot.send_message(
                            chat_id,
                            "⚠️ Video will be deleted after 1 hour ⏰"
                        )

                        threading.Thread(
                            target=auto_delete,
                            args=(chat_id, sent.message_id)
                        ).start()

                    elif file.endswith(".jpg") or file.endswith(".png"):

                        sent = bot.send_photo(chat_id, f)

                        bot.send_message(
                            chat_id,
                            "⚠️ Photo will be deleted after 1 hour ⏰"
                        )

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
        bot.send_message(
            chat_id,
            "❌ Download failed or cookies expired"
        )


# main
@bot.message_handler(func=lambda message: True)
def main(message):

    url = message.text.strip()

    if "instagram.com" in url:

        threading.Thread(
            target=download_instagram,
            args=(url, message.chat.id)
        ).start()

    else:
        bot.reply_to(
            message,
            "❌ Send Instagram link only"
        )


print("Bot running...")
bot.infinity_polling()
