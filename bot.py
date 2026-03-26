"""
Бот-помощник Натальи Тимошиной — Max мессенджер
Упрощённая версия для тестирования
"""
import os
import logging
import asyncio

from maxapi import Bot, Dispatcher
from maxapi.types import MessageCreated, Command, MessageCallback, BotStarted

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("BOT_TOKEN")
bot = Bot(TOKEN)
dp = Dispatcher()


# ═══════════════════════════════════════
# КЛАВИАТУРЫ (словари — так работает maxapi)
# ═══════════════════════════════════════

def make_kb(buttons):
    """
    buttons: список строк, каждая строка — список кортежей (текст, payload)
    Пример: [[("Кнопка 1", "btn1")], [("Кнопка 2", "btn2")]]
    """
    rows = []
    for row in buttons:
        r = []
        for text, payload in row:
            r.append({"type": "callback", "text": text, "payload": payload})
        rows.append(r)
    return [{"type": "inline_keyboard", "payload": {"buttons": rows}}]


MAIN_MENU = make_kb([
    [("🔍 Разобрать мою ситуацию", "menu_diag")],
    [("📚 Бесплатные материалы для роста", "menu_mat")],
    [("📈 Хочу больше клиентов", "menu_clients")],
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
    [("Хочу уйти из салона на своё", "prob_exit")],
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
    [("Клиенты сами просят меня", "src_loyal")],
    [("Беру тех, от кого отказались", "src_left")],
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
    [("📋 Получить полный план", "go_site")],
    [("🔙 Вернуться в меню", "back_menu")],
])

KB_MATERIALS = make_kb([
    [("✅ 10 ошибок, из-за которых уходят клиенты", "mat_mistakes")],
    [("💬 Как ответить на «дорого»", "mat_expensive")],
    [("📝 Шаблоны сообщений для записи", "mat_templates")],
    [("🔙 Вернуться в меню", "back_menu")],
])

KB_AFTER_MAT = make_kb([
    [("🔍 Разобрать мою ситуацию", "menu_diag")],
    [("🔙 Вернуться в меню", "back_menu")],
])

KB_SITUATION = make_kb([
    [("Только начинаю, клиентов почти нет", "sit_beg")],
    [("Клиенты есть, но мало", "sit_unst")],
    [("Клиентов хватает, хочу больше", "sit_opt")],
])

KB_TRIED = make_kb([
    [("Не знаю с чего начать", "tried_no")],
    [("Пробовал(а), не сработало", "tried_fail")],
    [("Кое-что работает", "tried_some")],
])


# ═══════════════════════════════════════
# ТЕКСТЫ РЕЗУЛЬТАТОВ
# ═══════════════════════════════════════

