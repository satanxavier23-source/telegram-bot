with open(file, 'rb') as f:
                    if size < 50 * 1024 * 1024:
                        sent_message = bot.send_video(chat_id, f, caption=caption)
                    else:
                        sent_message = bot.send_document(chat_id, f, caption=caption)

                os.remove(file)

        bot.delete_message(chat_id, upload_sticker_msg.message_id)

        if sent_message:
            threading.Thread(
                target=auto_delete,
                args=(chat_id, sent_message.message_id)
            ).start()
        else:
            bot.send_message(chat_id, "❌ Reel not found or private")

    except Exception as e:
        print(e)
        bot.send_message(chat_id, "❌ Download failed")


# Handler
@bot.message_handler(func=lambda message: True)
def main(message):

    url = message.text.strip()

    if "instagram.com/reel" in url:
        executor.submit(download_reel, url, message.chat.id)
    else:
        bot.reply_to(message, "❌ Send Instagram Reel link only")


print("Bot running...")
bot.infinity_polling()
