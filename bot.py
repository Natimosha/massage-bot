"""
Бот-помощник Натальи Тимошиной — Max мессенджер
Полная версия
"""
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


# ═══════════════════════════════════════════════════════════════
# ФУНКЦИЯ СОЗДАНИЯ КЛАВИАТУР
# ═══════════════════════════════════════════════════════════════

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


# ═══════════════════════════════════════════════════════════════
# ВСЕ КЛАВИАТУРЫ
# ═══════════════════════════════════════════════════════════════

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


# ═══════════════════════════════════════════════════════════════
# ВСЕ ТЕКСТЫ
# ═══════════════════════════════════════════════════════════════

START_MSG = """Привет! Я — бот Натальи Тимошиной 👋

Здесь можно разобрать свою ситуацию, получить полезные материалы 
и понять, как привлечь больше клиентов на массаж.

Выбирайте:"""

DIAG_Q1 = "Отлично, давайте разберёмся!\n\nДля начала — как вас зовут? Напишите имя."

DIAG_Q2 = "{name}, расскажите — как вы сейчас работаете?"

DIAG_Q3 = "В каком городе работаете? Это важно для расчётов — цены и конкуренция сильно отличаются."

DIAG_Q4_SALON = "Сколько примерно клиентов у вас в неделю в салоне?"
DIAG_Q4_HYBRID = "Сколько примерно частных клиентов у вас в неделю? Не считая салон."
DIAG_Q4_PRIVATE = "Сколько клиентов у вас в неделю?"

DIAG_Q5 = "Что сейчас беспокоит больше всего?"

DIAG_Q6_SALON = "Последний вопрос! Как клиенты попадают именно к вам?"
DIAG_Q6_PRIVATE = """Последний вопрос! Откуда к вам сейчас приходят клиенты? 
Выберите всё, что подходит, потом нажмите «Готово»."""

MATERIALS_INTRO = "Вот что у меня есть для вас — выбирайте, что актуально:"

MATERIAL_SENT = """Готово, держите! 📎

Кстати, если хотите понять, что в вашей ситуации сработает лучше всего — 
могу сделать быстрый разбор. Это займёт 2 минуты."""

MORE_CLIENTS_Q1 = """Хорошо, давайте разберёмся, что вам подойдёт. Пара вопросов:

Как бы вы описали свою ситуацию сейчас?"""

MORE_CLIENTS_Q2 = "Пробовали что-то делать для привлечения клиентов?"

PRODUCT_RECS = {
    "beginner": """Понимаю — когда не знаешь, за что хвататься, 
любой совет кажется абстрактным.

Вам подойдёт курс «7 дней — 7 шагов к доходу на массаже». 
Там всё разложено по дням: что делать в первую очередь, 
где искать клиентов, как назначить цену.

Или можно начать с бесплатного — 
сделать разбор вашей ситуации, и я подскажу первые 3 шага.""",
    
    "unstable": """Знакомая история — вроде что-то делаешь, но результат не тот.

Скорее всего, проблема не в усилиях, а в том, что силы уходят не туда. 
У вас конкретная ситуация, и нужен конкретный разбор.

Рекомендую начать с диагностики — я определю ваш сценарий 
и покажу, на чём сфокусироваться. 
А полный план с расчётами — в персональном PDF-отчёте.""",
    
    "optimize": """О, у вас уже рабочая система — это здорово.

На вашем уровне рост — это не «больше клиентов», 
а «больше дохода с тех же усилий»: 
повышение чека, автоматизация, масштабирование.

Тут лучше всего работает индивидуальный разбор. 
Могу предложить персональную консультацию — 
посмотрим вашу экономику и найдём конкретные точки роста."""
}

