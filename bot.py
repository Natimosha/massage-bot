"""
Бот-помощник Натальи Тимошиной — Max мессенджер
Версия 3.1
"""

import os
import logging
import asyncio
from datetime import datetime


from maxapi import Bot, Dispatcher
from maxapi.types import MessageCreated, Command, MessageCallback, BotStarted
from maxapi.types import CallbackButton, LinkButton, ButtonsPayload, Attachment
from maxapi.types import InputMedia


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


TOKEN = os.environ.get("BOT_TOKEN")
bot = Bot(TOKEN)
dp = Dispatcher()


# ═══════════════════════════════════════════════════════════════
# НАСТРОЙКИ АДМИНИСТРАТОРА
# ═══════════════════════════════════════════════════════════════
ADMIN_CHAT_ID = 68198998  # ВАШ CHAT_ID (не user_id!)
CHANNEL_ID = -69954394920441  # ID канала для проверки подписки
CHANNEL_LINK = "https://max.ru/id780608560670_biz"  # ссылка на канал



# ═══════════════════════════════════════════════════════════════
# БЕНЧМАРКИ ЦЕН ПО ГОРОДАМ
# ═══════════════════════════════════════════════════════════════

BENCHMARKS = {
    "city_moscow": {"name": "Москва", "avg": 4000},
    "city_spb": {"name": "Санкт-Петербург", "avg": 3500},
    "city_million": {"name": "город-миллионник", "avg": 3000},
    "city_big": {"name": "крупный город", "avg": 2500},
    "city_medium": {"name": "средний город", "avg": 2000},
    "city_small": {"name": "небольшой город", "avg": 1500},
}

PRICE_MAP = {
    "price_1500": 1250, "price_2500": 2000, "price_3500": 3000,
    "price_5000": 4250, "price_more": 6000,
}

CLIENTS_MAP = {
    "cl_2": 1, "cl_5": 4, "cl_10": 8, "cl_15": 13, "cl_20": 18,
}



# ═══════════════════════════════════════════════════════════════
# КЛАВИАТУРЫ
# ═══════════════════════════════════════════════════════════════

def make_kb(buttons):
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


MAIN_MENU = make_kb([
    [("🔍 Разобрать мою ситуацию", "menu_diag")],
    [("📚 Бесплатные материалы для роста", "menu_mat")],
    [("🎁 Подарок за подписку", "menu_gift")],
    [("💰 Дополнительный доход массажиста", "menu_ewa")],
])

KB_WORK_MODE = make_kb([
    [("Только в салоне", "wm_salon")],
    [("Совмещаю салон и частную практику", "wm_hybrid")],
    [("Только частная практика", "wm_private")],
])

KB_CITY = make_kb([
    [("Москва", "city_moscow"), ("Санкт-Петербург", "city_spb")],
    [("Город-миллионник", "city_million"), ("Крупный город", "city_big")],
    [("Средний город", "city_medium"), ("Небольшой город", "city_small")],
])

KB_PRICE = make_kb([
    [("До 1 500₽", "price_1500"), ("1 500 – 2 500₽", "price_2500")],
    [("2 500 – 3 500₽", "price_3500"), ("3 500 – 5 000₽", "price_5000")],
    [("Больше 5 000₽", "price_more")],
])

KB_CLIENTS_SALON = make_kb([
    [("До 5", "cl_5"), ("5-10", "cl_10")],
    [("10-15", "cl_15"), ("Больше 15", "cl_20")],
])

KB_CLIENTS_HYBRID = make_kb([
    [("0-2", "cl_2"), ("3-5", "cl_5")],
    [("5-10", "cl_10"), ("Больше 10", "cl_15")],
])

KB_CLIENTS_PRIVATE = make_kb([
    [("До 5", "cl_5"), ("5-10", "cl_10")],
    [("10-15", "cl_15"), ("Больше 15", "cl_20")],
])

KB_PROBLEM_SALON = make_kb([
    [("Мало клиентов / пустые окна", "prob_few")],
    [("Низкий процент, хочу больше", "prob_low")],
    [("Хочу уйти из салона на своё дело", "prob_exit")],
    [("Клиенты не возвращаются", "prob_noreturn")],
])

KB_PROBLEM_HYBRID = make_kb([
    [("Хочу полностью уйти из салона", "prob_exit")],
    [("Хочу развивать частную практику", "prob_grow")],
    [("Не хватает частных клиентов", "prob_few")],
    [("Не знаю, как совмещать", "prob_conflict")],
])

KB_PROBLEM_PRIVATE = make_kb([
    [("Мало клиентов, пустые дни", "prob_few")],
    [("Хочу больше зарабатывать", "prob_more")],
    [("Нет стабильности", "prob_unstable")],
    [("Хочу масштабироваться", "prob_scale")],
])

KB_SOURCES_SALON = make_kb([
    [("Администратор записывает", "src_admin")],
    [("Клиенты сами просят записать ко мне", "src_loyal")],
    [("Беру тех, от кого отказались другие", "src_left")],
    [("По-разному", "src_mixed")],
])

KB_SOURCES_PRIVATE = make_kb([
    [("Сарафанное радио", "src_ref")],
    [("Соцсети", "src_social")],
    [("Площадки (Авито, Профи)", "src_plat")],
    [("Карты (Яндекс, 2ГИС)", "src_maps")],
    [("Нет своих каналов", "src_none")],
    [("Готово → результат", "src_done")],
])

