from datetime import timedelta, datetime

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiogram.utils.callback_data import CallbackData

from filters import Registered_User, Banned_User
from loader import dp
from utils.db_api.gino import User, UserActivity, Set

menu_cb = CallbackData('menu', 'section', 'action', 'id', 'page')


@dp.message_handler(CommandStart(), Banned_User())
async def start_banned_user(message: Message):
    await message.answer('Вы были заблокированы для использования ботом\n'
                         'Для связи обращаться:')


@dp.message_handler(CommandStart(), Registered_User())
async def start_registered_user(message: Message, state: FSMContext):
    user = await User.get(message.from_user.id)
    if user.timezone == None:
        await message.answer(f'Привет {user.name}! Для полноценной работы нужно подстроить часовые пояса и '
                             f'выбрать дни тренировок,'
                             f'чтобы получить полный функционал',
                             reply_markup=InlineKeyboardMarkup(
                                 inline_keyboard=[
                                     [
                                         InlineKeyboardButton(text='Перейти к настройке',
                                                              callback_data='user_timezone')
                                     ]
                                 ]
                             )
                             )
    else:
        keyboard_markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text='Мои тренировки',
                                      callback_data='my_training')],
                [InlineKeyboardButton(text='Мой тренер',
                                      callback_data='my_trainer')],
                [
                    InlineKeyboardButton(text='Изменить мои данные',
                                         callback_data='edit_info')
                ],
                [
                    InlineKeyboardButton(text='Мой прогресс',callback_data='my_progress')
                ]
            ]
        )
        reply = 'Всё готово к тренировкам! Я подготовил для тебя программу тренировок, ' \
                'тебе осталось только выбрать дни и время! Переходи в раздел мои тренировки.'
        await message.answer_sticker(sticker='CAACAgIAAxkBAAIFXl-MM6pAuLdeCrnU_an2tvqJXDP5AAKDAQACJQNSD1jTbR37DxktGwQ')
        await message.answer(text=reply, reply_markup=keyboard_markup)


@dp.callback_query_handler(Registered_User(), text='main')
async def menu_users(call: CallbackQuery, state: FSMContext):
    user = await User.get(call.from_user.id)
    if user.timezone == None:
        await call.message.answer(f'Привет {user.name}! Для полноценной работы нужно подстроить часовые пояса и '
                                  f'выбрать дни тренировок,'
                                  f'чтобы получить полный функционал',
                                  reply_markup=InlineKeyboardMarkup(
                                      inline_keyboard=[
                                          [
                                              InlineKeyboardButton(text='Перейти к настройке',
                                                                   callback_data='user_timezone')
                                          ]
                                      ]
                                  )
                                  )
    else:
        keyboard_markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text='Мои тренировки',
                                      callback_data='my_training')],
                [InlineKeyboardButton(text='Мой тренер',
                                      callback_data='my_trainer')],
                [
                    InlineKeyboardButton(text='Изменить мои данные',
                                         callback_data='edit_info')
                ],
                [
                    InlineKeyboardButton(text='Мой прогресс',callback_data='my_progress')
                ]
            ]
        )
        reply = 'Всё готово к тренировкам! Можешь выбрать составлять тренировки, '
        await call.message.answer_sticker(
            sticker='CAACAgIAAxkBAAIFXl-MM6pAuLdeCrnU_an2tvqJXDP5AAKDAQACJQNSD1jTbR37DxktGwQ')
        await call.message.answer(text=reply, reply_markup=keyboard_markup)
