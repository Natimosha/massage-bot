"""
Бот-помощник Натальи Тимошиной для мессенджера Max.
massagestart.ru

Запуск: python bot.py
"""
import asyncio
import logging
import os

from maxapi import Bot, Dispatcher
from maxapi.types import BotStarted, MessageCreated, MessageCallback, Command

from storage import get_user, update_user, add_tag, schedule_chain, get_all_users_for_chain
from scenarios import determine_scenario
from keyboards import (
    MAIN_MENU, KB_WORK_MODE, KB_CITY,
    KB_CLIENTS_SALON, KB_CLIENTS_HYBRID, KB_CLIENTS_PRIVATE,
    KB_PROBLEM_SALON, KB_PROBLEM_HYBRID, KB_PROBLEM_PRIVATE,
    KB_SOURCES_SALON, KB_SOURCES_PRIVATE,
    kb_result, KB_MATERIALS, KB_AFTER_MATERIAL,
    KB_SITUATION, KB_TRIED, kb_product_recommendation,
    KB_CHAIN_DAY2, KB_CHAIN_DAY3, KB_CHAIN_DAY5, KB_CHAIN_DAY6, KB_CHAIN_DAY7,
    KB_SURVEY_BRAKE,
)
from texts import (
    START_MSG, DIAG_Q1, DIAG_Q2, DIAG_Q3,
    DIAG_Q4_SALON, DIAG_Q4_HYBRID, DIAG_Q4_PRIVATE,
    DIAG_Q5, DIAG_Q6_SALON, DIAG_Q6_PRIVATE,
    RESULTS, MATERIALS_INTRO, MATERIAL_SENT,
    MORE_CLIENTS_Q1, MORE_CLIENTS_Q2, PRODUCT_RECS,
    CHAIN, CHAIN_SURVEY_THANKS,
    PERIODIC_SURVEY, PERIODIC_SURVEY_THANKS,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─── Токен из переменной окружения ───
TOKEN = os.environ.get("BOT_TOKEN", "ВСТАВЬТЕ_ВАШ_ТОКЕН_СЮДА")
bot = Bot(TOKEN)
dp = Dispatcher()


# ═══════════════════════════════════════════════════════════════
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ═══════════════════════════════════════════════════════════════

def get_chat_id(event):
    """Универсальная функция для получения chat_id из разных типов событий"""
    try:
        # Пробуем разные варианты
        if hasattr(event, 'chat_id'):
            return str(event.chat_id)
        elif hasattr(event, 'message') and hasattr(event.message, 'chat_id'):
            return str(event.message.chat_id)
        elif hasattr(event, 'message') and hasattr(event.message, 'recipient') and hasattr(event.message.recipient, 'chat_id'):
            return str(event.message.recipient.chat_id)
        elif hasattr(event, 'message') and hasattr(event.message, 'chat') and hasattr(event.message.chat, 'id'):
            return str(event.message.chat.id)
        else:
            # Логируем структуру объекта для отладки
            logger.error(f"Не могу найти chat_id в объекте: {dir(event)}")
            return None
    except Exception as e:
        logger.error(f"Ошибка при получении chat_id: {e}")
        return None


async def send(chat_id, text, attachments=None):
    """Отправить сообщение с опциональными вложениями (кнопками)."""
    await bot.send_message(
        chat_id=chat_id,
        text=text,
        attachments=attachments,
    )


async def show_menu(chat_id):
    """Показать главное меню."""
    await send(chat_id, START_MSG, MAIN_MENU)
    await update_user(chat_id, state=None)


# ═══════════════════════════════════════════════════════════════
# /START и кнопка «Начать»
# ═══════════════════════════════════════════════════════════════

@dp.bot_started()
async def on_bot_started(event: BotStarted):
    """Пользователь нажал кнопку «Начать» в боте."""
    chat_id = get_chat_id(event)
    if not chat_id:
        logger.error("Не удалось получить chat_id в on_bot_started")
        return
    user = await get_user(chat_id)
    await show_menu(chat_id)
    # Запуск цепочки прогрева через 24 часа
    if user.get("chain_day", 0) == 0:
        await schedule_chain(chat_id, 0)


@dp.message_created(Command("start"))
async def on_start_command(event: MessageCreated):
    """Пользователь отправил /start."""
    chat_id = get_chat_id(event)
    if not chat_id:
        logger.error("Не удалось получить chat_id в on_start_command")
        return
    user = await get_user(chat_id)
    await show_menu(chat_id)
    if user.get("chain_day", 0) == 0:
        await schedule_chain(chat_id, 0)


# ═══════════════════════════════════════════════════════════════
# ОБРАБОТКА ТЕКСТОВЫХ СООБЩЕНИЙ (имя в диагностике)
# ═══════════════════════════════════════════════════════════════

@dp.message_created()
async def on_message(event: MessageCreated):
    """Обработка текстовых сообщений."""
    chat_id = get_chat_id(event)
    if not chat_id:
        logger.error("Не удалось получить chat_id в on_message")
        return
    user = await get_user(chat_id)
    text = (event.message.body.text or "").strip()

    if not text:
        return

    # Если ждём имя в диагностике
    if user.get("state") == "diag_waiting_name":
        name = text.split()[0].capitalize()
        await update_user(chat_id, name=name, state="diag_q2")
        await send(chat_id, DIAG_Q2.format(name=name), KB_WORK_MODE)
        return

    # Если не в каком-то конкретном состоянии — показать меню
    if text.lower() in ("меню", "menu", "начать", "старт"):
        await show_menu(chat_id)


# ═══════════════════════════════════════════════════════════════
# ОБРАБОТКА НАЖАТИЙ КНОПОК (callback)
# ═══════════════════════════════════════════════════════════════

@dp.message_callback()
async def on_callback(event: MessageCallback):
    """Обработка нажатий inline-кнопок."""
    chat_id = get_chat_id(event)
    if not chat_id:
        logger.error("Не удалось получить chat_id в on_callback")
        return
    data = event.callback.payload or ""
    user = await get_user(chat_id)
    name = user.get("name", "")

    # ─── Навигация ───
    if data == "back_menu":
        await show_menu(chat_id)
        return

    # ─── ГЛАВНОЕ МЕНЮ ───
    if data == "menu_diagnostics":
        await update_user(chat_id, state="diag_waiting_name")
        await send(chat_id, DIAG_Q1)
        return

    if data == "menu_materials":
        await send(chat_id, MATERIALS_INTRO, KB_MATERIALS)
        await update_user(chat_id, state="materials")
        return

    if data == "menu_more_clients":
        await send(chat_id, MORE_CLIENTS_Q1, KB_SITUATION)
        await update_user(chat_id, state="clients_q1")
        return

    # ─── ДИАГНОСТИКА: вопрос 2 — формат работы ───
    if data.startswith("wm_"):
        mode_map = {"wm_salon": "salon-only", "wm_hybrid": "hybrid", "wm_private": "private-only"}
        work_mode = mode_map.get(data, "private-only")
        await update_user(chat_id, work_mode=work_mode, state="diag_q3")
        await send(chat_id, DIAG_Q3, KB_CITY)
        return

    # ─── ДИАГНОСТИКА: вопрос 3 — город ───
    if data.startswith("city_"):
        await update_user(chat_id, city=data, state="diag_q4")
        wm = user.get("work_mode", "private-only")
        if wm == "salon-only":
            await send(chat_id, DIAG_Q4_SALON, KB_CLIENTS_SALON)
        elif wm == "hybrid":
            await send(chat_id, DIAG_Q4_HYBRID, KB_CLIENTS_HYBRID)
        else:
            await send(chat_id, DIAG_Q4_PRIVATE, KB_CLIENTS_PRIVATE)
        return

    # ─── ДИАГНОСТИКА: вопрос 4 — количество клиентов ───
    if data.startswith("cl_"):
        await update_user(chat_id, clients_range=data, state="diag_q5")
        wm = user.get("work_mode", "private-only")
        if wm == "salon-only":
            await send(chat_id, DIAG_Q5, KB_PROBLEM_SALON)
        elif wm == "hybrid":
            await send(chat_id, DIAG_Q5, KB_PROBLEM_HYBRID)
        else:
            await send(chat_id, DIAG_Q5, KB_PROBLEM_PRIVATE)
        return

    # ─── ДИАГНОСТИКА: вопрос 5 — главная проблема ───
    if data.startswith("prob_"):
        await update_user(chat_id, main_problem=data, state="diag_q6")
        wm = user.get("work_mode", "private-only")
        if wm == "salon-only":
            await send(chat_id, DIAG_Q6_SALON, KB_SOURCES_SALON)
        else:
            await send(chat_id, DIAG_Q6_PRIVATE, KB_SOURCES_PRIVATE)
        return

    # ─── ДИАГНОСТИКА: вопрос 6 — источники клиентов ───
    if data.startswith("src_"):
        if data == "src_done":
            pass
        else:
            wm = user.get("work_mode", "private-only")
            if wm == "salon-only":
                await update_user(chat_id, client_sources=[data])
            else:
                sources = user.get("client_sources", [])
                if data not in sources:
                    sources.append(data)
                    await update_user(chat_id, client_sources=sources)
                await send(
                    chat_id,
                    f"✓ Добавлено. Выберите ещё или нажмите «Готово».",
                    KB_SOURCES_PRIVATE
                )
                return

        user = await get_user(chat_id)
        scenario = determine_scenario(user)
        await update_user(chat_id, scenario=scenario, state=None, diagnostics_done=True)
        await add_tag(chat_id, f"scenario:{scenario}")
        await add_tag(chat_id, f"wm:{user.get('work_mode', '')}")

        result_text = RESULTS.get(scenario, RESULTS["private-grow"])
        await send(chat_id, result_text.format(name=name), kb_result())
        return

    # ─── БЕСПЛАТНЫЕ МАТЕРИАЛЫ ───
    if data.startswith("mat_"):
        material_names = {
            "mat_mistakes": "10 ошибок",
            "mat_expensive": "Ответ на дорого",
            "mat_templates": "Шаблоны сообщений",
        }
        mat_name = material_names.get(data, "материал")
        await add_tag(chat_id, f"material:{data}")

        await send(
            chat_id,
            f"📎 «{mat_name}» — отправляю!\n\n"
            f"[Здесь будет файл — подключим после создания PDF-материалов]\n\n"
            f"{MATERIAL_SENT}",
            KB_AFTER_MATERIAL,
        )
        return

    # ─── ХОЧУ БОЛЬШЕ КЛИЕНТОВ: вопрос 1 ───
    if data.startswith("sit_"):
        situation_map = {
            "sit_beginner": "beginner",
            "sit_unstable": "unstable",
            "sit_optimize": "optimize",
        }
        await update_user(chat_id, state="clients_q2", client_situation=situation_map.get(data, "unstable"))
        await send(chat_id, MORE_CLIENTS_Q2, KB_TRIED)
        return

    # ─── ХОЧУ БОЛЬШЕ КЛИЕНТОВ: вопрос 2 → рекомендация ───
    if data.startswith("tried_"):
        user = await get_user(chat_id)
        situation = user.get("client_situation", "unstable")

        if situation == "beginner":
            rec_key = "beginner"
            product = "course"
        elif situation == "optimize":
            rec_key = "optimize"
            product = "mentoring"
        else:
            rec_key = "unstable"
            product = "pdf"

        rec_text = PRODUCT_RECS.get(rec_key, PRODUCT_RECS["unstable"])
        await send(chat_id, rec_text, kb_product_recommendation(product))
        await add_tag(chat_id, f"interest:{product}")
        await update_user(chat_id, state=None, products_shown=True)
        return

    # ─── ЦЕПОЧКА ПРОГРЕВА ───
    if data == "chain_checklist_maps":
        await add_tag(chat_id, "interest:maps_checklist")
        await send(chat_id, "Отправлю чек-лист по картам в ближайшее время! 📎\n\n[Здесь будет файл]")
        return

    if data == "chain_have_maps":
        await add_tag(chat_id, "has:maps_profile")
        await send(chat_id, "Отлично! Значит, у вас уже есть этот канал. Завтра расскажу, что дальше.")
        return

    if data.startswith("survey_"):
        survey_tags = {
            "survey_find_clients": "pain:find_clients",
            "survey_retain": "pain:retain",
            "survey_raise_price": "pain:raise_price",
            "survey_burnout": "pain:burnout",
        }
        tag = survey_tags.get(data, f"survey:{data}")
        await add_tag(chat_id, tag)
        await send(chat_id, CHAIN_SURVEY_THANKS)
        return

    if data == "chain_next":
        await send(chat_id, "Отлично, продолжим завтра! 😊")
        return

    # ─── ПЕРИОДИЧЕСКИЕ ОПРОСЫ ───
    if data.startswith("psurv_"):
        survey_tags = {
            "psurv_no_source": "brake:no_source",
            "psurv_no_time": "brake:no_time",
            "psurv_not_working": "brake:not_working",
            "psurv_scale": "brake:want_scale",
        }
        tag = survey_tags.get(data, f"psurv:{data}")
        await add_tag(chat_id, tag)
        await send(chat_id, PERIODIC_SURVEY_THANKS)
        return


# ═══════════════════════════════════════════════════════════════
# ФОНОВАЯ ЦЕПОЧКА ПРОГРЕВА
# ═══════════════════════════════════════════════════════════════

async def chain_worker():
    while True:
        try:
            users = await get_all_users_for_chain()
            for uid, udata in users:
                day = udata.get("chain_day", 0) + 1
                if day > 7:
                    continue

                text = CHAIN.get(day, "")
                if not text:
                    continue

                kb_map = {
                    2: KB_CHAIN_DAY2,
                    3: KB_CHAIN_DAY3,
                    5: KB_CHAIN_DAY5,
                    6: KB_CHAIN_DAY6,
                    7: KB_CHAIN_DAY7,
                }
                attachments = kb_map.get(day)

                try:
                    await send(uid, text, attachments)
                    await schedule_chain(uid, day)
                    logger.info(f"Chain day {day} sent to {uid}")
                except Exception as e:
                    logger.error(f"Error sending chain to {uid}: {e}")

        except Exception as e:
            logger.error(f"Chain worker error: {e}")

        await asyncio.sleep(300)


# ═══════════════════════════════════════════════════════════════
# ЗАПУСК БОТА
# ═══════════════════════════════════════════════════════════════

async def main():
    logger.info("Бот запускается...")
    asyncio.create_task(chain_worker())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
