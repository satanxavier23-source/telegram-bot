```python
import telebot
import yt_dlp
import os
import uuid

BOT_TOKEN = "YOUR_BOT_TOKEN"

bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "👋 Welcome!\n\n🎬 Send TeraBox link to download video."
    )


def download_video(url, filename):
    ydl_opts = {
        'outtmpl': filename,
        'format': 'best',
        'cookiefile': 'cookies.txt',
        'quiet': True,
        'noplaylist': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


@bot.message_handler(func=lambda message: True)
def handle(message):

    if not message.text:
        return

    url = message.text.strip()

    if "terabox" in url or "1024terabox" in url:

        bot.reply_to(message, "⏳ Downloading video...")

        unique_id = str(uuid.uuid4())
        filename = f"video_{unique_id}.mp4"

        try:
            download_video(url, filename)

            bot.send_message(message.chat.id, "📤 Uploading video...")

            with open(filename, "rb") as video:
                bot.send_video(message.chat.id, video)

            os.remove(filename)

            bot.send_message(message.chat.id, "✅ Done")

        except Exception as e:
            print("Error:", e)
            bot.send_message(
                message.chat.id,
                "❌ Download failed\nTry another link or refresh cookies."
            )

    else:
        bot.send_message(
            message.chat.id,
            "⚠️ Send valid TeraBox link"
        )


print("🤖 Bot running...")
bot.infinity_polling()
```
