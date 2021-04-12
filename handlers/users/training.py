import asyncio
from datetime import datetime, timedelta, time

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import TypeOfFileMismatch

from loader import dp, bot
from utils.db_api.gino import UserActivity, Set, User, Practice, Exercise, Repeat, Activity

training_cd = CallbackData('training', 'set_id')
weight_cd = CallbackData('weight', 'activity_id')


# practice_weight_cd = CallbackData('practice', 'activity_id')


async def training(dp: Dispatcher):
    users = await UserActivity.query.gino.all()
    now = datetime.utcnow()
    for one in users:
        user = await User.get(one.user)
        set = await Set.get(one.set)
        try:
            user_timezone = now + timedelta(hours=user.timezone)
            if user_timezone.date() == one.begin and one.last_training == None and one.set != None:
                if datetime.time(user_timezone + timedelta(minutes=30)).hour == int(one.time) and \
                        datetime.time(user_timezone + timedelta(minutes=30)).minute == 0:
                    await dp.bot.send_message(chat_id=one.user, text='Через 30 минут начнется твоя тренировка!'
                                                                     'Не пропусти!')
                if datetime.time(user_timezone).hour == int(one.time) and \
                        datetime.time(user_timezone).minute == 0:
                    await dp.bot.send_message(chat_id=one.user, text='Пора тренироваться!', reply_markup=
                    InlineKeyboardMarkup(
                        inline_keyboard=[
                            [
                                InlineKeyboardButton(text='Начнем', callback_data=
                                training_cd.new(
                                    set_id=set.id
                                ))
                            ],
                            [
                                InlineKeyboardButton(text='Сегодня не получится',
                                                     callback_data='no_training')
                            ]
                        ]
                    ))
            if user.banned == False and one.set != None:
                days = list(user.days_of_week)
                for day in days:
                    if user_timezone.isoweekday() == int(day):
                        if datetime.time(user_timezone + timedelta(minutes=30)).hour == int(one.time) and \
                                datetime.time(user_timezone + timedelta(minutes=30)).minute == 0:
                            await dp.bot.send_message(chat_id=one.user,
                                                      text='Через 30 минут начнется твоя тренировка!'
                                                           'Не пропусти!')
                        if datetime.time(user_timezone).hour == int(one.time) and \
                                datetime.time(user_timezone).minute == 0:
                            await dp.bot.send_message(chat_id=one.user, text='Пора тренироваться!', reply_markup=
                            InlineKeyboardMarkup(
                                inline_keyboard=[
                                    [
                                        InlineKeyboardButton(text='Начнем', callback_data=
                                        training_cd.new(
                                            set_id=set.id
                                        ))
                                    ],
                                    [
                                        InlineKeyboardButton(text='Сегодня не получится',
                                                             callback_data='no_training')
                                    ]
                                ]
                            ))
        except:
            pass
    users = await User.query.gino.all()
    for user in users:
        now = datetime.utcnow()
        if user.timezone != None:
            user_timezone = now + timedelta(hours=user.timezone)
            print(user_timezone)
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


@dp.callback_query_handler(text='no_training')
async def no_training(call: CallbackQuery):
    await call.message.answer('Очень жаль...', reply_markup=
    InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='На главную', callback_data='main')
            ]
        ]
    ))


