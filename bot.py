import os
import telebot
from telebot import types

BOT_TOKEN = os.getenv("BOT_TOKEN") or "YOUR_BOT_TOKEN"

bot = telebot.TeleBot(BOT_TOKEN)

# =========================
# SOURCE CHANNEL
# =========================
SOURCE_CHANNEL = -1003590340901

# =========================
# DEFAULT TARGET CHANNELS
# =========================
target_channels = [
    -1003932803968,
]

# =========================
# ADMIN
# =========================
ADMIN_IDS = [6630347046, 7194569468]

# =========================
# CAPTION SETTINGS
# =========================
CAPTION_TEXT = "കിന്നാരത്തുമ്പികൾ പ്രീമിയം ❤️📈🔥"
caption_enabled = True


def is_admin(user_id):
    return user_id in ADMIN_IDS


def main_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("🟢 Caption ON", "🔴 Caption OFF")
    kb.row("➕ Add Target", "➖ Remove Target")
    kb.row("📋 Target List", "📊 Status")
    return kb


def send_admin_message(chat_id, text):
    try:
        bot.send_message(chat_id, text)
    except Exception as e:
        print("Admin message error:", e)


@bot.message_handler(commands=["start"])
def start(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "Access denied ❌")
        return

    bot.reply_to(
        message,
        "V3 Auto Forward Bot Ready ✅",
        reply_markup=main_keyboard()
    )


@bot.message_handler(func=lambda m: is_admin(m.from_user.id) and m.text == "🟢 Caption ON")
def caption_on(message):
    global caption_enabled
    caption_enabled = True
    bot.reply_to(message, "Caption ON ayi ✅")


@bot.message_handler(func=lambda m: is_admin(m.from_user.id) and m.text == "🔴 Caption OFF")
def caption_off(message):
    global caption_enabled
    caption_enabled = False
    bot.reply_to(message, "Caption OFF ayi ✅")


@bot.message_handler(func=lambda m: is_admin(m.from_user.id) and m.text == "📊 Status")
def status(message):
    txt = "\n".join(str(x) for x in target_channels) if target_channels else "No targets"
    bot.reply_to(
        message,
        f"Source: {SOURCE_CHANNEL}\n\n"
        f"Caption: {'ON ✅' if caption_enabled else 'OFF ❌'}\n"
        f"Caption Text: {CAPTION_TEXT}\n\n"
        f"Targets:\n{txt}"
    )


@bot.message_handler(func=lambda m: is_admin(m.from_user.id) and m.text == "📋 Target List")
def target_list(message):
    if not target_channels:
        bot.reply_to(message, "Target channels ഇല്ല ❌")
        return

    txt = "\n".join([f"{i+1}. {cid}" for i, cid in enumerate(target_channels)])
    bot.reply_to(message, f"Target channels 📋\n\n{txt}")


@bot.message_handler(func=lambda m: is_admin(m.from_user.id) and m.text == "➕ Add Target")
def add_target_prompt(message):
    msg = bot.reply_to(
        message,
        "New target channel ID അയക്കൂ\n\nExample:\n-1003932803968"
    )
    bot.register_next_step_handler(msg, add_target_save)


def add_target_save(message):
    global target_channels
    if not is_admin(message.from_user.id):
        return

    try:
        cid = int(message.text.strip())
        if cid in target_channels:
            bot.reply_to(message, "ഈ target already ഉണ്ട് ✅")
            return

        target_channels.append(cid)
        bot.reply_to(message, f"Target added ✅\n{cid}")
    except:
        bot.reply_to(message, "Invalid channel ID ❌")


@bot.message_handler(func=lambda m: is_admin(m.from_user.id) and m.text == "➖ Remove Target")
def remove_target_prompt(message):
    if not target_channels:
        bot.reply_to(message, "Target channels ഇല്ല ❌")
        return

    txt = "\n".join([f"{i+1}. {cid}" for i, cid in enumerate(target_channels)])
    msg = bot.reply_to(
        message,
        f"Remove ചെയ്യാനുള്ള target ID അയക്കൂ:\n\n{txt}"
    )
    bot.register_next_step_handler(msg, remove_target_save)


def remove_target_save(message):
    global target_channels
    if not is_admin(message.from_user.id):
        return

    try:
        cid = int(message.text.strip())
        if cid not in target_channels:
            bot.reply_to(message, "ഈ target list il ഇല്ല ❌")
            return

        target_channels.remove(cid)
        bot.reply_to(message, f"Target removed ✅\n{cid}")
    except:
        bot.reply_to(message, "Invalid channel ID ❌")


def forward_to_target(target_id, source_id, message_id, content_type):
    global caption_enabled

    if content_type == "text":
        bot.forward_message(target_id, source_id, message_id)
    else:
        bot.forward_message(target_id, source_id, message_id)

        if caption_enabled:
            bot.send_message(target_id, CAPTION_TEXT)


@bot.channel_post_handler(func=lambda m: True)
def auto_forward(message):
    try:
        print("POST RECEIVED ✅")
        print("CHAT ID:", message.chat.id)
        print("TYPE:", message.content_type)
        print("MESSAGE ID:", message.message_id)

        if message.chat.id != SOURCE_CHANNEL:
            print("Ignored: not source channel")
            return

        if not target_channels:
            print("No target channels")
            return

        for target_id in target_channels:
            try:
                forward_to_target(
                    target_id,
                    SOURCE_CHANNEL,
                    message.message_id,
                    message.content_type
                )
                print(f"Sent to {target_id} ✅")
            except Exception as e:
                print(f"Target send failed {target_id} ❌", e)
                for admin_id in ADMIN_IDS:
                    try:
                        bot.send_message(admin_id, f"Target send failed ❌\nTarget: {target_id}\nError: {e}")
                    except:
                        pass

        print("FORWARD DONE ✅")

    except Exception as e:
        print("FORWARD ERROR ❌", e)
        for admin_id in ADMIN_IDS:
            try:
                bot.send_message(admin_id, f"Forward error ❌\n{e}")
            except:
                pass


print("Bot Running ✅")
bot.infinity_polling(
    timeout=60,
    long_polling_timeout=60,
    skip_pending=True,
    allowed_updates=["message", "channel_post"]
)
