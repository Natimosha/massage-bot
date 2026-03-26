import os
import logging
import asyncio
from maxapi import Bot, Dispatcher
from maxapi.types import MessageCreated, Command, MessageCallback, BotStarted
from maxapi.types import CallbackButton, LinkButton, ButtonsPayload, Attachment

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("BOT_TOKEN")
bot = Bot(TOKEN)
dp = Dispatcher()


def make_kb(buttons):
    """Создает inline-клавиатуру"""
    rows = []
    for row in buttons:
        r = []
        for item in row:
            if len(item) == 3 and item[2] == "link":
                r.append(LinkButton(text=item[0], url=item[1]))
            else:
                r.append(CallbackButton(text=item[0], payload=item[1]))
        rows.append(r)
    
    payload = ButtonsPayload(buttons=rows)
    attachment = Attachment(type="inline_keyboard", payload=payload)
    return [attachment]


# Клавиатуры
MAIN_MENU = make_kb([
    [("🔍 Разобрать мою ситуацию", "menu_diag")],
    [("📚 Бесплатные материалы для роста", "menu_mat")],
    [("📈 Хочу больше клиентов", "menu_clients")],
])

KB_BACK = make_kb([
    [("🔙 Вернуться в меню", "back_menu")],
])


# Хранилище пользователей
users = {}


def get_user(chat_id):
    cid = str(chat_id)
    if cid not in users:
        users[cid] = {"name": None, "state": None}
    return users[cid]


def set_user(chat_id, **kwargs):
    get_user(chat_id)
    users[str(chat_id)].update(kwargs)


async def reply(chat_id, text, kb=None):
    await bot.send_message(chat_id=chat_id, text=text, attachments=kb)


@dp.message_created(Command("start"))
async def on_start_cmd(event: MessageCreated):
    cid = event.message.recipient.chat_id
    get_user(cid)
    await reply(cid, 
        "Привет! Я бот-помощник Натальи Тимошиной 👋\n\nВыбирайте:",
        MAIN_MENU
    )


@dp.message_callback()
async def on_callback(event: MessageCallback):
    cid = event.message.recipient.chat_id
    data = event.callback.payload or ""
    
    if data == "back_menu":
        await reply(cid, "Выбирайте:", MAIN_MENU)
        return
    
    if data == "menu_diag":
        await reply(cid, "Давайте проведём диагностику! Как вас зовут?")
        return
    
    if data == "menu_mat":
        await reply(cid, "Вот доступные материалы:\n\n1. 10 ошибок\n2. Ответ на «дорого»\n3. Шаблоны сообщений", KB_BACK)
        return
    
    if data == "menu_clients":
        await reply(cid, "Расскажите о вашей ситуации:", KB_BACK)
        return
    
    await reply(cid, f"Вы нажали: {data}", KB_BACK)


@dp.message_created()
async def on_text(event: MessageCreated):
    cid = event.message.recipient.chat_id
    text = event.message.body.text or ""
    u = get_user(cid)
    
    if u.get("state") == "wait_name":
        name = text.split()[0].capitalize()
        set_user(cid, name=name, state=None)
        await reply(cid, f"Приятно познакомиться, {name}! Что дальше?", MAIN_MENU)
        return
    
    if text.lower() in ("меню", "menu", "старт"):
        await reply(cid, "Выбирайте:", MAIN_MENU)
    else:
        await reply(cid, f"Вы написали: {text}")


async def main():
    logger.info("Бот запускается...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
