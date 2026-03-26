import os
import logging
import asyncio
from maxapi import Bot, Dispatcher
from maxapi.types import MessageCreated

logging.basicConfig(level=logging.INFO)

TOKEN = os.environ.get("BOT_TOKEN")
bot = Bot(TOKEN)
dp = Dispatcher()

@dp.message_created()
async def echo(event: MessageCreated):
    try:
        chat_id = event.chat_id
        text = event.message.body.text or ""
        
        await bot.send_message(
            chat_id=chat_id,
            text=f"✅ Бот работает! Вы написали: {text}"
        )
        logging.info(f"Сообщение от {chat_id}: {text}")
    except Exception as e:
        logging.error(f"Ошибка в обработчике: {e}")

async def main():
    logging.info("🚀 Бот запускается...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