KB_BACK = make_kb([
    [("🔙 Вернуться в меню", "back_menu")],
])

KB_RESULT = make_kb([
    [("📊 Пройти углублённую диагностику", "go_site")],
    [("🔙 Вернуться в меню", "back_menu")],
])

KB_EMAIL_SKIP = make_kb([
    [("Пропустить", "email_skip")],
])

# ── ПРАВКА 1: обновлённое меню материалов ──
KB_MATERIALS = make_kb([
    [("📎 Первый клиент → Постоянный клиент", "mat_client_path")],
    [("📎 Продающая упаковка профиля", "mat_packaging")],
    [("🔙 Вернуться в меню", "back_menu")],
])

KB_AFTER_MAT = make_kb([
    [("🔍 Разобрать мою ситуацию", "menu_diag")],
    [("🔙 Вернуться в меню", "back_menu")],
])


# ═══════════════════════════════════════════════════════════════
# EWA PRODUCT — клавиатуры
# ═══════════════════════════════════════════════════════════════

KB_EWA_INTEREST = make_kb([
    [("Расскажите подробнее", "ewa_more")],
    [("Не моё", "ewa_no")],
])

KB_EWA_ACTION = make_kb([
    [("Хочу узнать больше — свяжитесь со мной", "ewa_contact")],
    [("Хочу сначала посмотреть продукты", "ewa_products")],
    [("🔙 Вернуться в меню", "back_menu")],
])

KB_GIFT_SUBSCRIBE = make_kb([
    [("📢 Перейти в канал", CHANNEL_LINK, "link")],
    [("✅ Я подписался — проверить", "gift_check")],
    [("🔙 Вернуться в меню", "back_menu")],
])


# ═══════════════════════════════════════════════════════════════
# EWA PRODUCT — тексты (ПРАВКА 3: обновлённые)
# ═══════════════════════════════════════════════════════════════

EWA_HOOK = (
    "Ваши клиенты часто спрашивают у вас совета — что попить для кожи, "
    "для волос, для суставов, для энергии и настроения?\n\n"
    "Вы рекомендуете, они благодарят. Но что если на этих рекомендациях "
    "можно ещё и зарабатывать?\n\n"
    "Не впаривая, не навязывая — просто предлагая то, в чём вы уверены"
)

EWA_DETAILS = (
    "Ewa Product — российская компания, продукты для здоровья, красоты и биохакинга.\n\n"
    "Как это работает:\n"
    "▫️ Вы рекомендуете продукты своим клиентам\n"
    "▫️ Они покупают по вашей ссылке\n"
    "▫️ Вы получаете вознаграждение с каждой покупки\n"
    "▫️ Если кто-то тоже начинает рекомендовать — процент и с их продаж\n\n"
    "Почему это интересно именно сейчас:\n"
    "▫️ Компании 3 года — стадия активного роста\n"
    "▫️ Заходить на старте выгоднее, чем когда бренд уже всем знаком\n"
    "▫️ Не нужны вложения, аренда или найм\n\n"
    "Это не вместо массажа, а вместе — как дополнительный этаж к тому, что уже есть"
)

EWA_NO = "Ок, без проблем. Если передумаете — кнопка никуда не денется."

EWA_CONTACT = (
    "Отлично! Я передам вашу заявку Наталье — она свяжется с вами в ближайшее время"
)

EWA_PRODUCTS = (
    "Познакомиться с продукцией можно тут:\n"
    "👉 https://ewaproduct.com/shop?purchase_ref_id=363052"
)



# ═══════════════════════════════════════════════════════════════
# ХРАНЕНИЕ ДАННЫХ
# ═══════════════════════════════════════════════════════════════

users = {}

def get_user(chat_id):
    cid = str(chat_id)
    if cid not in users:
        users[cid] = {
            "name": None, "email": None, "state": None,
            "work_mode": None, "city": None, "price": None,
            "clients": None, "problem": None, "sources": [],
            "scenario": None,
        }
    return users[cid]

def set_user(chat_id, **kwargs):
    cid = str(chat_id)
    if cid not in users:
        get_user(cid)
    users[cid].update(kwargs)



# ═══════════════════════════════════════════════════════════════
# ЛОГИКА СЦЕНАРИЕВ
# ═══════════════════════════════════════════════════════════════

def determine_scenario(u):
    wm = u.get("work_mode", "")
    prob = u.get("problem", "")
    if wm == "salon":
        return "salon-exit" if prob == "prob_exit" else "salon-grow"
    elif wm == "hybrid":
        return "hybrid-exit" if prob == "prob_exit" else "hybrid-grow"
    elif wm == "private":
        if prob in ("prob_more", "prob_scale"):
            return "private-optimize"
        return "private-grow"
    return "private-grow"


