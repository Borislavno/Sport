from datetime import timedelta, datetime

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiogram.utils.callback_data import CallbackData

from loader import dp
from utils.db_api.gino import User

date_cd = CallbackData('date', 'day')
days_of_training = CallbackData('days_of_week', 'day')

@dp.callback_query_handler(text='user_timezone')
async def user_timezone(call: CallbackQuery,state: FSMContext):
    now = datetime.utcnow()
    month = {1: 'Января', 2: 'Февраля', 3: 'Марта', 4: 'Апреля', 5: 'Мая', 6: 'Июня',
             7: 'Июля', 8: 'Августа', 9: 'Сентября', 10: 'Октября', 11: 'Ноября', 12: 'Декабря'}
    for key, val in month.items():
        if now.month == key:
            month = val
    tomorrow = now.date() + timedelta(days=1)
    await call.message.answer('Сверка часами! Выбери сегодняшнюю дату',
                              reply_markup=
                              InlineKeyboardMarkup(
                                  inline_keyboard=[
                                      [
                                          InlineKeyboardButton(text=f'{now.day} {month}',
                                                               callback_data=date_cd.new(
                                                                   day=now.day
                                                               )),
                                          InlineKeyboardButton(text=f'{tomorrow.day} {month}',
                                                               callback_data=date_cd.new(
                                                                   day=tomorrow.day
                                                               ))
                                      ]
                                  ]
                              ))
    await state.set_state('day_zone')

@dp.callback_query_handler(date_cd.filter(), state='day_zone')
async def date_user(call: CallbackQuery, callback_data: dict, state: FSMContext):
    day = int(callback_data.get('day'))
    await state.update_data(day=day)
    await call.message.answer('Напиши,какой час у тебя')
    await state.set_state('timezone')


@dp.message_handler(state='timezone')
async def user_timezone(message: Message, state: FSMContext):
    user_time = message.text
    month = {1: 'Января', 2: 'Февраля', 3: 'Марта', 4: 'Апреля', 5: 'Мая', 6: 'Июня',
             7: 'Июля', 8: 'Августа', 9: 'Сентября', 10: 'Октября', 11: 'Ноября', 12: 'Декабря'}
    if user_time.isdigit() and len(user_time) < 3:
        data = await state.get_data()
        day = int(data.get('day'))
        now = datetime.utcnow()
        time = int(user_time)
        if day > now.day:
            time = int(user_time) + 24
        timezone = time - now.hour
        await state.update_data(timezone=timezone)
        for key, val in month.items():
            if now.month == key:
                month = val
        await message.answer(f'Подтверди следующие данные: \nСейчас {day} {month},{user_time} часов {now.minute} минут',
                             reply_markup=InlineKeyboardMarkup(
                                 inline_keyboard=[
                                     [
                                         InlineKeyboardButton(text='Все верно', callback_data='choice_days_of_training')
                                     ],
                                     [
                                         InlineKeyboardButton(text='Я ошибся,ввести заново', callback_data='false')
                                     ]
                                 ]
                             ))
        await state.set_state('finish_timezone')
    else:
        await message.answer('Введи час в числовом значении')


@dp.callback_query_handler(state='finish_timezone', text='false')
async def user_repeat(call: CallbackQuery, state: FSMContext):
    await state.reset_data()
    now = datetime.utcnow()
    tomorrow = now.date() + timedelta(days=1)
    month = {1: 'Января', 2: 'Февраля', 3: 'Марта', 4: 'Апреля', 5: 'Мая', 6: 'Июня',
             7: 'Июля', 8: 'Августа', 9: 'Сентября', 10: 'Октября', 11: 'Ноября', 12: 'Декабря'}
    for key, val in month.items():
        if now.month == key:
            month = val
    await call.message.answer('Выбери сегодняшнюю дату',
                              reply_markup=
                              InlineKeyboardMarkup(
                                  inline_keyboard=[
                                      [
                                          InlineKeyboardButton(text=f'{now.day} {month}',
                                                               callback_data=date_cd.new(
                                                                   day=now.day
                                                               )),
                                          InlineKeyboardButton(text=f'{tomorrow.day} {month}',
                                                               callback_data=date_cd.new(
                                                                   day=tomorrow.day
                                                               ))
                                      ]
                                  ]
                              ))
    await state.set_state('day_zone')


