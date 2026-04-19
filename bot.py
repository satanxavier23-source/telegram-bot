import os
import re
import asyncio
import aiohttp
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

AUTO_FORWARD_CHANNEL_ID = -1003932803968
AUTO_DELETE_SECONDS = 3600

URL_REGEX = re.compile(r'https?://\S+')

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "en-US,en;q=0.9",
}


def extract_url(text):
    if not text:
        return None
    links = URL_REGEX.findall(text)
    return links[0] if links else None


async def get_direct_link(url):
    try:
        async with aiohttp.ClientSession(headers=HEADERS) as session:
            async with session.get(url, allow_redirects=True) as resp:
                html = await resp.text()

                # 🔥 try to find direct video link
                match = re.search(r'https://[^"]+\.mp4', html)
                if match:
                    return match.group(0), None

                # fallback (rare cases)
                match2 = re.search(r'"downloadUrl":"(.*?)"', html)
                if match2:
                    return match2.group(1).replace("\\/", "/"), None

                return None, "Video link not found"

    except Exception as e:
        return None, str(e)


async def auto_delete(bot, chat_id, msg_id, delay):
    await asyncio.sleep(delay)
    try:
        await bot.delete_message(chat_id, msg_id)
    except:
        pass


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 TeraBox Downloader (No API)\n\nSend link 📥"
    )


async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    url = extract_url(text)

    if not url:
        await update.message.reply_text("❌ Link ഇല്ല")
        return

    msg = await update.message.reply_text("🔍 Processing...")

    link, error = await get_direct_link(url)

    if error:
        await msg.edit_text(f"❌ Failed\n{error}")
        return

    try:
        await msg.edit_text("📤 Uploading...")

        sent = await update.message.reply_video(video=link)

        # auto forward
        try:
            await context.bot.copy_message(
                chat_id=AUTO_FORWARD_CHANNEL_ID,
                from_chat_id=update.effective_chat.id,
                message_id=sent.message_id
            )
        except Exception as e:
            print("Forward error:", e)

        # auto delete
        asyncio.create_task(auto_delete(context.bot, sent.chat.id, sent.message_id, AUTO_DELETE_SECONDS))

        await msg.delete()

    except Exception as e:
        await msg.edit_text(f"❌ Upload failed\n{str(e)}")


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

    print("Bot running 🔥")
    app.run_polling()


if __name__ == "__main__":
    main()