def build_result_text(u):
    name = u.get("name") or ""
    scenario = u.get("scenario", "private-grow")
    city = u.get("city", "city_medium")
    price_key = u.get("price", "price_2500")

    bench = BENCHMARKS.get(city, BENCHMARKS["city_medium"])
    city_name = bench["name"]
    market_avg = bench["avg"]
    user_price = PRICE_MAP.get(price_key, 2000)
    clients_count = CLIENTS_MAP.get(u.get("clients", "cl_10"), 8)

    wm = u.get("work_mode", "private")
    if wm == "salon":
        monthly = int(user_price * clients_count * 4 * 0.4)
    else:
        monthly = int(user_price * clients_count * 4 * 0.85)

    monthly_fmt = f"{monthly:,}".replace(",", " ")

    if user_price < market_avg * 0.85:
        price_note = (
            f"→ Ваш чек (~{user_price}₽) ниже среднего по {city_name} ({market_avg}₽). "
            f"Потенциал: +{int((market_avg - user_price) * clients_count * 4)}₽/мес при повышении до рыночного"
        )
    elif user_price > market_avg * 1.15:
        price_note = (
            f"→ Ваш чек (~{user_price}₽) выше среднего по {city_name} ({market_avg}₽) — это сильная позиция"
        )
    else:
        price_note = (
            f"→ Ваш чек (~{user_price}₽) на уровне рынка для {city_name} ({market_avg}₽)"
        )

    scenarios = {
        "salon-exit": {
            "title": "вы переросли салон",
            "desc": (
                "Вы работаете в салоне, но чувствуете, что пора работать на себя.\n"
                "Это нормальный и закономерный этап роста, и у вас есть для этого база."
            ),
            "points": [
                "У вас есть клиенты, которые идут именно к вам, и это ваш актив",
                "Без подготовки уход из салона может обрушить доход на 2-3 месяца",
                "Нужен план: финансовая подушка, каналы привлечения, клиенты ДО увольнения",
            ],
            "full": (
                "В подробном разборе вы сможете получить пошаговый план выхода из салона\n"
                "с расчётами: сколько частных клиентов набрать до увольнения,\n"
                "где их взять, и как уйти без конфликта"
            ),
        },
        "salon-grow": {
            "title": "рост внутри салона",
            "desc": (
                "Вы решили развиваться в салоне — и это разумный путь.\n"
                "Но доход ограничен условиями."
            ),
            "points": [
                "Доход можно увеличить на 30-50% без смены места работы",
                "Ключ к этому — стать незаменимым: повысить возвращаемость клиентов",
                "Есть конкретные шаги для салонной модели",
            ],
            "full": (
                "В подробном разборе вы увидите, как увеличить процент, выстроить лояльность\n"
                "и создать позицию, при которой салон будет заинтересован вас удержать"
            ),
        },
        "hybrid-exit": {
            "title": "переход на полную частную практику",
            "desc": (
                "Вы уже совмещаете — самое сложное позади.\n"
                "Вопрос — когда безопасно уйти из салона."
            ),
            "points": [
                "У вас есть частные клиенты, и это ваш фундамент",
                "Но их пока недостаточно для безопасного ухода",
                "Нужно довести поток до точки, когда работа в салоне станет необязательной",
            ],
            "full": (
                "В подробном разборе вы получите расчёт вашей «точки безопасного выхода»,\n"
                "какие каналы добавить, и конкретный таймлайн (план по времени) перехода"
            ),
        },
        "hybrid-grow": {
            "title": "параллельное развитие",
            "desc": "Совмещение — это мудрая стратегия, но без системы вы рискуете разорваться.",
            "points": [
                "Главное — привлекать частных клиентов без конфликта с салоном",
                "Частный поток можно увеличить без дополнительных рабочих часов",
                "Важно чётко разделить каналы: салонные клиенты отдельно, свои отдельно",
            ],
            "full": (
                "В подробном разборе вы узнаете, как этично развивать частную базу,\n"
                "какие каналы привлечения клиентов хорошо работают в вашем городе,\n"
                "и как управлять двумя потоками"
            ),
        },
        "private-grow": {
            "title": "рост частной практики",
            "desc": (
                "Вы работаете на себя — это очень серьёзный шаг.\n"
                "Но клиентов пока не хватает."
            ),
            "points": [
                "Мало источников клиентов — если один просядет, просядет всё",
                "В вашем городе есть потенциал для роста",
                "Нужна система из нескольких каналов",
            ],
            "full": (
                "В подробном разборе вы увидите, какие каналы подключить именно в вашей ситуации,\n"
                "как поднять чек, и план выхода на стабильный доход"
            ),
        },
        "private-optimize": {
            "title": "оптимизация практики",
            "desc": (
                "У вас всё хорошо. Остаётся только вопрос, как расти дальше,\n"
                "когда есть всего одна пара рук?"
            ),
            "points": [
                "Вы работаете на максимуме времени",
                "Рост возможен — через повышение чека, автоматизацию или масштабирование",
                "Есть точки, где вы недозарабатываете, их можно «подтянуть»",
            ],
            "full": (
                "В подробном разборе я покажу вам, где именно вы теряете деньги,\n"
                "как перейти от «много работаю» к «умно зарабатываю»"
            ),
        },
    }

    s = scenarios.get(scenario, scenarios["private-grow"])
    points = "\n".join([f"→ {p}" for p in s["points"]])

    return (
        f"📊 {name}, ваш разбор готов!\n\n"
        f"Ваш сценарий: {s['title']}.\n\n"
        f"{s['desc']}\n\n"
        f"Ваши цифры:\n"
        f"→ Примерный доход сейчас: ~{monthly_fmt}₽/мес\n"
        f"{price_note}\n"
        f"→ Клиентов в неделю: ~{clients_count}\n\n"
        f"Что я вижу:\n{points}\n\n"
        f"{s['full']}"
    )



# ═══════════════════════════════════════════════════════════════
# ВСПОМОГАТЕЛЬНЫЕ
# ═══════════════════════════════════════════════════════════════

async def reply(chat_id, text, kb=None):
    await bot.send_message(chat_id=chat_id, text=text, attachments=kb)


