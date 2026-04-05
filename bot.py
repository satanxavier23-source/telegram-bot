import telebot
import yt_dlp
import os
import time

BOT_TOKEN = os.getenv("8623388098:AAGY5lF3kcbAN25K_ZZ5IzzEt0ddcs38RIQ")

bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(
        message,
        "Send Instagram Reel/Post/Story or Terabox link 📥"
    )


def download_video(url, chat_id, msg_id):

    def progress_hook(d):
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%')
            try:
                bot.edit_message_text(
                    f"⏳ Downloading {percent}",
                    chat_id,
                    msg_id
                )
            except:
                pass

    ydl_opts = {
        'outtmpl': 'video.%(ext)s',
        'format': 'best',
        'progress_hooks': [progress_hook],
        'quiet': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    for file in os.listdir():
        if file.startswith("video"):
            return file


@bot.message_handler(func=lambda message: True)
def downloader(message):

    url = message.text

    try:

        # Downloading message
