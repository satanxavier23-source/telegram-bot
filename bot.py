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
FORCE_JOIN_CHANNEL = os.getenv("FORCE_JOIN_CHANNEL", "")
AUTO_FORWARD_CHANNEL_ID = -1003932803968
AUTO_DELETE_SECONDS = 3600

TERABOX_DOMAINS = [
    "terabox.com",
    "1024terabox.com",
    "teraboxapp.com",
    "nephobox.com",
    "freeterabox.com",
    "4funbox.com",
    "mirrobox.com",
    "terasharelink.com",
    "terasharefile.com",
]

URL_REGEX = re.compile(r'https?://\S+')

API_LIST = [
    "https://teraboxvideodownloader.nepcoderdevs.workers.dev/?url={url}",
    "https://teraboxapi2.onrender.com/api?url={url}",
]


def extract_url(text: str) -> str | None:
    if not text:
        return None
    links = URL_REGEX.findall(text)
    return links[0] if links else None


def is_terabox_url(url: str) -> bool:
    url = url.lower()
    return any(domain in url for domain in TERABOX_DOMAINS)


async def is_user_joined(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> bool:
    if not FORCE_JOIN_CHANNEL:
        return True

    channel = FORCE_JOIN_CHANNEL
    if not channel.startswith("@"):
        channel = "@" + channel

    try:
        member = await context.bot.get_chat_member(channel, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False


async def fetch_direct_link(url: str) -> tuple[str | None, str | None]:
    timeout = aiohttp.ClientTimeout(total=30)
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    for api_template in API_LIST:
        api_url = api_template.format(url=url)

        try:
            async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
                async with session.get(api_url) as resp:
                    raw_text = await resp.text()

                    if resp.status != 200:
                        print(f"API failed: {api_url} -> HTTP {resp.status}")
                        continue

                    try:
                        data = await resp.json(content_type=None)
                    except Exception:
                        print(f"Invalid JSON from: {api_url}")
                        print(raw_text[:300])
                        continue

                    direct_link = (
                        data.get("download")
                        or data.get("download_url")
                        or data.get("url")
                        or data.get("direct_link")
                        or data.get("video")
                    )

                    if direct_link:
                        print(f"Success API: {api_url}")
                        return direct_link, None

                    print(f"No link found from: {api_url}")
                    print(str(data)[:300])

        except asyncio.TimeoutError:
            print(f"Timeout API: {api_url}")
            continue
        except Exception as e:
            print(f"Request failed: {api_url} -> {str(e)}")
            continue

    return None, "All API failed ❌"


async def auto_delete_message(bot, chat_id, message_id, wait_time):
    await asyncio.sleep(wait_time)
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception:
        pass


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🚀 *TeraBox Downloader Bot*\n\n"
        "📥 TeraBox link അയക്കൂ\n"
        "⚡ Fast processing\n"
        "🗑 File auto delete after 1 hour\n"
    )

    if FORCE_JOIN_CHANNEL:
        channel = FORCE_JOIN_CHANNEL
        if not channel.startswith("@"):
            channel = "@" + channel
        text += f"\n🔔 ആദ്യം join ചെയ്യൂ: {channel}"

    await update.message.reply_text(text, parse_mode="Markdown")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    text = update.message.text.strip()

    joined = await is_user_joined(context, user_id)
    if not joined:
        channel = FORCE_JOIN_CHANNEL
        if not channel.startswith("@"):
            channel = "@" + channel
        await update.message.reply_text(f"❌ ആദ്യം ഈ channel join ചെയ്യണം:\n{channel}")
        return

    url = extract_url(text)
    if not url:
        await update.message.reply_text("❌ Link കണ്ടില്ല")
        return

    if not is_terabox_url(url):
        await update.message.reply_text("❌ Valid TeraBox link അയക്കൂ")
        return

    status_msg = await update.message.reply_text("🔍 Link processing...")

    direct_link, error = await fetch_direct_link(url)

    if error:
        await status_msg.edit_text(f"❌ Failed\n\n{error}")
        return

    try:
        await status_msg.edit_text("⬇️ Download ready...\n📤 Uploading to Telegram...")

        sent = await update.message.reply_video(
            video=direct_link,
            caption="✅ Downloaded successfully"
        )

        try:
            await context.bot.copy_message(
                chat_id=AUTO_FORWARD_CHANNEL_ID,
                from_chat_id=chat_id,
                message_id=sent.message_id
            )
            print("Auto forward success")
        except Exception as e:
            print("Auto forward error:", e)

        asyncio.create_task(
            auto_delete_message(context.bot, sent.chat_id, sent.message_id, AUTO_DELETE_SECONDS)
        )

        done = await update.message.reply_text("🗑 File will auto delete after 1 hour")
        asyncio.create_task(
            auto_delete_message(context.bot, done.chat_id, done.message_id, AUTO_DELETE_SECONDS)
        )

        await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text(f"❌ Telegram upload failed\n\n{str(e)[:300]}")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    print("ERROR:", context.error)


def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN missing")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
