import telebot
import yt_dlp
import os
import uuid

BOT_TOKEN = "8623388098:AAGY5lF3kcbAN25K_ZZ5IzzEt0ddcs38RIQ"

bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "📥 Send Instagram Reel/Post Link")


@bot.message_handler(func=lambda message: True)
def download_video(message):
    url = message.text.strip()

    if "instagram.com" not in url:
        bot.reply_to(message, "❌ Send valid Instagram link")
        return

    bot.reply_to(message, "⏳ Downloading...")

    file_name = f"video_{uuid.uuid4().hex}.mp4"

    ydl_opts = {
        'format': 'best',
        'outtmpl': file_name,
        'quiet': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        if os.path.exists(file_name):

            with open(file_name, "rb") as video:
                bot.send_video(message.chat.id, video)

            os.remove(file_name)

        else:
            bot.send_message(message.chat.id, "❌ Download failed")

    except Exception as e:
        bot.send_message(message.chat.id, "❌ Instagram blocked or invalid link")
        print(e)


bot.infinity_polling()