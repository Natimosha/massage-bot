"""
Хранение данных пользователей: состояния диалогов, теги, расписание цепочки.
Используем JSON-файл для простоты (на бесплатном хостинге нет БД).
"""
import json
import os
import asyncio
from datetime import datetime, timedelta
from typing import Optional

DATA_FILE = "user_data.json"
_lock = asyncio.Lock()


def _load() -> dict:
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def _save(data: dict):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


async def get_user(chat_id: str) -> dict:
    async with _lock:
        data = _load()
        uid = str(chat_id)
        if uid not in data:
            data[uid] = {
                "name": None,
                "state": None,           # текущее состояние диалога
                "scenario": None,         # определённый сценарий (salon-exit, etc.)
                "work_mode": None,        # salon-only / hybrid / private-only
                "city": None,
                "clients_range": None,
                "main_problem": None,
                "client_sources": [],
                "tags": [],               # теги для сегментации
                "chain_day": 0,           # текущий день цепочки прогрева
                "chain_next": None,       # ISO datetime следующего сообщения цепочки
                "registered_at": datetime.now().isoformat(),
                "diagnostics_done": False,
                "products_shown": False,
            }
            _save(data)
        return data[uid]


async def update_user(chat_id: str, **kwargs):
    async with _lock:
        data = _load()
        uid = str(chat_id)
        if uid not in data:
            data[uid] = {}
        data[uid].update(kwargs)
        _save(data)


async def add_tag(chat_id: str, tag: str):
    async with _lock:
        data = _load()
        uid = str(chat_id)
        if uid in data:
            tags = data[uid].get("tags", [])
            if tag not in tags:
                tags.append(tag)
                data[uid]["tags"] = tags
                _save(data)


async def get_all_users_for_chain() -> list:
    """Получить пользователей, которым пора отправить сообщение цепочки."""
    async with _lock:
        data = _load()
        now = datetime.now()
        result = []
        for uid, udata in data.items():
            chain_next = udata.get("chain_next")
            if chain_next and udata.get("chain_day", 0) < 8:
                try:
                    next_dt = datetime.fromisoformat(chain_next)
                    if now >= next_dt:
                        result.append((uid, udata))
                except (ValueError, TypeError):
                    pass
        return result


async def schedule_chain(chat_id: str, day: int):
    """Запланировать следующее сообщение цепочки через 24 часа."""
    next_time = (datetime.now() + timedelta(hours=24)).isoformat()
    await update_user(chat_id, chain_day=day, chain_next=next_time)