async def check_subscription(user_id):
    """Проверяет, подписан ли пользователь на канал."""
    import aiohttp
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://platform-api.max.ru/chats/{CHANNEL_ID}/members"
            headers = {"Authorization": TOKEN}
            params = {"user_ids": str(user_id)}
            async with session.get(url, headers=headers, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    members = data.get("members", [])
                    return len(members) > 0
                return False
    except Exception as e:
        logger.error(f"Ошибка проверки подписки: {e}")
        return False


async def send_gift(cid):
    """Отправляет подарок (guide_03.pdf) без запроса email."""
    import aiohttp
    import tempfile

    await reply(cid,
        "📎 «Шаблоны визиток массажиста»\n\n"
        "5 готовых шаблонов визиток с текстами, советы по дизайну и печати.\n"
        "Внутри только то, что реально работает"
    )

    await asyncio.sleep(1)

    try:
        pdf_url = "https://raw.githubusercontent.com/Natimosha/massage-bot/main/guide_03.pdf"
        async with aiohttp.ClientSession() as session:
            async with session.get(pdf_url) as resp:
                if resp.status == 200:
                    pdf_data = await resp.read()
                    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                        tmp.write(pdf_data)
                        tmp_path = tmp.name
                    await bot.send_message(
                        chat_id=cid,
                        attachments=[InputMedia(path=tmp_path)]
                    )
                    import os
                    os.unlink(tmp_path)
                else:
                    await reply(cid, "Не удалось отправить файл. Напишите нам, и мы отправим вручную.")
    except Exception as e:
        logger.error(f"Ошибка отправки подарка: {e}")
        await reply(cid, "Не удалось отправить файл. Напишите нам, и мы отправим вручную.")

    await asyncio.sleep(1)

    await reply(cid,
        "Спасибо за подписку! В канале — разборы, шаблоны и конкретные шаги для роста дохода",
        KB_BACK
    )



# ═══════════════════════════════════════════════════════════════
# ОБРАБОТЧИКИ
# ═══════════════════════════════════════════════════════════════

START_MSG = (
    "Привет! Я — бот Натальи Тимошиной 👋\n\n"
    "Помогу разобрать вашу ситуацию, получить полезные материалы "
    "и понять, как привлечь больше клиентов на массаж.\n\n"
    "Выбирайте:"
)


@dp.bot_started()
async def on_start_btn(event: BotStarted):
    cid = event.chat_id
    get_user(cid)
    await reply(cid, START_MSG, MAIN_MENU)
    
    if ADMIN_CHAT_ID and ADMIN_CHAT_ID != int(cid):
        try:
            await bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=f"🆕 **Новый пользователь в боте!**\nID: `{cid}`"
            )
        except Exception as e:
            logger.warning(f"Не удалось отправить уведомление: {e}")


@dp.message_created(Command("start"))
async def on_start_cmd(event: MessageCreated):
    cid = event.message.recipient.chat_id
    get_user(cid)
    await reply(cid, START_MSG, MAIN_MENU)
    
    if ADMIN_CHAT_ID and ADMIN_CHAT_ID != int(cid):
        try:
            await bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=f"🆕 **Новый пользователь в боте!**\nID: `{cid}`"
            )
        except Exception as e:
            logger.warning(f"Не удалось отправить уведомление: {e}")


