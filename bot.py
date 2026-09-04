import asyncio
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Yahan aap apne 2 alag-alag bots ke tokens aur unke target group daal sakte hain
BOT_CONFIGS = [
    {
        "token": "8462187621:AAGKHzcyORpkzMv3DDQSsCxLMv2zXkZwc3I",  # Pehle bot ka token
        "chat_id": "https://t.me/vikshhy",
    },
    {
        "token": "BOT_TOKEN_2_HERE",  # Dusre bot ka token
        "chat_id": "@your_public_group_2",
    },
]


async def create_forwarder(token: str, chat_id: str):
    """Har ek bot ke liye alag handler aur instance banata hai."""
    application = ApplicationBuilder().token(token).build()

    async def forward_to_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = update.message
        if message and message.chat.type == "private":
            user = message.from_user
            user_info = (
                f"📥 **New Message**\n"
                f"👤 **From:** {user.full_name} (@{user.username if user.username else 'No Username'})\n"
                f"🆔 **ID:** `{user.id}`\n\n"
            )
            try:
                await context.bot.send_message(
                    chat_id=chat_id, text=user_info, parse_mode="Markdown"
                )
                await context.bot.forward_message(
                    chat_id=chat_id,
                    from_chat_id=message.chat_id,
                    message_id=message.message_id,
                )
            except Exception as e:
                logging.error(f"Error with token {token[:5]}...: {e}")

    application.add_handler(
        MessageHandler(filters.ChatType.PRIVATE & ~filters.COMMAND, forward_to_group)
    )

    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    print(f"Bot active with token prefix: {token[:10]}...")


async def main():
    # Dono bots ko ek sath run karne ke liye tasks banana
    tasks = [create_forwarder(config["token"], config["chat_id"]) for config in BOT_CONFIGS]
    await asyncio.gather(*tasks)

    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())
  
