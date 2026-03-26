"""
Логика определения сценария на основе ответов пользователя.
6 сценариев: salon-exit, salon-grow, hybrid-exit, hybrid-grow, private-grow, private-optimize.
"""


def determine_scenario(user: dict) -> str:
    """Определить сценарий на основе данных пользователя."""
    work_mode = user.get("work_mode", "")
    problem = user.get("main_problem", "")
    clients = user.get("clients_range", "")

    if work_mode == "salon-only":
        if problem == "prob_want_exit":
            return "salon-exit"
        else:
            return "salon-grow"

    elif work_mode == "hybrid":
        if problem == "prob_want_exit":
            return "hybrid-exit"
        else:
            return "hybrid-grow"

    elif work_mode == "private-only":
        # Определяем по проблеме и количеству клиентов
        if problem in ("prob_want_more", "prob_scale"):
            return "private-optimize"
        elif problem == "prob_few_clients" and clients in ("cl_10-15", "cl_15+"):
            return "private-optimize"
        else:
            return "private-grow"

    return "private-grow"  # fallback