RESULTS = {
    "salon-exit": (
        "📊 {name}, ваш разбор готов!\n\n"
        "Ваш сценарий: вы переросли салон.\n\n"
        "Вы работаете в салоне, но чувствуете — пора на своё. "
        "Это нормальный этап роста, и у вас есть для этого база.\n\n"
        "Что я вижу:\n"
        "→ У вас есть клиенты, которые идут именно к вам\n"
        "→ Без подготовки уход может обрушить доход на 2-3 месяца\n"
        "→ Нужен план: подушка, каналы привлечения, клиенты ДО увольнения\n\n"
        "В полном разборе — пошаговый план выхода с расчётами под ваш город."
    ),
    "salon-grow": (
        "📊 {name}, ваш разбор готов!\n\n"
        "Ваш сценарий: рост внутри салона.\n\n"
        "Салон даёт стабильность, но доход ограничен условиями.\n\n"
        "Что я вижу:\n"
        "→ Доход можно увеличить на 30-50% без смены места\n"
        "→ Ключ — стать незаменимым для салона\n"
        "→ Есть конкретные шаги для салонной модели\n\n"
        "В полном разборе — как увеличить процент и выстроить лояльность."
    ),
    "hybrid-exit": (
        "📊 {name}, ваш разбор готов!\n\n"
        "Ваш сценарий: переход на полную частную практику.\n\n"
        "Вы уже совмещаете — самое сложное позади.\n\n"
        "Что я вижу:\n"
        "→ У вас есть частные клиенты — это фундамент\n"
        "→ Их пока недостаточно для безопасного ухода\n"
        "→ Нужно довести поток до точки, когда салон необязателен\n\n"
        "В полном разборе — расчёт «точки безопасного выхода»."
    ),
    "hybrid-grow": (
        "📊 {name}, ваш разбор готов!\n\n"
        "Ваш сценарий: параллельное развитие.\n\n"
        "Совмещение — мудрая стратегия, но без системы можно разорваться.\n\n"
        "Что я вижу:\n"
        "→ Главное — привлекать частных клиентов без конфликта с салоном\n"
        "→ Частный поток можно увеличить без доп. часов\n"
        "→ Важно чётко разделить каналы\n\n"
        "В полном разборе — как этично развивать частную базу."
    ),
    "private-grow": (
        "📊 {name}, ваш разбор готов!\n\n"
        "Ваш сценарий: рост частной практики.\n\n"
        "Вы работаете на себя, но клиентов не хватает.\n\n"
        "Что я вижу:\n"
        "→ Мало источников клиентов\n"
        "→ Потенциал роста значительный\n"
        "→ Нужна система из нескольких каналов\n\n"
        "В полном разборе — какие каналы подключить и как поднять чек."
    ),
    "private-optimize": (
        "📊 {name}, ваш разбор готов!\n\n"
        "Ваш сценарий: оптимизация практики.\n\n"
        "У вас всё хорошо, вопрос — как расти дальше.\n\n"
        "Что я вижу:\n"
        "→ Вы работаете на максимуме времени\n"
        "→ Рост через чек, автоматизацию или масштабирование\n"
        "→ Есть точки, где вы недозарабатываете\n\n"
        "В полном разборе — где теряете деньги и как умно зарабатывать."
    ),
}


# ═══════════════════════════════════════
# ХРАНЕНИЕ ДАННЫХ ПОЛЬЗОВАТЕЛЕЙ (в памяти)
# ═══════════════════════════════════════

users = {}


def get_user(chat_id):
    cid = str(chat_id)
    if cid not in users:
        users[cid] = {
            "name": None,
            "state": None,
            "work_mode": None,
            "city": None,
            "clients": None,
            "problem": None,
            "sources": [],
            "situation": None,
        }
    return users[cid]


def set_user(chat_id, **kwargs):
    cid = str(chat_id)
    if cid not in users:
        get_user(cid)
    users[cid].update(kwargs)


# ═══════════════════════════════════════
# ЛОГИКА СЦЕНАРИЕВ
# ═══════════════════════════════════════

def determine_scenario(u):
    wm = u.get("work_mode", "")
    prob = u.get("problem", "")

    if wm == "salon":
        return "salon-exit" if prob == "prob_exit" else "salon-grow"
    elif wm == "hybrid":
        return "salon-exit" if prob == "prob_exit" else "hybrid-grow"
    elif wm == "private":
        if prob in ("prob_more", "prob_scale"):
            return "private-optimize"
        return "private-grow"
    return "private-grow"


# ═══════════════════════════════════════
# ОТПРАВКА СООБЩЕНИЙ
# ═══════════════════════════════════════

async def reply(chat_id, text, kb=None):
    await bot.send_message(chat_id=chat_id, text=text, attachments=kb)


# ═══════════════════════════════════════
# ОБРАБОТЧИКИ
# ═══════════════════════════════════════

