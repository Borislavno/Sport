import random
from datetime import datetime, timedelta, date

from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from handlers.users.training import training_cd
from loader import dp
from utils.db_api.gino import UserActivity, User, Set, db, Goal, Activity, Exercise, Repeat

random_cd = CallbackData('random', 'user_goal')
confirm_cd = CallbackData('confirm', 'id_set')
update_set = CallbackData('update', 'id_set', 'begin_day', 'begin_month')
time_set = CallbackData('time', 'id_set', 'begin', 'hour', 'confirm')


@dp.callback_query_handler(text='my_training')
async def check_training(call: CallbackQuery):
    user = await User.get(call.from_user.id)
    user_activity = await UserActivity.query.where(UserActivity.user == call.from_user.id).gino.first()
    if user_activity.begin == None and user_activity.last_training == None:
        await call.message.answer('У вас нет программы тренировок, можете сделать ее самостоятельно'
                                  ' или мы сами составим специально для Вас',
                                  reply_markup=InlineKeyboardMarkup(
                                      inline_keyboard=[
                                          [
                                              InlineKeyboardButton(text='Подобрать программу',
                                                                   callback_data=random_cd.new(
                                                                       user_goal=user.goal))
                                          ],
                                          [
                                              InlineKeyboardButton(text='На главную', callback_data='main')
                                          ]
                                      ]))
    else:
        if user_activity.begin != None and user_activity.last_training == None:
            mounts = {1:'января',2:'ферваля',3:'марта',4:'апреля',5:'мая',6:'июня',
                      7:'июля',8:'августа',9:'сентября',10:'октября',11:'ноября',12:'декабря'}
            for one,val in mounts.items():
                if (user_activity.begin).month==one:
                    month = val
            await call.message.answer(f'Ваша первая тренировка начнется {(user_activity.begin).day} '
                                      f'{month} в {user_activity.time}:00',
                                      reply_markup=
                                      InlineKeyboardMarkup(
                                          inline_keyboard=[
                                              [
                                                  InlineKeyboardButton(text='Тестовая кнопка для тренировки',
                                                                       callback_data=
                                                                       training_cd.new(
                                                                           set_id=user_activity.set
                                                                       ))
                                              ],
                                              [
                                                  InlineKeyboardButton(text='Назад', callback_data='main')
                                              ]
                                          ]
                                      ))
        else:
            days = {1: 'Понедельник', 2: 'Вторник', 3: 'Среда', 4: 'Четверг', 5: 'Пятница', 6: 'Суббота',
                    7: 'Воскресение'}
            new_list = list(user.days_of_week)
            one_day = ''
            for one in new_list:
                for number, day in days.items():
                    if int(one) == number:
                        one_day = one_day + f'{day}\n'
            await call.message.answer(f'Ваши тренировки проходят в {user_activity.time}:00 по следующим '
                                      f'дням:\n{one_day}', reply_markup=
                                      InlineKeyboardMarkup(
                                          inline_keyboard=[
                                              [
                                                  InlineKeyboardButton(text='Назад', callback_data='main')
                                              ],
                                              [
                                                  InlineKeyboardButton(text='Тестовая кнопка для тренировки',
                                                                       callback_data=
                                                                       training_cd.new(
                                                                           set_id=user_activity.set
                                                                       ))
                                              ]
                                          ]
                                      ))


@dp.callback_query_handler(random_cd.filter())
async def random_sets(call: CallbackQuery, callback_data: dict):
    user_goal = int(callback_data.get('user_goal'))
    user = await User.get(call.from_user.id)
    all_set = await Set.query.where((Set.place==user.place)&(Set.goal==user_goal)).gino.all() or 0
    numbers = []
    if all_set == 0:
        await call.message.answer('На данный момент нет тренировок', reply_markup=InlineKeyboardMarkup
            (inline_keyboard=[
            [
                InlineKeyboardButton(text='На главную', callback_data='main')
            ]
        ]))
    else:
        for one in all_set:
            numbers.append(one.id)
        random_number = random.choice(numbers)
        random_set = await Set.get(random_number)
        text = f'Программа:\n{random_set.name}\nДлительность курса : {random_set.days} дней\n'
        await call.message.answer(text=text, reply_markup=
        InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='Выбрать данную программу',
                                         callback_data=confirm_cd.new(
                                             id_set=random_set.id
                                         ))
                ],
                [
                    InlineKeyboardButton(text='Выбрать другую програму',
                                         callback_data=random_cd.new(
                                             user_goal=user_goal
                                         ))
                ],
                [
                    InlineKeyboardButton(text='Назад', callback_data='main')
                ]
            ]
        ))


