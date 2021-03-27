import random

from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.markdown import hlink

from loader import dp, bot
from utils.db_api.gino import User, Trainer, db, Goal

choice_trainer = CallbackData('trainer', 'id_trainer')
confirm_study = CallbackData('update', 'id_user')
refuse_study = CallbackData('refuse', 'id_user')


@dp.callback_query_handler(text='my_trainer')
async def check_user_trainer(call: CallbackQuery):
    user = await User.get(call.from_user.id)
    if user.my_trainer == None:
        await call.message.answer('У вас нет тренера. Не хотите его найти?',
                                  reply_markup=InlineKeyboardMarkup(
                                      inline_keyboard=[
                                          [
                                              InlineKeyboardMarkup(text='Подобрать мне тренера',
                                                                   callback_data='find_trainer')
                                          ],
                                          [
                                              InlineKeyboardButton(text='На главную', callback_data='main')
                                          ]
                                      ]
                                  ))
    if user.my_trainer != None:
        trainer = await Trainer.query.where(Trainer.user == user.my_trainer).gino.first()
        user = await User.get(trainer.user)
        trainer_link = f'https://t.me/{user.name}'
        await call.message.answer(f'Ваш тренер:\n{user.fullname}\n'
                                  f'Связаться с ним можно по этой ссылке - {hlink(user.name, trainer_link)}',
                                  reply_markup=InlineKeyboardMarkup(
                                      inline_keyboard=[
                                          [
                                              InlineKeyboardButton(text='Отказаться от услуг данного тренера',
                                                                   callback_data='delete_my_trainer')
                                          ],
                                          [
                                              InlineKeyboardButton(text='На главную', callback_data='main')
                                          ]
                                      ]
                                  ))

@dp.callback_query_handler(text='delete_my_trainer')
async def delete_users_trainer(call: CallbackQuery):
    user = await User.get(call.from_user.id)
    await user.update(my_trainer=None).apply()
    await call.message.answer('Вы отказались от тренера',reply_markup=
                              InlineKeyboardMarkup(
                                  inline_keyboard=[
                                      [
                                          InlineKeyboardButton(text='На главную', callback_data='main')
                                      ]
                                  ]
                              ))


@dp.callback_query_handler(text='find_trainer')
async def all_trainer(call: CallbackQuery):
    count = await db.func.count(Trainer.confirmed == True).gino.scalar() or 0
    if count == 0:
        await call.message.answer('На данный момент тренеров нет',
                                  reply_markup=InlineKeyboardMarkup(
                                      inline_keyboard=[
                                          [
                                              InlineKeyboardButton(text='На главкую', callback_data='main')
                                          ]
                                      ]
                                  ))
    if count != 0:
        random_number = random.randint(1, int(count))
        trainer = await Trainer.query.where(Trainer.id==random_number).gino.first() or 0
        user_trainer = await User.get(trainer.user) or 0
        text = f'Мы подобрали тебе тренера:\n{user_trainer.fullname}\n' \
               f'Стаж работы: {trainer.experience} лет\nОбразование: {trainer.education}'
        if trainer == 0:
            text = 'Тренеров нет в базе данных'
        await call.message.answer(text,reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text='Выбрать данного тренера',
                                             callback_data=choice_trainer.new(
                                                 id_trainer=user_trainer.id
                                             ))
                    ],
                    [
                        InlineKeyboardButton(text='Подобрать другого',
                                             callback_data='find_trainer')

                    ],
                    [
                        InlineKeyboardButton(text='На главную', callback_data='main')
                    ]
                ]
            ))


@dp.callback_query_handler(choice_trainer.filter(), state='*')
async def submit_application_trainer(call: CallbackQuery, callback_data: dict):
    id_trainer = int(callback_data.get('id_trainer'))
    await call.message.answer('Заявка отправлена. Ждите.',
                              reply_markup=InlineKeyboardMarkup(
                                  inline_keyboard=[
                                      [
                                          InlineKeyboardButton(text='На главную', callback_data='main')
                                      ]
                                  ]
                              ))
    user = await User.get(call.from_user.id)
    goal = await Goal.get(user.goal)
    await bot.send_message(chat_id=id_trainer,
                           text=f'Пользователь {user.fullname} хочет, чтобы Вы стали его тренером\n'
                                f'Цель пользователя: {goal.name} \n'
                                f'Количество тренировок в неделю: {user.training_times}',
                           reply_markup=InlineKeyboardMarkup(
                               inline_keyboard=[
                                   [
                                       InlineKeyboardMarkup(text='Согласиться',
                                                            callback_data=confirm_study.new(
                                                                id_user=call.from_user.id
                                                            ))
                                   ],
                                   [
                                       InlineKeyboardButton(text='Отказать', callback_data=
                                       refuse_study.new(
                                           id_user=call.from_user.id
                                       ))
                                   ]
                               ]
                           ))


@dp.callback_query_handler(confirm_study.filter(), state='*')
async def update_user_trainer(call: CallbackQuery, callback_data: dict):
    id_user = int(callback_data.get('id_user'))
    user = await User.get(id_user)
    trainer = await Trainer.query.where(Trainer.user == call.from_user.id).gino.first()
    await user.update(my_trainer=trainer.user).apply()
    link = f'https://t.me/{user.name}'
    await call.message.answer('Поздравляем! У Вас появился ученик!\n'
                              f'Связаться с ним можно по этой ссылке - {hlink(user.name, link)}')
    await bot.send_message(chat_id=id_user, text='Поздравляем! Тренер принял вашу заявку!')


@dp.callback_query_handler(refuse_study.filter(), state='*')
async def refuse_study_trainer(call: CallbackQuery, callback_data: dict):
    id_user = int(callback_data.get('id_user'))
    await call.message.answer('Вы отказались от ученика.')
    await bot.send_message(chat_id=id_user, text='К сожалению, Ваша заявка отклонена')
