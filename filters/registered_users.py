from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

from utils.db_api.gino import User, Trainer


class Trainers(BoundFilter):
    async def check(self, message: types.Message):
        trainer = await Trainer.query.where(Trainer.user == message.from_user.id).gino.first() or 0
        if trainer != 0:
            if trainer.user == message.from_user.id:
                return message.from_user.id


class Registered_User(BoundFilter):
    async def check(self, message: types.Message):
        user = await User.get(message.from_user.id) or 0
        if user != 0:
            if user.id == message.from_user.id and user.is_trainer == False:
                return message.from_user.id


class Banned_User(BoundFilter):
    async def check(self, message: types.Message):
        user = await User.get(message.from_user.id) or 0
        if user != 0:
            if user.banned == True:
                return message.from_user.id
