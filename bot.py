import telebot
import yt_dlp
import os
import time
import threading

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)

# stickers
DOWNLOAD_STICKER = "CAACAgIAAxkBAAEc4N1p1LTZmb8i6oASRfW-ZMKWFgYSNwACLAADJHFiGsUg5gPvePzkOwQ"
UPLOAD_STICKER = "CAACAgUAAxkBAAEc4OJp1LWYEjUSwApZlfkeg71X8fF98QACgQgAAngBKFSg3YsqMnYcsTsE"


# start message
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(
        message,
        "Hello 🙋‍♂️\n\n"
        "📥 Instagram Video Downloader Bot 📥\n\n"
        "➪ Send Instagram link 🖇\n"
        "➪ Reel ❤️\n"
        "➪ ⏱ Auto delete after 1 hour 😊\n\n"
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


# download function
def download_instagram(url, chat_id):

    status = bot.send_sticker(chat_id, DOWNLOAD_STICKER)

    unique = str(int(time.time()))

    ydl_opts = {
        'outtmpl': f'insta_{unique}.%(ext)s',
        'format': 'best',
        'cookiefile': 'instagram_cookies.txt',
        'quiet': True,
        'nocheckcertificate': True,
        'geo_bypass': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        bot.send_sticker(chat_id, UPLOAD_STICKER)

        sent_message = None

        for file in os.listdir():

            if file.startswith(f"insta_{unique}"):

                size = os.path.getsize(file)

                with open(file, 'rb') as f:

                    if file.endswith(".mp4"):

                        if size < 50 * 1024 * 1024:
                            sent_message = bot.send_video(chat_id, f)
                        else:
                            sent_message = bot.send_document(chat_id, f)

                    elif file.endswith(".jpg"):
                        sent_message = bot.send_photo(chat_id, f)

                    else:
                        sent_message = bot.send_document(chat_id, f)

                os.remove(file)

        bot.delete_message(chat_id, status.message_id)

        if sent_message:
            threading.Thread(
                target=auto_delete,
                args=(chat_id, sent_message.message_id)
            ).start()
        else:
            bot.send_message(chat_id, "❌ Private account / Cookies expired / File not found")

    except Exception as e:
        print(e)
        bot.send_message(chat_id, "❌ Download failed")


# message handler
@bot.message_handler(func=lambda message: True)
def main(message):

    url = message.text.strip()

    if "instagram.com" in url:

        threading.Thread(
            target=download_instagram,
            args=(url, message.chat.id)
        ).start()

    else:
        bot.reply_to(message, "❌ Send Instagram link only")


print("Bot running...")
bot.infinity_polling()
