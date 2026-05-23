                    response_text += f"`{aid}`\n"
                response_text += "\n"
            if stroke := found_buckets:
                response_text += "📦 **Storage Buckets (Bucket ID):**\n"
                for bucket in found_buckets:
                    response_text += f"`{bucket}`\n"
                response_text += "\n"
            bot.edit_message_text(response_text, message.chat.id, msg.message_id, parse_mode="Markdown")
        else:
            bot.edit_message_text("✅ Scan complete! Koi Firebase core configuration parameters nahi mile.", message.chat.id, msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ Scan ke dauran koi error aayi: {str(e)}", message.chat.id, msg.message_id)
        if os.path.exists(apk_path):
            os.remove(apk_path)

print("Bot chal raha hai...")
bot.infinity_polling()