@dp.callback_query_handler(confirm_cd.filter())
async def confirm_set(call: CallbackQuery, callback_data: dict):
    id_set = (callback_data.get('id_set'))
    now = datetime.utcnow()
    today = now.date()
    tomorrow = today + timedelta(days=1)
    day_after_tomorrow = tomorrow + timedelta(days=1)
    await call.message.answer('Выбери день, когда начнешь заниматься',
                              reply_markup=InlineKeyboardMarkup(
                                  inline_keyboard=[
                                      [
                                          InlineKeyboardButton(text=f'Сегодня, {today.day}.{today.month}',
                                                               callback_data=update_set.new(
                                                                   id_set=id_set,
                                                                   begin_day=today.day,
                                                                   begin_month=today.month
                                                               ))
                                      ],
                                      [
                                          InlineKeyboardButton(text=f'Завтра, {tomorrow.day}.{tomorrow.month}',
                                                               callback_data=update_set.new(
                                                                   id_set=id_set,
                                                                   begin_day=tomorrow.day,
                                                                   begin_month=tomorrow.month
                                                               ))
                                      ],
                                      [
                                          InlineKeyboardButton(
                                              text=f'Послезавтра, {day_after_tomorrow.day}.{day_after_tomorrow.month}',
                                              callback_data=update_set.new(
                                                  id_set=id_set,
                                                  begin_day=day_after_tomorrow.day,
                                                  begin_month=day_after_tomorrow.month
                                              ))
                                      ],
                                      [
                                          InlineKeyboardButton(text='Назад', callback_data='my_training')
                                      ]
                                  ]
                              ))


@dp.callback_query_handler(update_set.filter())
async def update_user_activity(call: CallbackQuery, callback_data: dict):
    id_set = int(callback_data.get('id_set'))
    begin_day = int(callback_data.get('begin_day'))
    begin_month = int(callback_data.get('begin_month'))
    now = datetime.now()
    begin_date = date(now.year, begin_month, begin_day)
    markup = InlineKeyboardMarkup(row_width=3)
    for time in range(25):
        if len(str(time)) < 2:
            time = f'0{time}'
        markup.insert(InlineKeyboardButton(
            text=f'{time}:00',
            callback_data=time_set.new(id_set=id_set, begin=begin_date, hour=time, confirm='-')
        ))
    markup.row(InlineKeyboardButton(text='Назад', callback_data=confirm_cd.new(id_set=id_set)))
    await call.message.answer('Выбери время тренировок, чтобы я мог напоминать', reply_markup=markup)


@dp.callback_query_handler(time_set.filter(confirm='+'))
async def update_user_activity(call: CallbackQuery, callback_data: dict):
    id_set = int(callback_data.get('id_set'))
    begin = (callback_data.get('begin'))
    begin = datetime.strptime(begin, '%Y-%m-%d').date()
    hour = int(callback_data.get('hour'))
    exercises = await Exercise.query.where(Exercise.set == id_set).gino.all()
    for one in exercises:
        exercise = await Exercise.get(one.id)
        list = (exercise.repeats_1, exercise.repeats_2, exercise.repeats_3, exercise.repeats_4, exercise.repeats_5)
        for two in list:
            repeat = await Repeat.get(two) or 0
            if repeat != 0:
                total = await db.func.count(Activity.id).gino.scalar() + 1
                await Activity.create(id=total,
                                      set=id_set,
                                      user=call.from_user.id,
                                      exercise=one.id,
                                      repeat=repeat.id)
    user_activity = await UserActivity.query.where(UserActivity.user == call.from_user.id).gino.first()
    await user_activity.update(set=id_set,
                               user=call.from_user.id,
                               begin=begin,
                               time=hour).apply()

    await call.message.answer('Поздравляю! Теперь у тебя есть собственная программа, по которой будем заниматься!',
                              reply_markup=InlineKeyboardMarkup(
                                  inline_keyboard=[
                                      [
                                          InlineKeyboardButton(text='На главную', callback_data='main')
                                      ]
                                  ]
                              ))


@dp.callback_query_handler(time_set.filter())
async def choice_confirm_set(call: CallbackQuery, callback_data: dict):
    id_set = int(callback_data.get('id_set'))
    begin = callback_data.get('begin')
    hour = int(callback_data.get('hour'))
    set = await Set.get(id_set)
    user = await User.get(call.from_user.id)
    goal = await Goal.get(user.goal)
    text = f'Вы выбрали следующую программу тренировок:\nПрограмма для : {goal.name}\n' \
           f'Продолжительность программы: {set.days} тренировочных дней\n' \
           f'Тренировка начинается с {begin[8:10]}.{begin[5:7]},' \
           f' время проведения тренировки в {hour} часов.\nВсе верно?'
    reply = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Подтверждаю', callback_data=time_set.new(id_set=id_set,
                                                                                    begin=begin,
                                                                                    hour=hour,
                                                                                    confirm='+'))
            ],
            [
                InlineKeyboardButton(text='Назад', callback_data=update_set.new(id_set=id_set,
                                                                                begin_day=begin[8:10],
                                                                                begin_month=begin[5:7]))
            ]
        ])
    await call.message.answer(text=text, reply_markup=reply)
