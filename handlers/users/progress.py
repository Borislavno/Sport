from datetime import datetime, timedelta, time

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message

from loader import bot, dp
from utils.db_api.gino import User, Progress, Week, db


async def progress(dp: Dispatcher):
    users = await User.query.gino.all()
    for user in users:
        now = datetime.utcnow()
        try:
            user_timezone = now.today() + timedelta(hours=user.timezone) or 0
            if user_timezone != 0:
                if user_timezone.hour == time(hour=9) and user_timezone.minute == time(minute=0):
                    await dp.bot.send_message(chat_id=user.id,
                                              text='Пора взвесить собственный вес, чтобы ты смог увидеть,как '
                                                   'становишься лучше с каждой тренировкой',
                                              reply_markup=InlineKeyboardMarkup(
                                                  inline_keyboard=[
                                                      [
                                                          InlineKeyboardButton(text='Ввести вес',
                                                                               callback_data='new_progress')
                                                      ]
                                                  ]))
        except:
            pass



@dp.callback_query_handler(text='new_progress')
async def take_weight(call: CallbackQuery, state: FSMContext):
    await call.message.answer('Взвесьтесь и введите свой вес')
    await state.set_state('take_weight')


@dp.message_handler(state='take_weight')
async def check_update_weight(message: Message, state: FSMContext):
    weight = message.text
    if weight.isdigit() and len(weight) < 4:
        progress = await Progress.query.where(Progress.user == message.from_user.id).gino.first()
        now = datetime.utcnow()
        if progress.update_week == 1:
            one_week = await Week.get(progress.week_1)
            if one_week.day_six != None and one_week.day_seven == None:
                total = await db.func.count(Week.id).gino.scalar() or 0
                await one_week.update(day_seven=weight).apply()
                new_weak = await Week.create(id=total + 1, progress=progress.id, day_one=None, begin=now.today())
                await progress.update(week_2=new_weak.id, update_week=2).apply()
            if one_week.day_five != None and one_week.day_six == None:
                await one_week.update(day_six=weight).apply()
            if one_week.day_four != None and one_week.day_five == None:
                await one_week.update(day_five=weight).apply()
            if one_week.day_three != None and one_week.day_four == None:
                await one_week.update(day_four=weight).apply()
            if one_week.day_two != None and one_week.day_three == None:
                await one_week.update(day_three=weight).apply()
            if one_week.day_one != None and one_week.day_two == None:
                await one_week.update(day_two=weight).apply()
            if one_week.day_one == None:
                await one_week.update(day_one=weight).apply()
        if progress.update_week == 2:
            one_week = await Week.get(progress.week_2) or 0
            total = await db.func.count(Week.id).gino.scalar() or 0
            if one_week.day_six != None and one_week.day_seven == None:
                await one_week.update(day_seven=weight).apply()
                new_weak = await Week.create(id=total + 1, progress=progress.id, day_one=None, begin=now.today())
                await progress.update(week_3=new_weak.id, update_week=3).apply()
            if one_week.day_five != None and one_week.day_six == None:
                await one_week.update(day_six=weight).apply()
            if one_week.day_four != None and one_week.day_five == None:
                await one_week.update(day_five=weight).apply()
            if one_week.day_three != None and one_week.day_four == None:
                await one_week.update(day_four=weight).apply()
            if one_week.day_two != None and one_week.day_three == None:
                await one_week.update(day_three=weight).apply()
            if one_week.day_one != None and one_week.day_two == None:
                await one_week.update(day_two=weight).apply()
            if one_week.day_one == None:
                await one_week.update(day_one=weight).apply()
        if progress.update_week == 3:
            one_week = await Week.get(progress.week_3) or 0
            total = await db.func.count(Week.id).gino.scalar() or 0
            if one_week.day_six != None and one_week.day_seven == None:
                await one_week.update(day_seven=weight).apply()
                new_weak = await Week.create(id=total + 1, progress=progress.id, day_one=None, begin=now.today())
                await progress.update(week_4=new_weak.id, update_week=4).apply()
            if one_week.day_five != None and one_week.day_six == None:
                await one_week.update(day_six=weight).apply()
            if one_week.day_four != None and one_week.day_five == None:
                await one_week.update(day_five=weight).apply()
            if one_week.day_three != None and one_week.day_four == None:
                await one_week.update(day_four=weight).apply()
            if one_week.day_two != None and one_week.day_three == None:
                await one_week.update(day_three=weight).apply()
            if one_week.day_one != None and one_week.day_two == None:
                await one_week.update(day_two=weight).apply()
            if one_week.day_one == None:
                await one_week.update(day_one=weight).apply()
        if progress.update_week == 4:
            one_week = await Week.get(progress.week_4) or 0
            total = await db.func.count(Week.id).gino.scalar() or 0
            if one_week.day_six != None and one_week.day_seven == None:
                await one_week.update(day_seven=weight).apply()
                list = (progress.week_1, progress.week_2, progress.week_3, progress.week_4)
                for one in list:
                    week = await Week.get(one)
                    await week.update(begin=None, day_one=None, day_two=None, day_three=None, day_four=None,
                                      day_five=None,
                                      day_six=None, day_seven=None).apply()
                await progress.update(update_week=1).apply()
                user = await User.get(message.from_user.id)
                await user.update(weight=weight).apply()
            if one_week.day_five != None and one_week.day_six == None:
                await one_week.update(day_six=weight).apply()
            if one_week.day_four != None and one_week.day_five == None:
                await one_week.update(day_five=weight).apply()
            if one_week.day_three != None and one_week.day_four == None:
                await one_week.update(day_four=weight).apply()
            if one_week.day_two != None and one_week.day_three == None:
                await one_week.update(day_three=weight).apply()
            if one_week.day_one != None and one_week.day_two == None:
                await one_week.update(day_two=weight).apply()
            if one_week.day_one == None:
                await one_week.update(day_one=weight).apply()
        await message.answer('Вес сохранен!')
        await state.finish()
    else:
        await message.answer('Введи числовое значение')

