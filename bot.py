import os
import time
import queue
import threading
from urllib.parse import quote

import requests
import telebot

# =========================
# CONFIG
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
APIFY_TOKEN = os.getenv("APIFY_TOKEN", "").strip()

# Actor endpoint
APIFY_URL = (
    "https://api.apify.com/v2/acts/"
    "igview-owner~terabox-fast-video-downloader/"
    "run-sync-get-dataset-items?token="
)

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN missing")

if not APIFY_TOKEN:
    raise ValueError("APIFY_TOKEN missing")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

VALID_HOSTS = [
    "terabox.com",
    "www.terabox.com",
    "1024terabox.com",
    "www.1024terabox.com",
    "teraboxapp.com",
    "www.teraboxapp.com",
    "teraboxlink.com",
    "www.teraboxlink.com",
    "nephobox.com",
    "www.nephobox.com",
    "4funbox.com",
    "www.4funbox.com",
    "mirrobox.com",
    "www.mirrobox.com",
    "momerybox.com",
    "www.momerybox.com",
    "terafileshare.com",
    "www.terafileshare.com",
]

download_queue = queue.Queue()
active_users = set()
lock = threading.Lock()


# =========================
# HELPERS
# =========================
def is_terabox_link(url: str) -> bool:
    url = (url or "").lower().strip()
    return any(host in url for host in VALID_HOSTS)


def get_apify_data(link: str):
    url = APIFY_URL + quote(APIFY_TOKEN, safe="")
    payload = {"link": link}

    r = requests.post(url, json=payload, timeout=300)
    r.raise_for_status()

    data = r.json()
    if not isinstance(data, list) or not data:
        raise Exception("No data returned from API")

    item = data[0]

    if not item.get("success"):
        err = item.get("error", "Unknown API error")
        raise Exception(err)

    video_url = item.get("streaming_url") or item.get("download_url")
    if not video_url:
        raise Exception("No streaming_url or download_url found")

    title = item.get("filename") or "TeraBox Video"
    size = item.get("size")
    return {
        "video_url": video_url,
        "title": title,
        "size": size,
        "raw": item
    }


def human_size(size):
    try:
        size = int(size)
    except:
        return "Unknown"
    units = ["B", "KB", "MB", "GB", "TB"]
    idx = 0
    while size >= 1024 and idx < len(units) - 1:
        size /= 1024
        idx += 1
    return f"{size:.2f} {units[idx]}"


def safe_edit(chat_id, msg_id, text):
    try:
        bot.edit_message_text(text, chat_id, msg_id, parse_mode="HTML")
    except:
        pass


def main_keyboard():
    kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("📊 Status", "❓ Help")
    return kb


# =========================
# WORKER
# =========================
def worker():
    while True:
        job = download_queue.get()
        if not job:
            continue

        chat_id = job["chat_id"]
        user_id = job["user_id"]
        link = job["link"]

        status_msg = None

        try:
            status_msg = bot.send_message(chat_id, "🔍 Link checking...")

            info = get_apify_data(link)

            title = info["title"]
            video_url = info["video_url"]
            size_text = human_size(info["size"])

            safe_edit(
                chat_id,
                status_msg.message_id,
                f"✅ Link resolved\n"
                f"🎬 <b>{title}</b>\n"
                f"📦 {size_text}\n\n"
                f"📤 Uploading to Telegram..."
            )

            # direct URL send
            bot.send_chat_action(chat_id, "upload_video")
            try:
                bot.send_video(
                    chat_id,
                    video_url,
                    caption=f"🎬 <b>{title}</b>\n🔥 Downloaded successfully"
                )
            except:
                bot.send_document(
                    chat_id,
                    video_url,
                    caption=f"🎬 <b>{title}</b>\n🔥 Sent as document"
                )

            safe_edit(
                chat_id,
                status_msg.message_id,
                f"✅ Completed\n"
                f"🎬 <b>{title}</b>\n"
                f"📦 {size_text}"
            )

        except Exception as e:
            error_text = str(e)[:350]
            if status_msg:
                safe_edit(chat_id, status_msg.message_id, f"❌ Failed\n<code>{error_text}</code>")
            else:
                bot.send_message(chat_id, f"❌ Failed\n<code>{error_text}</code>")

        finally:
            with lock:
                active_users.discard(user_id)
            download_queue.task_done()


# start 2 workers
for _ in range(2):
    t = threading.Thread(target=worker, daemon=True)
    t.start()


# =========================
# COMMANDS
# =========================
@bot.message_handler(commands=["start"])
def start_cmd(message):
    txt = (
        "🚀 <b>TeraBox Premium Downloader Bot</b>\n\n"
        "TeraBox link അയച്ചാൽ video download ചെയ്ത് അയക്കും.\n\n"
        "✅ Apify API\n"
        "✅ Queue system\n"
        "✅ Premium status\n\n"
        "Link അയക്കൂ 📥"
    )
    bot.send_message(message.chat.id, txt, reply_markup=main_keyboard())


@bot.message_handler(commands=["help"])
def help_cmd(message):
    txt = (
        "❓ <b>How to use</b>\n\n"
        "1. TeraBox link paste ചെയ്യുക\n"
        "2. Bot link resolve ചെയ്യും\n"
        "3. Video upload ചെയ്യും\n\n"
        "Button:\n"
        "📊 Status = queue status"
    )
    bot.send_message(message.chat.id, txt, reply_markup=main_keyboard())


@bot.message_handler(commands=["status"])
def status_cmd(message):
    with lock:
        active = len(active_users)
    qsize = download_queue.qsize()
    bot.send_message(
        message.chat.id,
        f"📊 <b>Status</b>\n\n"
        f"Queue: <b>{qsize}</b>\n"
        f"Active: <b>{active}</b>",
        reply_markup=main_keyboard()
    )


# =========================
# BUTTONS
# =========================
@bot.message_handler(func=lambda m: m.text == "📊 Status")
def btn_status(message):
    status_cmd(message)


@bot.message_handler(func=lambda m: m.text == "❓ Help")
def btn_help(message):
    help_cmd(message)


# =========================
# LINK HANDLER
# =========================
@bot.message_handler(func=lambda m: True, content_types=["text"])
def handle_text(message):
    text = (message.text or "").strip()

    if text in ["📊 Status", "❓ Help"]:
        return

    if not is_terabox_link(text):
        bot.reply_to(message, "❌ Valid TeraBox link അയക്കൂ")
        return

    with lock:
        if message.from_user.id in active_users:
            bot.reply_to(message, "⏳ നിങ്ങളുടെ download already running ആണ്. കുറച്ച് wait ചെയ്യൂ.")
            return

        active_users.add(message.from_user.id)

    pos = download_queue.qsize() + 1
    download_queue.put({
        "chat_id": message.chat.id,
        "user_id": message.from_user.id,
        "link": text
    })

    bot.reply_to(
        message,
        f"✅ Added to queue\n"
        f"🔢 Position: <b>{pos}</b>"
    )


# =========================
# RUN
# =========================
def run_bot():
    print("Bot running...")
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=30)
        except Exception as e:
            print("Polling error:", e)
            time.sleep(5)


if __name__ == "__main__":
    run_bot()