@dp.message_created()
async def on_text(event: MessageCreated):
    cid = event.message.recipient.chat_id
    u = get_user(cid)
    text = (event.message.body.text or "").strip()
    
    if not text:
        return
    
    # ⭐ ОБРАБОТКА КОМАНДЫ /checksub (отладка) ⭐
    if text.startswith("/checksub"):
        if int(cid) != ADMIN_CHAT_ID:
            await reply(cid, "⛔ Нет прав")
            return
        import aiohttp
        # Проверяем себя или указанный user_id
        parts = text.split()
        check_id = parts[1] if len(parts) > 1 else cid
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://platform-api.max.ru/chats/{CHANNEL_ID}/members"
                headers = {"Authorization": TOKEN}
                params = {"user_ids": str(check_id)}
                async with session.get(url, headers=headers, params=params) as resp:
                    status = resp.status
                    raw = await resp.text()
                    await reply(cid,
                        f"🔍 **Отладка проверки подписки**\n\n"
                        f"Channel ID: `{CHANNEL_ID}`\n"
                        f"User ID: `{check_id}`\n"
                        f"HTTP status: {status}\n"
                        f"Ответ API:\n```\n{raw[:1500]}\n```"
                    )
        except Exception as e:
            await reply(cid, f"❌ Ошибка: {e}")
        return

    # ⭐ ОБРАБОТКА КОМАНДЫ /chats ⭐
    if text.startswith("/chats"):
        if int(cid) != ADMIN_CHAT_ID:
            await reply(cid, "⛔ Нет прав")
            return
        import aiohttp
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://platform-api.max.ru/chats"
                headers = {"Authorization": TOKEN}
                async with session.get(url, headers=headers) as resp:
                    data = await resp.json()
                    chats = data.get("chats", [])
                    if not chats:
                        await reply(cid, "📭 Бот не состоит ни в одном чате/канале.")
                        return
                    result = "📋 **Чаты/каналы бота:**\n\n"
                    for chat in chats:
                        result += (
                            f"▫️ {chat.get('title', 'Без названия')}\n"
                            f"   ID: `{chat.get('chat_id')}`\n"
                            f"   Тип: {chat.get('type', '?')}\n\n"
                        )
                    await reply(cid, result)
        except Exception as e:
            await reply(cid, f"❌ Ошибка: {e}")
        return

    # ⭐ ОБРАБОТКА КОМАНДЫ /stats ⭐
    if text.startswith("/stats"):
        if int(cid) != ADMIN_CHAT_ID:
            await reply(cid, "⛔ Нет прав")
            return
        total_users = len(users)
        users_with_name = sum(1 for u in users.values() if u.get("name"))
        users_with_email = sum(1 for u in users.values() if u.get("email"))
        completed_diag = sum(1 for u in users.values() if u.get("scenario"))
        stats_text = (
            f"📊 **Статистика бота**\n\n"
            f"👥 Всего пользователей: {total_users}\n"
            f"📝 Представились: {users_with_name}\n"
            f"📧 Оставили email: {users_with_email}\n"
            f"✅ Прошли диагностику: {completed_diag}"
        )
        await reply(cid, stats_text)
        return

    # ⭐ ОБРАБОТКА КОМАНДЫ /last ⭐
    if text.startswith("/last"):
        if int(cid) != ADMIN_CHAT_ID:
            await reply(cid, "⛔ Нет прав")
            return
        try:
            with open("вопросы.txt", "r", encoding="utf-8") as f:
                content = f.read()
            blocks = content.split("="*60)
            last_blocks = blocks[-5:]
            if len(last_blocks) < 2:
                await reply(cid, "📭 Вопросов пока нет.")
                return
            result = "📋 **Последние вопросы:**\n\n"
            for block in last_blocks:
                if block.strip():
                    lines = block.strip().split("\n")
                    for line in lines:
                        if "Имя:" in line or "Вопрос:" in line:
                            result += f"{line}\n"
                    result += "-"*30 + "\n"
            await reply(cid, result)
        except FileNotFoundError:
            await reply(cid, "📭 Вопросов пока нет.")
        except Exception as e:
            await reply(cid, f"❌ Ошибка: {e}")
        return

    # ⭐ ОБРАБОТКА КОМАНДЫ /reply ⭐
    if text.startswith("/reply"):
        # Только админ может использовать /reply
        if int(cid) != ADMIN_CHAT_ID:
            await reply(cid, "⛔ Нет прав")
            return
        
        parts = text.split(maxsplit=2)
        if len(parts) < 3:
            await reply(cid, "❌ Формат: /reply ID_пользователя Текст ответа\n\nПример: /reply 232975199 Здравствуйте!")
            return
        
        try:
            user_id = int(parts[1])
            reply_text = parts[2]
            
            # Отправляем ответ пользователю
            await bot.send_message(
                chat_id=user_id,
                text=f"💬 **Ответ от Натальи:**\n\n{reply_text}\n\n---\nЕсли у вас есть ещё вопросы, я всегда на связи! 🤗"
            )
            
            # Подтверждение админу
            await reply(cid, f"✅ Ответ отправлен пользователю `{user_id}`")
            
            # Логируем
            with open("ответы_админа.txt", "a", encoding="utf-8") as f:
                f.write(f"{datetime.now()} | Ответ пользователю {user_id}: {reply_text}\n")
                
        except ValueError:
            await reply(cid, "❌ Ошибка: ID должен быть числом")
        except Exception as e:
            await reply(cid, f"❌ Ошибка при отправке: {e}")
        return
    
    state = u.get("state")

    # Ждём имя
    if state == "wait_name":
        name = text.split()[0].capitalize()
        set_user(cid, name=name, state="wait_wm")
        await reply(cid, f"{name}, расскажите — как вы сейчас работаете?", KB_WORK_MODE)
        
        if ADMIN_CHAT_ID and ADMIN_CHAT_ID != int(cid):
            try:
                await bot.send_message(
                    chat_id=ADMIN_CHAT_ID,
                    text=f"👤 Пользователь **{name}** (ID: `{cid}`) проходит диагностику."
                )
            except Exception as e:
                logger.warning(f"Не удалось отправить уведомление: {e}")
        return

    # Ждём email
    if state == "wait_email":
        if "@" in text and "." in text:
            set_user(cid, email=text.strip(), state="send_material")
            await reply(cid, "Спасибо! Сохранила ✉️ Отправляю материал.")
            logger.info(f"Email collected: {text.strip()} from {cid}")
            await asyncio.sleep(0.7)
            u = get_user(cid)
            mat_key = u.get("pending_material", "")
            await send_material(cid, mat_key)
            
            if ADMIN_CHAT_ID and ADMIN_CHAT_ID != int(cid):
                user_name = u.get("name") or "Неизвестный"
                try:
                    await bot.send_message(
                        chat_id=ADMIN_CHAT_ID,
                        text=f"📧 Пользователь **{user_name}** (ID: `{cid}`) оставил email:\n`{text.strip()}`"
                    )
                except Exception as e:
                    logger.warning(f"Не удалось отправить уведомление: {e}")
        else:
            await reply(cid,
                "Хм, не очень похоже на email. Попробуйте ещё раз или нажмите «Пропустить».",
                KB_EMAIL_SKIP
            )
        return

    # Команды меню
    if text.lower() in ("меню", "menu", "старт"):
        set_user(cid, state=None)
        await reply(cid, "Выбирайте:", MAIN_MENU)
        return
    
    # ═══════════════════════════════════════════════════════════════
    # ЛЮБОЙ ДРУГОЙ ТЕКСТ - ВОПРОС ПОЛЬЗОВАТЕЛЯ
    # ═══════════════════════════════════════════════════════════════
    
    user_name = u.get("name") or "Не представился"
    user_email = u.get("email") or "email не указан"
    
    # Сохраняем в файл
    with open("вопросы.txt", "a", encoding="utf-8") as f:
        f.write(f"{'='*60}\n")
        f.write(f"Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Имя: {user_name}\n")
        f.write(f"ID: {cid}\n")
        f.write(f"Email: {user_email}\n")
        f.write(f"Вопрос: {text}\n")
        f.write(f"{'='*60}\n\n")
    
    # Отправляем уведомление админу
    if ADMIN_CHAT_ID and ADMIN_CHAT_ID != int(cid):
        try:
            await bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=f"❓ **Новый вопрос от {user_name}**\n\n"
                     f"👤 Имя: {user_name}\n"
                     f"🆔 ID: `{cid}`\n"
                     f"📧 Email: {user_email}\n\n"
                     f"💬 **Вопрос:**\n{text}\n\n"
                     f"📝 Чтобы ответить, используйте команду:\n`/reply {cid} Текст ответа`"
            )
        except Exception as e:
            logger.warning(f"Не удалось отправить уведомление: {e}")
    
    # Отвечаем пользователю
    await reply(
        cid,
        "🙏 Спасибо за вопрос! Я передам его Наталье, и она свяжется с вами в ближайшее время",
        MAIN_MENU
    )
    return