@dp.callback_query_handler(state='days_of_training', text='false')
@dp.callback_query_handler(state='*', text='choice_days_of_training')
async def user_timezone(call: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state == 'finish_timezone':
        data = await state.get_data()
        user = await User.get(call.from_user.id)
        await user.update(timezone=int(data['timezone'])).apply()
    await state.reset_data()
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='Понедельник', callback_data=days_of_training.new(day=1)),
            InlineKeyboardButton(text='Вторник', callback_data=days_of_training.new(day=2))
        ],
        [
            InlineKeyboardButton(text='Среда', callback_data=days_of_training.new(day=3)),
            InlineKeyboardButton(text='Четверг', callback_data=days_of_training.new(day=4))
        ],
        [
            InlineKeyboardButton(text='Пятница', callback_data=days_of_training.new(day=5)),
            InlineKeyboardButton(text='Суббота', callback_data=days_of_training.new(day=6))
        ],
        [
            InlineKeyboardButton(text='Воскресение', callback_data=days_of_training.new(day=7))
        ]
    ])
    await call.message.answer('Выбери дни проведения тренировок', reply_markup=markup)
    await state.set_state('days_of_training')


@dp.callback_query_handler(days_of_training.filter(), state='days_of_training')
async def choice_days_training(call: CallbackQuery, state: FSMContext, callback_data: dict):
    day = int(callback_data.get('day'))
    user = await User.get(call.from_user.id)
    data = await state.get_data()
    days = {1: 'Понедельник', 2: 'Вторник', 3: 'Среда', 4: 'Четверг', 5: 'Пятница', 6: 'Суббота',
            7: 'Воскресение'}
    if len(data) == 0:
        await state.update_data(first_day=day)
    if len(data) == 1:
        await state.update_data(second_day=day)
    if len(data) == 2:
        await state.update_data(third_day=day)
    if len(data) == 3:
        await state.update_data(fourth_day=day)
    if len(data) == 4:
        await state.update_data(fifth_day=day)
    if len(data) == 5:
        await state.update_data(sixth_day=day)
    data = await state.get_data()
    if len(data) == user.training_times:
        text = 'Вы выбрали следующие дни для тренировки:\n\n'
        if len(data) >=1:
            first_day = data['first_day']
            for key, val in days.items():
                if first_day == key:
                    day = val
            text = text + f'{day}\n'
        if len(data) >= 2:
            second_day = data['second_day']
            for key, val in days.items():
                if second_day == key:
                    day = val
            text = text + f'{day}\n'
        if len(data) >= 3:
            third_day = data['third_day']
            for key, val in days.items():
                if third_day == key:
                    day = val
            text = text + f'{day}\n'
        if len(data) >= 4:
            fourth_day = data['fourth_day']
            for key, val in days.items():
                if fourth_day == key:
                    day = val
            text = text + f'{day}\n'
        if len(data) >= 5:
            fifth_day = data['fifth_day']
            for key, val in days.items():
                if fifth_day == key:
                    day = val
            text = text + f'{day}\n'
        if len(data) >= 6:
            sixth_day = data['sixth_day']
            for key, val in days.items():
                if sixth_day == key:
                    day = val
            text = text + f'{day}\n'
        await call.message.answer(text=text, reply_markup=
        InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='Все верно!', callback_data='true')
                ],
                [
                    InlineKeyboardButton(text='Ввести заново', callback_data='false')
                ]
            ]
        ))

    if len(data) < user.training_times:
        for key, val in days.items():
            if day == key:
                day = val
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text='Понедельник', callback_data=days_of_training.new(day=1)),
                InlineKeyboardButton(text='Вторник', callback_data=days_of_training.new(day=2))
            ],
            [
                InlineKeyboardButton(text='Среда', callback_data=days_of_training.new(day=3)),
                InlineKeyboardButton(text='Четверг', callback_data=days_of_training.new(day=4))
            ],
            [
                InlineKeyboardButton(text='Пятница', callback_data=days_of_training.new(day=5)),
                InlineKeyboardButton(text='Суббота', callback_data=days_of_training.new(day=6))
            ],
            [
                InlineKeyboardButton(text='Воскресение', callback_data=days_of_training.new(day=7))
            ]
        ])
        await call.message.answer(
            f'Ты выбрал : {day}, осталось опредить {int(user.training_times) - int(len(data))} дней',
            reply_markup=markup)



@dp.callback_query_handler(state='days_of_training', text='true')
async def days_finish(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    text = ''
    exp = {1: 'first_day', 2: 'second_day', 3: 'third_day', 4: 'fourth_day', 5: 'fifth_day', 6: 'sixth_day'}
    for lens, day in exp.items():
        if len(data) >= lens:
            one = data.get(day)
            text = text + f'{one}'
    user = await User.get(call.from_user.id)
    await user.update(days_of_week=text).apply()
    await call.message.answer('Все! Вопросов больше нет!',
                              reply_markup=InlineKeyboardMarkup(
                                  inline_keyboard=[
                                      [
                                          InlineKeyboardButton(text='На главную', callback_data='main')
                                      ]
                                  ]
                              ))
    await state.finish()
