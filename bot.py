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


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(
        message,
        "Instagram Downloader Bot 🤖\n\n"
        "Send Instagram link\n"
        "Reel / Post / Story / Highlights\n\n"
        "🔍 Debug mode enabled"
    )


def auto_delete(chat_id, message_id):
    time.sleep(3600)
    try:
        bot.delete_message(chat_id, message_id)
        bot.send_message(chat_id, "🗑 File deleted after 1 hour")
    except Exception as e:
        print("Auto delete error:", e)


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
        'cookiefile': 'instagram_cookies.txt',
        'progress_hooks': [progress_hook],
        'quiet': False,
        'nocheckcertificate': True,
        'geo_bypass': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0'
        }
    }

    try:
        print("Downloading:", url)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        print("Download success")

        bot.edit_message_text("⬆️ Uploading...", chat_id, status.message_id)

        files_found = False

        for file in os.listdir():

            if file.startswith(f"insta_{unique}"):

                files_found = True

                size = os.path.getsize(file)
                print("File:", file, "Size:", size)

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

        if not files_found:
            bot.send_message(
                chat_id,
                "❌ No file found (check cookies or link)"
            )

        bot.delete_message(chat_id, status.message_id)

    except Exception as e:

        print("ERROR:", str(e))

        bot.send_message(
            chat_id,
            f"❌ Download failed\n\nError:\n{str(e)}"
        )


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