RESULTS = {
    "salon-exit": """📊 {name}, ваш разбор готов!

Ваш сценарий: вы переросли салон.

Вы работаете в салоне, но чувствуете — пора на своё. 
Это нормальный этап роста, и у вас есть для этого база. 
Но уходить «в пустоту» опасно.

Что я вижу:
→ У вас уже есть клиенты, которые идут именно к вам — это ваш актив
→ Но без подготовки уход может обрушить доход на 2-3 месяца
→ Нужен чёткий план: финансовая подушка, каналы привлечения, 
первые частные клиенты ДО увольнения

В полном разборе — пошаговый план выхода из салона 
с расчётами под ваш город и ситуацию.""",
    
    "salon-grow": """📊 {name}, ваш разбор готов!

Ваш сценарий: рост внутри салона.

Вы решили развиваться в салоне — и это разумный путь. 
Салон даёт стабильность и поток, но ваш доход ограничен тем, 
как выстроены отношения с руководством и клиентами.

Что я вижу:
→ Ваш доход можно увеличить на 30-50% без смены места работы
→ Ключ — стать незаменимым: повысить возвращаемость клиентов 
и создать аргументы для пересмотра условий
→ Есть конкретные шаги, которые работают именно в салонной модели

В полном разборе — как увеличить процент, выстроить лояльность 
и создать позицию, при которой салон заинтересован вас удержать.""",
    
    "hybrid-exit": """📊 {name}, ваш разбор готов!

Ваш сценарий: переход на полную частную практику.

Вы уже совмещаете — значит, самое сложное позади: 
вы умеете привлекать клиентов. Теперь вопрос — 
когда безопасно отпустить салон.

Что я вижу:
→ У вас есть частные клиенты — это фундамент
→ Но их пока недостаточно, чтобы уйти без просадки в доходе
→ Нужно довести частный поток до точки, 
когда салон станет необязательным

В полном разборе — расчёт вашей «точки безопасного выхода», 
какие каналы добавить, и конкретный таймлайн перехода.""",
    
    "hybrid-grow": """📊 {name}, ваш разбор готов!

Ваш сценарий: параллельное развитие.

Совмещение — мудрая стратегия: салон даёт стабильность, 
частная практика — рост. Но без системы 
вы рискуете разорваться между двумя фронтами.

Что я вижу:
→ Главный вызов — привлекать частных клиентов без конфликта с салоном
→ Ваш частный поток можно увеличить без дополнительных рабочих часов
→ Важно чётко разделить каналы: салонные клиенты отдельно, свои отдельно

В полном разборе — как этично развивать частную базу, 
какие каналы использовать в вашем городе, 
и как управлять двумя потоками без хаоса.""",
    
    "private-grow": """📊 {name}, ваш разбор готов!

Ваш сценарий: рост частной практики.

Вы работаете на себя — это уже серьёзный шаг. 
Но сейчас доход нестабильный, и клиентов не хватает.

Что я вижу:
→ У вас мало источников клиентов — если один просядет, просядет всё
→ Потенциал роста значительный: в вашем городе средний чек выше
→ Нужна система: несколько каналов, 
которые работают параллельно и дают стабильный поток

В полном разборе — какие каналы подключить именно в вашей ситуации, 
как поднять чек без потери клиентов, 
и пошаговый план выхода на стабильный доход.""",
    
    "private-optimize": """📊 {name}, ваш разбор готов!

Ваш сценарий: оптимизация работающей практики.

У вас уже всё хорошо — клиенты есть, доход стабильный. 
Вопрос — как расти дальше, когда «одна пара рук» становится потолком.

Что я вижу:
→ Вы работаете на максимуме своего времени
→ Следующий рост — через повышение чека, автоматизацию или масштабирование
→ Есть конкретные точки, где вы недозарабатываете

В полном разборе — где именно вы теряете деньги, 
как перейти от «много работаю» к «умно зарабатываю», 
и варианты масштабирования."""
}


# ═══════════════════════════════════════════════════════════════
# ХРАНЕНИЕ ДАННЫХ ПОЛЬЗОВАТЕЛЕЙ
# ═══════════════════════════════════════════════════════════════

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


# ═══════════════════════════════════════════════════════════════
# ЛОГИКА ОПРЕДЕЛЕНИЯ СЦЕНАРИЯ
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


# ═══════════════════════════════════════════════════════════════
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ═══════════════════════════════════════════════════════════════

async def reply(chat_id, text, kb=None):
    await bot.send_message(chat_id=chat_id, text=text, attachments=kb)


# ═══════════════════════════════════════════════════════════════
# ОБРАБОТЧИКИ
# ═══════════════════════════════════════════════════════════════

@dp.bot_started()
async def on_start_btn(event: BotStarted):
    cid = event.chat_id
    get_user(cid)
    await reply(cid, START_MSG, MAIN_MENU)


@dp.message_created(Command("start"))
async def on_start_cmd(event: MessageCreated):
    cid = event.message.recipient.chat_id
    get_user(cid)
    await reply(cid, START_MSG, MAIN_MENU)


