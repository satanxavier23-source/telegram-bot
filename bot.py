import telebot

BOT_TOKEN = "YOUR_BOT_TOKEN"

bot = telebot.TeleBot(BOT_TOKEN)

SOURCE_CHAT_ID = -1003590340901
TARGET_CHAT_ID = -1003932803968


@bot.message_handler(func=lambda message: True, content_types=[
    'text', 'photo', 'video', 'document', 'audio', 'voice',
    'sticker', 'animation', 'contact', 'location'
])
def auto_copy(message):
    try:
        if message.chat.id == SOURCE_CHAT_ID:
            bot.copy_message(
                chat_id=TARGET_CHAT_ID,
                from_chat_id=message.chat.id,
                message_id=message.message_id
            )
            print(f"Copied: {message.message_id}")
    except Exception as e:
        print("Error:", e)


print("Bot is running...")
bot.infinity_polling(skip_pending=True, timeout=30)