# ═══════════════════════════════════════════════════════════════
# ПРАВКА 1: ОТПРАВКА PDF ВМЕСТО ЗАГЛУШЕК
# ═══════════════════════════════════════════════════════════════

async def send_material(cid, mat_key):
    """Отправить PDF-материал после email или пропуска."""

    materials = {
        "mat_client_path": {
            "name": "Первый клиент → Постоянный клиент",
            "url": "https://raw.githubusercontent.com/Natimosha/massage-bot/main/guide_01.pdf",
            "desc": (
                "Внутри — готовые фразы для каждого этапа общения с клиентом:\n"
                "от первого «сколько стоит?» до момента, когда клиент записывается сам.\n\n"
                "Всё из реальной практики, ничего выдуманного"
            ),
        },
        "mat_packaging": {
            "name": "Продающая упаковка профиля",
            "url": "https://raw.githubusercontent.com/Natimosha/massage-bot/main/guide_02.pdf",
            "desc": (
                "Чек-лист для аудита вашего профиля + примеры, которые работают.\n"
                "Прайс, описание, фото, шапка — всё, что видит клиент до того, как решит написать.\n\n"
                "Проверьте себя за 10 минут"
            ),
        },
    }

    mat = materials.get(mat_key)
    set_user(cid, state=None)

    if not mat:
        await reply(cid, "Материал не найден. Попробуйте выбрать из меню.", MAIN_MENU)
        return

    # 1. Описание материала
    await reply(cid, f"📎 «{mat['name']}»\n\n{mat['desc']}")

    await asyncio.sleep(1)

    # 2. Скачиваем PDF с GitHub и отправляем
    import aiohttp
    import tempfile

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(mat["url"]) as resp:
                if resp.status == 200:
                    pdf_data = await resp.read()
                    # Сохраняем во временный файл
                    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                        tmp.write(pdf_data)
                        tmp_path = tmp.name
                    # Отправляем через InputMedia
                    await bot.send_message(
                        chat_id=cid,
                        attachments=[InputMedia(path=tmp_path)]
                    )
                    # Удаляем временный файл
                    import os
                    os.unlink(tmp_path)
                else:
                    logger.error(f"Ошибка скачивания PDF: HTTP {resp.status}")
                    await reply(cid, "Не удалось отправить файл. Напишите нам, и мы отправим вручную.")
    except Exception as e:
        logger.error(f"Ошибка отправки PDF {mat['url']}: {e}")
        await reply(cid, "Не удалось отправить файл. Напишите нам, и мы отправим вручную.")

    await asyncio.sleep(1)

    # 3. Мостик на диагностику
    await reply(cid,
        "Кстати, если хотите понять, что в вашей ситуации сработает лучше —\n"
        "могу сделать быстрый разбор за 2 минуты",
        KB_AFTER_MAT
    )



