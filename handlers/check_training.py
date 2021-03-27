from aiogram import Dispatcher

from loader import dp
from utils.db_api.gino import User, Activity


async def check_users(dp: Dispatcher):
    users =await User.gino.all()
    for user in users:
        activity = Activity.query.gino.all()