@dp.bot_started()
async def on_start_btn(event: BotStarted):
    cid = str(event.chat_id)
    get_user(cid)
    await reply(cid,
        "Привет! Я — бот Натальи Тимошиной 👋\n\n"
        "Здесь можно разобрать свою ситуацию, получить полезные материалы "
        "и понять, как привлечь больше клиентов на массаж.\n\n"
        "Выбирайте:",
        MAIN_MENU
    )


@dp.message_created(Command("start"))
async def on_start_cmd(event: MessageCreated):
    cid = str(event.message.recipient.chat_id)
    get_user(cid)
    await reply(cid,
        "Привет! Я — бот Натальи Тимошиной 👋\n\n"
        "Здесь можно разобрать свою ситуацию, получить полезные материалы "
        "и понять, как привлечь больше клиентов на массаж.\n\n"
        "Выбирайте:",
        MAIN_MENU
    )


@dp.message_created()
async def on_text(event: MessageCreated):
    cid = str(event.message.recipient.chat_id)
    u = get_user(cid)
    text = (event.message.body.text or "").strip()

    if not text:
        return

    # Ждём имя
    if u.get("state") == "wait_name":
        name = text.split()[0].capitalize()
        set_user(cid, name=name, state="wait_wm")
        await reply(cid, f"{name}, расскажите — как вы сейчас работаете?", KB_WORK_MODE)
        return

    # Любой другой текст
    if text.lower() in ("меню", "menu", "старт"):
        set_user(cid, state=None)
        await reply(cid,
            "Выбирайте:",
            MAIN_MENU
        )