@dp.message_callback()
async def on_callback(event: MessageCallback):
    cid = event.message.recipient.chat_id
    data = event.callback.payload or ""
    u = get_user(cid)
    name = u.get("name") or ""

    logger.info(f"Callback {cid}: {data}")

    # ─── Назад в меню ───
    if data == "back_menu":
        set_user(cid, state=None)
        await reply(cid, "Выбирайте:", MAIN_MENU)
        return

    # ─── ГЛАВНОЕ МЕНЮ ───
    if data == "menu_diag":
        set_user(cid, state="wait_name", sources=[])
        await reply(cid, "Отлично, давайте разберёмся!\n\nДля начала — как вас зовут? Напишите имя.")
        return

    if data == "menu_mat":
        await reply(cid, "Вот что у меня есть — выбирайте, что актуально:", KB_MATERIALS)
        return

    if data == "menu_ewa":
        await reply(cid, EWA_HOOK, KB_EWA_INTEREST)
        return

    # ═══════════════════════════════════════
    # ПОДАРОК ЗА ПОДПИСКУ
    # ═══════════════════════════════════════

    if data == "menu_gift":
        # Сразу проверяем подписку
        is_subscribed = await check_subscription(cid)
        if is_subscribed:
            await send_gift(cid)
        else:
            await reply(cid,
                "Этот подарок — для подписчиков канала 🎁\n\n"
                "Подпишитесь на канал, а потом нажмите «Я подписался — проверить».\n"
                "Я проверю и сразу отправлю PDF",
                KB_GIFT_SUBSCRIBE
            )
        return

    if data == "gift_check":
        is_subscribed = await check_subscription(cid)
        if is_subscribed:
            await send_gift(cid)
        else:
            await reply(cid,
                "Пока не вижу вас в подписчиках. Подпишитесь на канал и попробуйте ещё раз",
                KB_GIFT_SUBSCRIBE
            )
        return

    # ═══════════════════════════════════════
    # EWA PRODUCT
    # ═══════════════════════════════════════

    if data == "ewa_more":
        await reply(cid, EWA_DETAILS, KB_EWA_ACTION)
        return

    if data == "ewa_no":
        await reply(cid, EWA_NO, MAIN_MENU)
        return

    if data == "ewa_contact":
        await reply(cid, EWA_CONTACT, KB_BACK)
        logger.info(f"Ewa contact request from {cid}")
        # Уведомление админу
        if ADMIN_CHAT_ID and ADMIN_CHAT_ID != int(cid):
            user_name = u.get("name") or "Не представился"
            try:
                await bot.send_message(
                    chat_id=ADMIN_CHAT_ID,
                    text=f"💰 **Заявка на Ewa Product!**\n\n"
                         f"👤 Имя: {user_name}\n"
                         f"🆔 ID: `{cid}`\n\n"
                         f"Человек хочет узнать больше. Свяжитесь с ним:\n"
                         f"`/reply {cid} Текст ответа`"
                )
            except Exception as e:
                logger.warning(f"Не удалось отправить уведомление: {e}")
        return

    if data == "ewa_products":
        await reply(cid, EWA_PRODUCTS, KB_BACK)
        return

    # ═══════════════════════════════════════
    # ДИАГНОСТИКА
    # ═══════════════════════════════════════

    if data.startswith("wm_"):
        mode_map = {"wm_salon": "salon", "wm_hybrid": "hybrid", "wm_private": "private"}
        set_user(cid, work_mode=mode_map.get(data, "private"), state="wait_city")
        await reply(cid,
            "В каком городе работаете? Это важно, т. к. уровень цен и конкуренции зависит от города.",
            KB_CITY
        )
        return

    if data.startswith("city_"):
        set_user(cid, city=data, state="wait_price")
        wm = u.get("work_mode", "private")
        if wm == "salon":
            await reply(cid, "Какой средний чек за сеанс в вашем салоне?", KB_PRICE)
        else:
            await reply(cid, "Сколько стоит ваш сеанс массажа?", KB_PRICE)
        return

    if data.startswith("price_"):
        set_user(cid, price=data, state="wait_clients")
        wm = u.get("work_mode", "private")
        if wm == "salon":
            await reply(cid, "Сколько клиентов у вас в неделю в салоне?", KB_CLIENTS_SALON)
        elif wm == "hybrid":
            await reply(cid, "Сколько частных, лично ваших клиентов в неделю? Не считая салон.", KB_CLIENTS_HYBRID)
        else:
            await reply(cid, "Сколько клиентов у вас в неделю?", KB_CLIENTS_PRIVATE)
        return

    if data.startswith("cl_") and u.get("state") == "wait_clients":
        set_user(cid, clients=data, state="wait_problem")
        wm = u.get("work_mode", "private")
        if wm == "salon":
            await reply(cid, "Что сейчас беспокоит больше всего?", KB_PROBLEM_SALON)
        elif wm == "hybrid":
            await reply(cid, "Что сейчас беспокоит больше всего?", KB_PROBLEM_HYBRID)
        else:
            await reply(cid, "Что сейчас беспокоит больше всего?", KB_PROBLEM_PRIVATE)
        return

    if data.startswith("prob_"):
        set_user(cid, problem=data, state="wait_sources")
        wm = u.get("work_mode", "private")
        if wm == "salon":
            await reply(cid, "Последний вопрос! Как клиенты попадают именно к вам?", KB_SOURCES_SALON)
        else:
            await reply(cid,
                "Последний вопрос! Откуда приходят клиенты?\n"
                "Выберите всё подходящее, потом нажмите «Готово».",
                KB_SOURCES_PRIVATE
            )
        return

    if data.startswith("src_"):
        if data == "src_done":
            pass
        else:
            wm = u.get("work_mode", "private")
            if wm == "salon":
                set_user(cid, sources=[data])
            else:
                sources = u.get("sources", [])
                if data not in sources:
                    sources.append(data)
                    set_user(cid, sources=sources)
                await reply(cid, "✓ Добавлено. Выберите ещё или нажмите «Готово».", KB_SOURCES_PRIVATE)
                return

        u = get_user(cid)
        scenario = determine_scenario(u)
        set_user(cid, scenario=scenario, state=None)
        result_text = build_result_text(u)
        await reply(cid, result_text, KB_RESULT)
        
        if ADMIN_CHAT_ID and ADMIN_CHAT_ID != int(cid):
            user_name = u.get("name") or "Неизвестный"
            try:
                await bot.send_message(
                    chat_id=ADMIN_CHAT_ID,
                    text=f"✅ Пользователь **{user_name}** (ID: `{cid}`) завершил диагностику!\nСценарий: {scenario}"
                )
            except Exception as e:
                logger.warning(f"Не удалось отправить уведомление: {e}")
        return

    # ── ПРАВКА 4: ссылка на Навигатор роста ──
    if data == "go_site":
        await reply(cid,
            "На сайте есть расширенная диагностика — бесплатная.\n"
            "Она глубже, чем здесь: покажет вашу воронку клиентов, "
            "экономику и точки, где вы теряете деньги.\n\n"
            "А если захотите — в конце можно получить персональный "
            "PDF-план с пошаговыми действиями на 30 дней (990₽).\n\n"
            "👉 https://lp.massagestart.ru/test-navigator",
            KB_BACK
        )
        return

    # ═══════════════════════════════════════
    # БЕСПЛАТНЫЕ МАТЕРИАЛЫ (с email)
    # ═══════════════════════════════════════

    if data.startswith("mat_"):
        set_user(cid, pending_material=data, state="wait_email")
        await reply(cid,
            "📩 Чтобы получить наш полезный материал, напишите ваш email —\n"
            "отправлю на почту, чтобы точно не потерялся.\n\n"
            "Или нажмите «Пропустить» — отправлю прямо сюда.",
            KB_EMAIL_SKIP
        )
        return

    if data == "email_skip":
        u = get_user(cid)
        mat_key = u.get("pending_material", "")
        await send_material(cid, mat_key)
        return