#
# @dp.callback_query_handler(text='my_progress')
# async def user_progress(call: CallbackQuery):
#     progress = await Progress.query.where(Progress.user == call.from_user.id).gino.first()
#     user = await User.get(call.from_user.id)
#     list = (progress.week_1, progress.week_2, progress.week_3, progress.week_4)
#     weight = 0
#     days = 0
#     for one in list:
#         week = await Week.get(one) or 0
#         if week != 0:
#             list = (week.day_one, week.day_two, week.day_three, week.day_four, week.day_five,
#                     week.day_six, week.day_seven)
#             for day in list:
#                 if day != None:
#                     weight = weight + float(day)
#                     days = days + 1
#     try:
#         progress = weight // days
#         if progress < float(user.weight):
#             user_progress = float(user.weight) - float(progress)
#             text = f'Ты скинул {user_progress} кг за {days} дней'
#             await call.message.answer(text, reply_markup=
#             InlineKeyboardMarkup(
#                 inline_keyboard=[
#                     [
#                         InlineKeyboardButton(text='Тестовая кнопка для добавления прогресса',
#                                              callback_data='new_progress')
#                     ],
#                     [
#                         InlineKeyboardButton(text='На главную', callback_data='main')
#                     ]
#                 ]))
#         if progress > float(user.weight):
#             user_progress = float(progress) - float(user.weight)
#             text = f'Твой вес увеличился {user_progress} кг за {days} дней'
#             await call.message.answer(text, reply_markup=InlineKeyboardMarkup(
#                 inline_keyboard=[
#                     [
#                         InlineKeyboardButton(text='Тестовая кнопка для добавления прогресса',
#                                              callback_data='new_progress')
#                     ],
#                     [
#                         InlineKeyboardButton(text='На главную', callback_data='main')
#                     ]
#                 ]))
#         if progress == float(user.weight):
#             text = f'Твой вес не изменился за {days} дней'
#             await call.message.answer(text, reply_markup=
#             InlineKeyboardMarkup(
#                 inline_keyboard=[
#                     [
#                         InlineKeyboardButton(text='Тестовая кнопка для добавления прогресса',
#                                              callback_data='new_progress')
#                     ],
#                     [
#                         InlineKeyboardButton(text='На главную', callback_data='main')
#                     ]
#                 ]))
#     except ZeroDivisionError:
#         await call.message.answer('Я ежемесячно обнуляю твой прогресс, поэтому не переживай\n'
#                                   f'Твой вес сохранен {user.weight}', reply_markup=
#                                   InlineKeyboardMarkup(
#                                       inline_keyboard=[
#                                           [
#                                               InlineKeyboardButton(text='Тестовая кнопка для добавления прогресса',
#                                                                    callback_data='new_progress')
#                                           ],
#                                           [
#                                               InlineKeyboardButton(text='На главную', callback_data='main')
#                                           ]
#                                       ]))

@dp.callback_query_handler(text='my_progress')
async def user_progress(call: CallbackQuery):
    user= await User.get(call.from_user.id)
    progress = await Progress.query.where(Progress.user ==call.from_user.id).gino.first()
    days =[]
    list = (progress.week_1, progress.week_2, progress.week_3, progress.week_4)
    for one in list:
        week = await Week.get(one) or 0
        if week != 0:
            list = (week.day_one, week.day_two, week.day_three, week.day_four, week.day_five,
                        week.day_six, week.day_seven)
            for day in list:
                if day != None:
                    days.append(day)
    len_days = len(days)
    text = ''
    progress = days[len_days-1]
    try:
        progress_2 = days[len_days - 8] or 0
    except IndexError:
        progress_2= 0
    if user.goal == 1:
        if progress > user.weight:
            difference = float(progress) - float(user.weight)
            difference=str(difference)
            text = text + f'Ты хотел похудеть,а ты набрал {difference[0:5]} кг'
            if progress_2 != 0:
                text = text + f'\nНеделю назад ты весил {progress_2}'
        else:
            difference = float(user.weight) - float(progress)
            difference = str(difference)
            text = text + f'Молодец, ты похудел на {difference[0:5]} кг'
            if progress_2 != 0:
                text = text + f'\nНеделю назад ты весил {progress_2}'
    if user.goal == 2:
        if progress < user.weight:
            difference = float(progress) - float(user.weight)
            difference = str(difference)
            text = text + f'Ты хотел набрать вес,а ты скинул {difference[0:5]} кг'
            if progress_2 != 0:
                text = text + f'\nНеделю назад ты весил {progress_2}'
        else:
            difference = float(user.weight) - float(progress)
            difference = str(difference)
            text = text + f'Молодец, ты ты набрал {difference[0:5]} кг'
            if progress_2 != 0:
                text = text + f'\nНеделю назад ты весил {progress_2}'
    if user.goal == 3:
        text = text + f'Твой вес сейчас: {progress}'
        if progress_2 != 0:
            text = text + f'\nНеделю назад ты весил {progress_2}'

    await call.message.answer(text=text, reply_markup=
    InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Тестовая кнопка для добавления прогресса',
                                     callback_data='new_progress')
            ],
            [
                InlineKeyboardButton(text='На главную', callback_data='main')
            ]]))