@dp.callback_query_handler(text='repeat', state='next_repeat')
@dp.callback_query_handler(training_cd.filter(), state='*')
async def begin_training(call: CallbackQuery, state: FSMContext):
    await call.message.delete_reply_markup()
    user_activities = await UserActivity.query.where(UserActivity.user == call.from_user.id).gino.first()
    set = await Set.get(user_activities.set)
    ids = []
    exercises = await Exercise.query.where(Exercise.set == set.id).gino.all()
    for one in exercises:
        repeats = (one.repeats_1, one.repeats_2, one.repeats_3, one.repeats_4, one.repeats_5)
        for two in repeats:
            repeat = await Repeat.get(two) or 0
            if repeat != 0:
                ids.append(repeat.id)
    current_state = await state.get_state()
    if current_state == 'next_repeat':
        data = await state.get_data()
        repeat = int(data.get('repeat'))
        number = ids.index(repeat)
        await state.reset_data()
        try:
            number = ids[number + 1]
            repeat = await Repeat.get(number)
            exercise = await Exercise.get(repeat.exercise)
            practice = await Practice.get(exercise.practice)
            try:
                video = await call.message.answer_video(video=str(practice.image))
            except TypeOfFileMismatch:
                video = await call.message.answer_animation(animation=practice.image)
            text = f'Повторить {repeat.repeats} раз\n'
            user_activity = await Activity.query.where(
                (Activity.user == call.from_user.id) & (Activity.exercise == exercise.id) & (
                            Activity.repeat == repeat.id)).gino.first()
            if user_activity.weight != None:
                text = text + f'На прошлой тренировке ты брал вес {user_activity.weight} кг'
            desc = await call.message.answer(text=text, reply_markup=
            InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text='Остановить тренировку',
                                             callback_data='stop_training')
                    ]
                ]
            ))
            seconds = repeat.break_second + repeat.repeats * 1.5
            second_2 = seconds - 30
            await asyncio.sleep(second_2)
            timer = await call.message.answer(f'Осталось 30 секунд на выполнение подхода')
            await asyncio.sleep(15)
            await bot.delete_message(chat_id=call.message.chat.id,
                                     message_id=timer.message_id)
            timer = await call.message.answer(f'Осталось 15 секунд на выполнение подхода')
            await asyncio.sleep(15)
            await bot.delete_message(chat_id=call.message.chat.id,
                                     message_id=timer.message_id)
            await bot.delete_message(chat_id=call.message.chat.id,
                                     message_id=video.message_id)
            await bot.delete_message(chat_id=call.message.chat.id,
                                     message_id=desc.message_id)
            await state.set_state('update_weight')
            await state.update_data(repeat=repeat.id)
            message = await call.message.answer('Введи вес, который брал на данном подходе')
            await state.update_data(message=message.message_id)
        except IndexError:
            now = datetime.utcnow()
            user = await User.get(call.from_user.id)
            program_date = user_activities.begin + timedelta(days=int(set.days) * user.training_times)
            if now.date() < program_date:
                await user_activities.update(last_training=now.date()).apply()
                text = 'Отлично потренировались!'
            if now.date() >= program_date:
                text = 'Программа закончилась! Сообщи своему тренеру, или же подбери ее'
                activities = await Activity.query.where(Activity.user == call.from_user.id).gino.all()
                await user_activities.update(set=None, begin=None, last_training=None).apply()
                for one in activities:
                    activity = await Activity.get(one.id)
                    await activity.delete()
            await call.message.answer(text, reply_markup=
            InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text='На главную', callback_data='main')
                    ]
                ]
            ))
            await state.finish()
    else:
        number = ids[0]
        repeat = await Repeat.get(number)
        exercise = await Exercise.get(repeat.exercise)
        practice = await Practice.get(exercise.practice)
        try:
            video = await call.message.answer_video(video=str(practice.image))
        except:
            video = await call.message.answer_animation(animation=practice.image)
        text = f'Повторить {repeat.repeats} раз\n'
        user_activity = await Activity.query.where(
            (Activity.user == call.from_user.id) and (Activity.repeat == repeat.id)).gino.first() or 0
        if user_activity.weight != None:
            text = text + f'На прошлой тренировке ты брал вес {user_activity.weight} кг'
        desc = await call.message.answer(text=text, reply_markup=
        InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='Остановить тренировку',
                                         callback_data='stop_training')
                ]
            ]
        ))
        seconds = repeat.break_second + repeat.repeats * 1.5
        second_2 = seconds - 30
        await asyncio.sleep(second_2)
        timer = await call.message.answer(f'Осталось 30 секунд на выполнение подхода')
        await asyncio.sleep(15)
        await bot.delete_message(chat_id=call.message.chat.id,
                                 message_id=timer.message_id)
        timer = await call.message.answer(f'Осталось 15 секунд на выполнение подхода')
        await asyncio.sleep(15)
        await bot.delete_message(chat_id=call.message.chat.id,
                                 message_id=timer.message_id)
        await bot.delete_message(chat_id=call.message.chat.id,
                                 message_id=video.message_id)
        await bot.delete_message(chat_id=call.message.chat.id,
                                 message_id=desc.message_id)
        await state.set_state('update_weight')
        await state.update_data(repeat=repeat.id)
        message = await call.message.answer('Введи вес, который брал на данном подходе')
        await state.update_data(message=message.message_id)


@dp.message_handler(state='update_weight')
async def update_weight_repeat(message: Message, state: FSMContext):
    weight = message.text
    if weight.isdigit() and len(weight) < 5:
        try:
            weight = float(weight)
            data = await state.get_data()
            await bot.delete_message(chat_id=message.chat.id,
                                     message_id=int(data['message']))
            repeat = await Repeat.get(int(data['repeat']))
            activity = await Activity.query.where(
                (Activity.user == message.from_user.id) & (Activity.exercise == repeat.exercise) & (
                        Activity.repeat == repeat.id)).gino.first()
            await activity.update(weight=str(weight)).apply()
            await message.answer('Приступить к следующему подходу/упражнению',
                                 reply_markup=
                                 InlineKeyboardMarkup(
                                     inline_keyboard=[
                                         [
                                             InlineKeyboardButton(text='Продолжить тренировку',
                                                                  callback_data='repeat')
                                         ],
                                         [
                                             InlineKeyboardButton(text='Остановить тренировку',
                                                                  callback_data='stop_training')
                                         ]
                                     ]
                                 ))
            await state.set_state('next_repeat')
        except:
            await message.answer('Введи числовое значение. Например 50')
    else:
        await message.answer('Введи числовое значение. Например 50')


@dp.callback_query_handler(state='*', text='stop_training')
async def stopping(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.answer('Ты отменил тренировку', reply_markup=
    InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='На главную', callback_data='main')
            ]
        ]
    ))