# ═══════════════════════════════════════════════════════════════
# КОМАНДЫ АДМИНИСТРАТОРА
# ═══════════════════════════════════════════════════════════════

@dp.message_created(Command("reply"))
async def reply_to_user(event: MessageCreated):
    """Отправляет ответ конкретному пользователю. Использование: /reply 123456789 Текст ответа"""
    cid = event.message.recipient.chat_id
    
    if ADMIN_CHAT_ID and int(cid) != ADMIN_CHAT_ID:
        await reply(cid, "⛔ У вас нет прав для этой команды.")
        return
    
    text = (event.message.body.text or "").strip()
    parts = text.split(maxsplit=2)
    
    if len(parts) < 3:
        await reply(cid, "❌ Формат команды:\n/reply ID_пользователя Текст ответа\n\nПример: /reply 123456789 Здравствуйте!")
        return
    
    try:
        user_id = int(parts[1])
        reply_text = parts[2]
        
        await bot.send_message(
            chat_id=user_id,
            text=f"💬 **Ответ от Натальи:**\n\n{reply_text}\n\n---\nЕсли у вас есть ещё вопросы, я всегда на связи! 🤗"
        )
        
        await reply(cid, f"✅ Ответ успешно отправлен пользователю `{user_id}`\n\n📤 Текст ответа:\n{reply_text}")
        
        with open("ответы_админа.txt", "a", encoding="utf-8") as f:
            f.write(f"{'='*60}\n")
            f.write(f"Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Пользователю ID: {user_id}\n")
            f.write(f"Ответ: {reply_text}\n")
            f.write(f"{'='*60}\n\n")
            
    except ValueError:
        await reply(cid, "❌ Ошибка: ID пользователя должен быть числом.\nПример: /reply 123456789 Текст ответа")
    except Exception as e:
        await reply(cid, f"❌ Ошибка при отправке: {str(e)}")


@dp.message_created(Command("stats"))
async def show_stats(event: MessageCreated):
    """Показывает статистику бота"""
    cid = event.message.recipient.chat_id
    
    if ADMIN_CHAT_ID and int(cid) != ADMIN_CHAT_ID:
        await reply(cid, "⛔ У вас нет прав для этой команды.")
        return
    
    total_users = len(users)
    users_with_name = sum(1 for u in users.values() if u.get("name"))
    users_with_email = sum(1 for u in users.values() if u.get("email"))
    completed_diag = sum(1 for u in users.values() if u.get("scenario"))
    
    stats_text = (
        f"📊 **Статистика бота**\n\n"
        f"👥 Всего пользователей: {total_users}\n"
        f"📝 Представились: {users_with_name}\n"
        f"📧 Оставили email: {users_with_email}\n"
        f"✅ Прошли диагностику: {completed_diag}"
    )
    
    await reply(cid, stats_text)


@dp.message_created(Command("last"))
async def show_last_questions(event: MessageCreated):
    """Показывает последние 5 вопросов"""
    cid = event.message.recipient.chat_id
    
    if ADMIN_CHAT_ID and int(cid) != ADMIN_CHAT_ID:
        await reply(cid, "⛔ У вас нет прав для этой команды.")
        return
    
    try:
        with open("вопросы.txt", "r", encoding="utf-8") as f:
            content = f.read()
        
        blocks = content.split("="*60)
        last_blocks = blocks[-5:]
        
        if len(last_blocks) < 2:
            await reply(cid, "📭 Вопросов пока нет.")
            return
        
        result = "📋 **Последние вопросы:**\n\n"
        for block in last_blocks:
            if block.strip():
                lines = block.strip().split("\n")
                for line in lines:
                    if "Имя:" in line or "Вопрос:" in line:
                        result += f"{line}\n"
                result += "-"*30 + "\n"
        
        await reply(cid, result)
        
    except FileNotFoundError:
        await reply(cid, "📭 Файл с вопросами еще не создан.")
    except Exception as e:
        await reply(cid, f"❌ Ошибка: {e}")


# ═══════════════════════════════════════════════════════════════
# ЗАПУСК
# ═══════════════════════════════════════════════════════════════

async def main():
    logger.info("Бот запускается...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
