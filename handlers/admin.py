from aiogram.types import CallbackQuery, Message

from handlers.users.trainers import trainer_conrirm_cd, delete_trainer_cd
from loader import dp, bot
from utils.db_api.gino import Trainer, User

