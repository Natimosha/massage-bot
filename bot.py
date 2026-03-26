import os
import logging
import asyncio
from maxapi import Bot, Dispatcher
from maxapi.types import MessageCreated, Command, MessageCallback
from maxapi.types import InlineKeyboard, InlineButton

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("BOT_TOKEN")
bot = Bot(TOKEN)
dp = Dispatcher()

# Тексты
START_MSG = "Привет! Я бот-помощник Натальи Тимошиной 👋\n\nВыбирайте:"

# Клавиатура - ПРАВИЛЬНЫЙ ФОРМАТ
MAIN_MENU = InlineKeyboard(buttons=[
    [InlineButton(type="callback", text="🔍 Разобрать мою ситуацию", payload="menu_diagnostics")],
    [InlineButton(type="callback", text="📚 Бесплатные материалы для роста", payload="menu_materials")],
    [InlineButton(type="callback", text="📈 Хочу больше клиентов", payload="menu_more_clients")]
])

@dp.message_created(Command("start"))
async def start_command(event: MessageCreated):
    chat_id = event.message.recipient.chat_id
    await bot.send_message(
        chat_id=chat_id,
        text=START_MSG,
        attachments=[MAIN_MENU]
    )
    logger.info(f"Отправлено меню пользователю {chat_id}")

@dp.message_created()
async def handle_text(event: MessageCreated):
    chat_id = event.message.recipient.chat_id
    text = event.message.body.text or ""
    await bot.send_message(
        chat_id=chat_id,
        text=f"Вы написали: {text}"
    )
    logger.info(f"Получено сообщение от {chat_id}: {text}")

@dp.message_callback()
async def handle_callback(event: MessageCallback):
    chat_id = event.message.recipient.chat_id
    payload = event.callback.payload or ""
    logger.info(f"Callback от {chat_id}: {payload}")
    
    if payload == "menu_diagnostics":
        await bot.send_message(
            chat_id=chat_id,
            text="Давайте проведём диагностику! Как вас зовут?"
        )
    elif payload == "menu_materials":
        await bot.send_message(
            chat_id=chat_id,
            text="Вот доступные материалы:\n\n1. 10 ошибок, из-за которых уходят клиенты\n2. Как ответить на «дорого»\n3. Шаблоны сообщений для записи"
        )
    elif payload == "menu_more_clients":
        await bot.send_message(
            chat_id=chat_id,
            text="Расскажите о вашей ситуации:\n\n1. Только начинаю, клиентов почти нет\n2. Клиенты есть, но мало и нестабильно\n3. Клиентов хватает, хочу больше зарабатывать"
        )
    elif payload == "back_menu":
        await start_command(event)

async def main():
    logger.info("Бот запускается...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
