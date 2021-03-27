from aiogram import Dispatcher

from loader import dp
from .deleting import  CallAnswerMiddleware
from .throttling import ThrottlingMiddleware


if __name__ == "middlewares":
    dp.middleware.setup(CallAnswerMiddleware())
