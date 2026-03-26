"""
Все клавиатуры бота — inline-кнопки для Max API.
Формат Max: attachments → inline_keyboard → buttons (массив массивов).
"""


def kb(buttons: list[list[tuple[str, str]]]) -> list[dict]:
    """
    Создать inline-клавиатуру для Max API.
    buttons: [[("Текст кнопки", "callback_data"), ...], ...]
    Каждый внутренний список — одна строка кнопок.
    """
    rows = []
    for row in buttons:
        r = []
        for text, payload in row:
            r.append({
                "type": "callback",
                "text": text,
                "payload": payload
            })
        rows.append(r)
    return [{
        "type": "inline_keyboard",
        "payload": {"buttons": rows}
    }]


def kb_link(buttons: list[list]) -> list[dict]:
    """
    Клавиатура со смешанными кнопками (callback + link).
    Каждый элемент: ("text", "callback_data") или ("text", "url", "link")
    """
    rows = []
    for row in buttons:
        r = []
        for item in row:
            if len(item) == 3 and item[2] == "link":
                r.append({"type": "link", "text": item[0], "url": item[1]})
            else:
                r.append({"type": "callback", "text": item[0], "payload": item[1]})
        rows.append(r)
    return [{
        "type": "inline_keyboard",
        "payload": {"buttons": rows}
    }]


# ═══════════════════════════════════════
# ГЛАВНОЕ МЕНЮ
# ═══════════════════════════════════════

MAIN_MENU = kb([
    [("🔍 Разобрать мою ситуацию", "menu_diagnostics")],
    [("📚 Бесплатные материалы для роста", "menu_materials")],
    [("📈 Хочу больше клиентов", "menu_more_clients")],
])


# ═══════════════════════════════════════
# ДИАГНОСТИКА — вопросы
# ═══════════════════════════════════════

KB_WORK_MODE = kb([
    [("Только в салоне", "wm_salon")],
    [("Совмещаю салон и частную практику", "wm_hybrid")],
    [("Только частная практика", "wm_private")],
])

KB_CITY = kb([
    [("Москва", "city_moscow"), ("Санкт-Петербург", "city_spb")],
    [("Город-миллионник", "city_million"), ("Крупный город", "city_big")],
    [("Средний город", "city_medium"), ("Небольшой город", "city_small")],
])

# Количество клиентов — адаптивные
KB_CLIENTS_SALON = kb([
    [("До 5", "cl_0-5"), ("5-10", "cl_5-10")],
    [("10-15", "cl_10-15"), ("Больше 15", "cl_15+")],
])

KB_CLIENTS_HYBRID = kb([
    [("0-2", "cl_0-2"), ("3-5", "cl_3-5")],
    [("5-10", "cl_5-10"), ("Больше 10", "cl_10+")],
])

KB_CLIENTS_PRIVATE = kb([
    [("До 5", "cl_0-5"), ("5-10", "cl_5-10")],
    [("10-15", "cl_10-15"), ("Больше 15", "cl_15+")],
])

# Главная проблема — адаптивные
KB_PROBLEM_SALON = kb([
    [("Мало клиентов / пустые окна", "prob_few_clients")],
    [("Низкий процент, хочу больше", "prob_low_percent")],
    [("Хочу уйти из салона на своё", "prob_want_exit")],
    [("Клиенты не возвращаются ко мне", "prob_no_return")],
])

KB_PROBLEM_HYBRID = kb([
    [("Хочу полностью уйти из салона", "prob_want_exit")],
    [("Хочу развивать частную, оставаясь в салоне", "prob_want_grow")],
    [("Не хватает частных клиентов", "prob_few_clients")],
    [("Не знаю, как совмещать без конфликта", "prob_conflict")],
])

KB_PROBLEM_PRIVATE = kb([
    [("Мало клиентов, пустые дни", "prob_few_clients")],
    [("Клиенты есть, хочу больше зарабатывать", "prob_want_more")],
    [("Нет стабильности — то густо, то пусто", "prob_unstable")],
    [("Хочу масштабироваться", "prob_scale")],
])

# Источники клиентов
KB_SOURCES_SALON = kb([
    [("Администратор записывает", "src_admin")],
    [("Клиенты сами просят меня", "src_loyal")],
    [("Беру тех, от кого другие отказались", "src_leftovers")],
    [("По-разному", "src_mixed")],
])