@dp.message_callback()
async def on_callback(event: MessageCallback):
    cid = str(event.message.recipient.chat_id)
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
        set_user(cid, state="wait_name")
        await reply(cid, "Отлично, давайте разберёмся!\n\nДля начала — как вас зовут? Напишите имя.")
        return

    if data == "menu_mat":
        await reply(cid, "Вот что у меня есть — выбирайте, что актуально:", KB_MATERIALS)
        return

    if data == "menu_clients":
        set_user(cid, state="cl_q1")
        await reply(cid,
            "Хорошо, давайте разберёмся, что вам подойдёт.\n\n"
            "Как бы вы описали свою ситуацию сейчас?",
            KB_SITUATION
        )
        return

    # ─── ДИАГНОСТИКА ───

    # Формат работы
    if data.startswith("wm_"):
        mode_map = {"wm_salon": "salon", "wm_hybrid": "hybrid", "wm_private": "private"}
        set_user(cid, work_mode=mode_map.get(data, "private"), state="wait_city")
        await reply(cid,
            "В каком городе работаете? Это важно — цены и конкуренция отличаются.",
            KB_CITY
        )
        return

    # Город
    if data.startswith("city_"):
        set_user(cid, city=data, state="wait_clients")
        wm = u.get("work_mode", "private")
        if wm == "salon":
            await reply(cid, "Сколько клиентов у вас в неделю в салоне?", KB_CLIENTS_SALON)
        elif wm == "hybrid":
            await reply(cid, "Сколько частных клиентов в неделю? Не считая салон.", KB_CLIENTS_HYBRID)
        else:
            await reply(cid, "Сколько клиентов у вас в неделю?", KB_CLIENTS_PRIVATE)
        return

    # Количество клиентов
    if data.startswith("cl_"):
        set_user(cid, clients=data, state="wait_problem")
        wm = u.get("work_mode", "private")
        if wm == "salon":
            await reply(cid, "Что сейчас беспокоит больше всего?", KB_PROBLEM_SALON)
        elif wm == "hybrid":
            await reply(cid, "Что сейчас беспокоит больше всего?", KB_PROBLEM_HYBRID)
        else:
            await reply(cid, "Что сейчас беспокоит больше всего?", KB_PROBLEM_PRIVATE)
        return

    # Проблема
    if data.startswith("prob_"):
        set_user(cid, problem=data, state="wait_sources")
        wm = u.get("work_mode", "private")
        if wm == "salon":
            await reply(cid, "Последний вопрос! Как клиенты попадают именно к вам?", KB_SOURCES_SALON)
        else:
            await reply(cid,
                "Последний вопрос! Откуда приходят клиенты? "
                "Выберите всё подходящее, потом нажмите «Готово».",
                KB_SOURCES_PRIVATE
            )
        return

    # Источники
    if data.startswith("src_"):
        if data == "src_done":
            pass  # Переходим к результату ниже
        else:
            wm = u.get("work_mode", "private")
            if wm == "salon":
                set_user(cid, sources=[data])
                # Для салона — сразу к результату
            else:
                sources = u.get("sources", [])
                if data not in sources:
                    sources.append(data)
                    set_user(cid, sources=sources)
                await reply(cid, "✓ Добавлено. Выберите ещё или нажмите «Готово».", KB_SOURCES_PRIVATE)
                return

        # Показываем результат
        u = get_user(cid)
        scenario = determine_scenario(u)
        result_text = RESULTS.get(scenario, RESULTS["private-grow"])
        set_user(cid, state=None)
        await reply(cid, result_text.format(name=name), KB_RESULT)
        return

    # Ссылка на сайт
    if data == "go_site":
        await reply(cid,
            "Переходите по ссылке для получения полного плана:\n"
            "👉 https://lp.massagestart.ru\n\n"
            "Там вы сможете пройти полную диагностику с расчётами.",
            KB_BACK
        )
        return

    # ─── МАТЕРИАЛЫ ───
    if data.startswith("mat_"):
        names = {
            "mat_mistakes": "10 ошибок, из-за которых уходят клиенты",
            "mat_expensive": "Как ответить на «дорого»",
            "mat_templates": "Шаблоны сообщений для записи",
        }
        mat = names.get(data, "Материал")
        await reply(cid,
            f"📎 «{mat}» — отправляю!\n\n"
            "[Файл будет добавлен после создания PDF-материалов]\n\n"
            "Кстати, если хотите понять, что в вашей ситуации сработает лучше — "
            "могу сделать быстрый разбор за 2 минуты.",
            KB_AFTER_MAT
        )
        return

    # ─── ХОЧУ БОЛЬШЕ КЛИЕНТОВ ───
    if data.startswith("sit_"):
        sit_map = {"sit_beg": "beginner", "sit_unst": "unstable", "sit_opt": "optimize"}
        set_user(cid, situation=sit_map.get(data, "unstable"), state="cl_q2")
        await reply(cid, "Пробовали что-то делать для привлечения клиентов?", KB_TRIED)
        return

    if data.startswith("tried_"):
        u = get_user(cid)
        sit = u.get("situation", "unstable")

        if sit == "beginner":
            text = (
                "Понимаю — когда не знаешь, за что хвататься, "
                "любой совет кажется абстрактным.\n\n"
                "Вам подойдёт курс «7 дней — 7 шагов к доходу на массаже». "
                "Каждый день — одно конкретное действие.\n\n"
                "Или начните с бесплатного разбора ситуации."
            )
        elif sit == "optimize":
            text = (
                "У вас уже рабочая система — здорово.\n\n"
                "На вашем уровне рост — это повышение чека, "
                "автоматизация или масштабирование.\n\n"
                "Лучше всего сработает персональная консультация."
            )
        else:
            text = (
                "Знакомая история — вроде стараешься, а результат не тот.\n\n"
                "Скорее всего, силы уходят не туда. "
                "Рекомендую начать с диагностики — "
                "я определю ваш сценарий и покажу, на чём сфокусироваться."
            )

        set_user(cid, state=None)
        await reply(cid, text, make_kb([
            [("🔍 Сделать разбор бесплатно", "menu_diag")],
            [("🔙 Вернуться в меню", "back_menu")],
        ]))
        return


# ═══════════════════════════════════════
# ЗАПУСК
# ═══════════════════════════════════════

async def main():
    logger.info("Бот запускается...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
