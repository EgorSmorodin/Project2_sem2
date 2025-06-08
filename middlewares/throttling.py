from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from typing import Callable, Dict, Any, Awaitable
import time


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, limit: float = 0.5):
        self.limit = limit
        self.last_calls: Dict[int, float] = {}

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        user_id = data['event_from_user'].id
        current_time = time.time()

        if user_id in self.last_calls:
            elapsed = current_time - self.last_calls[user_id]
            if elapsed < self.limit:
                return

        self.last_calls[user_id] = current_time
        return await handler(event, data)