@dp.message_created()
async def on_text(event: MessageCreated):
    cid = event.message.recipient.chat_id
    u = get_user(cid)
    text = (event.message.body.text or "").strip()

    if not text:
        return

    # Ждём имя в диагностике
    if u.get("state") == "wait_name":
        name = text.split()[0].capitalize()
        set_user(cid, name=name, state="wait_wm")
        await reply(cid, DIAG_Q2.format(name=name), KB_WORK_MODE)
        return

    # Навигация по меню
    if text.lower() in ("меню", "menu", "старт"):
        set_user(cid, state=None)
        await reply(cid, "Выбирайте:", MAIN_MENU)
        return


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
        set_user(cid, state="wait_name")
        await reply(cid, DIAG_Q1)
        return

    if data == "menu_mat":
        await reply(cid, MATERIALS_INTRO, KB_MATERIALS)
        return

    if data == "menu_clients":
        set_user(cid, state="cl_q1")
        await reply(cid, MORE_CLIENTS_Q1, KB_SITUATION)
        return

    # ─── ДИАГНОСТИКА: формат работы ───
    if data.startswith("wm_"):
        mode_map = {"wm_salon": "salon", "wm_hybrid": "hybrid", "wm_private": "private"}
        set_user(cid, work_mode=mode_map.get(data, "private"), state="wait_city")
        await reply(cid, DIAG_Q3, KB_CITY)
        return

    # ─── ДИАГНОСТИКА: город ───
    if data.startswith("city_"):
        set_user(cid, city=data, state="wait_clients")
        wm = u.get("work_mode", "private")
        if wm == "salon":
            await reply(cid, DIAG_Q4_SALON, KB_CLIENTS_SALON)
        elif wm == "hybrid":
            await reply(cid, DIAG_Q4_HYBRID, KB_CLIENTS_HYBRID)
        else:
            await reply(cid, DIAG_Q4_PRIVATE, KB_CLIENTS_PRIVATE)
        return

    # ─── ДИАГНОСТИКА: количество клиентов ───
    if data.startswith("cl_"):
        set_user(cid, clients=data, state="wait_problem")
        wm = u.get("work_mode", "private")
        if wm == "salon":
            await reply(cid, DIAG_Q5, KB_PROBLEM_SALON)
        elif wm == "hybrid":
            await reply(cid, DIAG_Q5, KB_PROBLEM_HYBRID)
        else:
            await reply(cid, DIAG_Q5, KB_PROBLEM_PRIVATE)
        return

    # ─── ДИАГНОСТИКА: проблема ───
    if data.startswith("prob_"):
        set_user(cid, problem=data, state="wait_sources")
        wm = u.get("work_mode", "private")
        if wm == "salon":
            await reply(cid, DIAG_Q6_SALON, KB_SOURCES_SALON)
        else:
            await reply(cid, DIAG_Q6_PRIVATE, KB_SOURCES_PRIVATE)
        return

    # ─── ДИАГНОСТИКА: источники ───
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

        # Показываем результат диагностики
        u = get_user(cid)
        scenario = determine_scenario(u)
        result_text = RESULTS.get(scenario, RESULTS["private-grow"])
        set_user(cid, state=None)
        await reply(cid, result_text.format(name=name), KB_RESULT)
        return

    # ─── ССЫЛКА НА САЙТ ───
    if data == "go_site":
        await reply(cid, "Переходите по ссылке для получения полного плана:\n👉 https://lp.massagestart.ru", KB_BACK)
        return

    # ─── БЕСПЛАТНЫЕ МАТЕРИАЛЫ ───
    if data.startswith("mat_"):
        names = {
            "mat_mistakes": "10 ошибок, из-за которых уходят клиенты",
            "mat_expensive": "Как ответить на «дорого»",
            "mat_templates": "Шаблоны сообщений для записи",
        }
        mat = names.get(data, "Материал")
        await reply(cid, f"📎 «{mat}» — отправляю!\n\n[Файл будет добавлен после создания PDF-материалов]\n\n{MATERIAL_SENT}", KB_AFTER_MAT)
        return

    # ─── ХОЧУ БОЛЬШЕ КЛИЕНТОВ: вопрос 1 ───
    if data.startswith("sit_"):
        sit_map = {"sit_beg": "beginner", "sit_unst": "unstable", "sit_opt": "optimize"}
        set_user(cid, situation=sit_map.get(data, "unstable"), state="cl_q2")
        await reply(cid, MORE_CLIENTS_Q2, KB_TRIED)
        return

    # ─── ХОЧУ БОЛЬШЕ КЛИЕНТОВ: вопрос 2 → рекомендация ───
    if data.startswith("tried_"):
        u = get_user(cid)
        sit = u.get("situation", "unstable")
        rec_text = PRODUCT_RECS.get(sit, PRODUCT_RECS["unstable"])
        
        set_user(cid, state=None)
        await reply(cid, rec_text, make_kb([
            [("🔍 Сделать разбор бесплатно", "menu_diag")],
            [("🔙 Вернуться в меню", "back_menu")],
        ]))
        return


# ═══════════════════════════════════════════════════════════════
# ЗАПУСК БОТА
# ═══════════════════════════════════════════════════════════════

async def main():
    logger.info("Бот запускается...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