KB_SOURCES_PRIVATE = kb([
    [("Сарафанное радио", "src_referral")],
    [("Соцсети (VK, Telegram, Instagram)", "src_social")],
    [("Площадки (Авито, Профи.ру)", "src_platforms")],
    [("Карты (Яндекс, 2ГИС)", "src_maps")],
    [("Нет своих каналов / случайно", "src_none")],
    [("Готово → к результатам", "src_done")],
])


# ═══════════════════════════════════════
# РЕЗУЛЬТАТ ДИАГНОСТИКИ
# ═══════════════════════════════════════

def kb_result():
    return kb_link([
        [("📋 Получить полный план →", "https://lp.massagestart.ru", "link")],
        [("🔙 Вернуться в меню", "back_menu")],
    ])


# ═══════════════════════════════════════
# БЕСПЛАТНЫЕ МАТЕРИАЛЫ
# ═══════════════════════════════════════

KB_MATERIALS = kb([
    [("✅ 10 ошибок, из-за которых уходят клиенты", "mat_mistakes")],
    [("💬 Как ответить на «дорого»", "mat_expensive")],
    [("📝 Шаблоны сообщений для записи", "mat_templates")],
    [("🔙 Вернуться в меню", "back_menu")],
])

KB_AFTER_MATERIAL = kb([
    [("🔍 Разобрать мою ситуацию", "menu_diagnostics")],
    [("🔙 Вернуться в меню", "back_menu")],
])


# ═══════════════════════════════════════
# ХОЧУ БОЛЬШЕ КЛИЕНТОВ — подбор
# ═══════════════════════════════════════

KB_SITUATION = kb([
    [("Только начинаю, клиентов почти нет", "sit_beginner")],
    [("Клиенты есть, но мало и нестабильно", "sit_unstable")],
    [("Клиентов хватает, хочу больше зарабатывать", "sit_optimize")],
])

KB_TRIED = kb([
    [("Нет, не знаю с чего начать", "tried_nothing")],
    [("Пробовал(а), но не сработало", "tried_failed")],
    [("Кое-что работает, хочу усилить", "tried_some")],
])

def kb_product_recommendation(product: str):
    """Кнопки после рекомендации продукта."""
    buttons = []
    if product == "course":
        buttons.append([("📖 Подробнее о курсе →", "https://lp.massagestart.ru/#tariffs", "link")])
    elif product == "pdf":
        buttons.append([("📋 Подробнее о PDF-плане →", "https://lp.massagestart.ru", "link")])
    elif product == "mentoring":
        buttons.append([("🎯 Записаться на консультацию →", "https://forms.gle/Hhx7CJbf54RGbo8w6", "link")])
    buttons.append([("🔍 Сделать разбор бесплатно", "menu_diagnostics")])
    buttons.append([("🔙 Вернуться в меню", "back_menu")])
    return kb_link(buttons)


# ═══════════════════════════════════════
# ЦЕПОЧКА ПРОГРЕВА — кнопки по дням
# ═══════════════════════════════════════

KB_CHAIN_DAY2 = kb([
    [("Хочу чек-лист по картам", "chain_checklist_maps")],
    [("Уже есть профиль", "chain_have_maps")],
])

KB_CHAIN_DAY3 = kb([
    [("Где найти первых клиентов", "survey_find_clients")],
    [("Как удержать тех, кто есть", "survey_retain")],
    [("Как поднять цены", "survey_raise_price")],
    [("Как перестать работать 24/7", "survey_burnout")],
])

KB_CHAIN_DAY5 = kb([
    [("Хочу проверить свои звенья", "menu_diagnostics")],
    [("Понятно, что дальше?", "chain_next")],
])

KB_CHAIN_DAY6 = kb_link([
    [("📖 Подробнее о курсе →", "https://lp.massagestart.ru/#tariffs", "link")],
    [("🔍 Сделать диагностику", "menu_diagnostics")],
    [("Пока просто читаю", "chain_next")],
])

KB_CHAIN_DAY7 = kb([
    [("🔙 Вернуться в меню", "back_menu")],
])


# ═══════════════════════════════════════
# ПЕРИОДИЧЕСКИЕ ОПРОСЫ
# ═══════════════════════════════════════

KB_SURVEY_BRAKE = kb([
    [("Не знаю, где искать клиентов", "psurv_no_source")],
    [("Знаю, но руки не доходят", "psurv_no_time")],
    [("Пробую, но не работает", "psurv_not_working")],
    [("Всё хорошо, хочу масштабироваться", "psurv_scale")],
])
