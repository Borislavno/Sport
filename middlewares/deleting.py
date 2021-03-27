from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils.exceptions import MessageError

from utils.db_api.gino import User


class AccessMiddleware(BaseMiddleware):

    def __init__(self):
        super().__init__()

    async def on_pre_process_message(self, message: types.Message, data: dict, *arg, **kwargs):
        data['user'] = await User().get_or_create(types.User.get_current())

    async def on_pre_process_callback_query(self, callback_query: types.CallbackQuery, data: dict, *arg, **kwargs):
        data['user'] = await User().get_or_create(types.User.get_current())


class CallAnswerMiddleware(BaseMiddleware):
    """One screen menu - удаляем предыдущие сообщения"""

    def __init__(self):
        super().__init__()

    async def on_post_process_callback_query(self, call: types.CallbackQuery, data: dict, *arg, **kwargs):
        try:
            await call.message.delete()
        except MessageError:
            pass

    async def on_post_process_message(self, message: types.Message, data: dict, *arg, **kwargs):
        try:
            await message.delete()
        except MessageError:
            pass