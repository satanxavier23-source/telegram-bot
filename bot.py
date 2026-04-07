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


# START
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(
        message,
        "Instagram Downloader Bot 🤖\n\n"
        "Send Instagram link:\n"
        "Reel 🎬\n"
        "Photo 📷\n"
        "Video 🎥\n"
        "Carousel 📂\n"
        "Story 📱\n"
        "Highlights ⭐\n\n"
        "⚠️ Files auto delete after 1 hour ⏰"
    )


# AUTO DELETE FUNCTION
def auto_delete(chat_id, message_id):

    time.sleep(3600)

    try:
        bot.delete_message(chat_id, message_id)

        bot.send_message(
            chat_id,
            "🗑 File deleted automatically after 1 hour"
        )
    except:
        pass


# DOWNLOAD FUNCTION
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
        'format': 'best',
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

        files_found = False

        for file in os.listdir():

            if file.startswith(f"insta_{unique}"):

                files_found = True

                file_path = file
                file_size = os.path.getsize(file_path)

                with open(file_path, 'rb') as f:

                    # video
                    if file.endswith(".mp4"):

                        if file_size < 50 * 1024 * 1024:
                            sent = bot.send_video(chat_id, f)
                        else:
                            sent = bot.send_document(chat_id, f)

                        bot.send_message(
                            chat_id,
                            "⚠️ Video will be deleted after 1 hour ⏰"
                        )

                    # photo
                    elif file.endswith(".jpg") or file.endswith(".png"):

                        sent = bot.send_photo(chat_id, f)

                        bot.send_message(
                            chat_id,
                            "⚠️ Photo will be deleted after 1 hour ⏰"
                        )

                    else:
                        sent = bot.send_document(chat_id, f)

                threading.Thread(
                    target=auto_delete,
                    args=(chat_id, sent.message_id)
                ).start()

                os.remove(file_path)

        if not files_found:
            bot.send_message(
                chat_id,
                "❌ Private account / cookies expired / file not found"
            )

        bot.delete_message(chat_id, status.message_id)

    except Exception as e:
        bot.send_message(
            chat_id,
            "❌ Download failed or cookies expired"
        )


# MAIN
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
