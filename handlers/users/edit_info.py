from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from loader import dp
from utils.db_api.gino import User, Place, Goal, Set, UserActivity, Activity, Exercise, Repeat, db

goals_cd = CallbackData('update_goal', 'goal')
place_cd = CallbackData('update_place', 'place')
time_cd = CallbackData('update_time', 'time')
days_cd = CallbackData('update_days', 'days')
sets_cd = CallbackData('update_set','set')
hour_cd = CallbackData('update_hour', 'hour')


@dp.callback_query_handler(text='edit_info')
async def menu_info(call: CallbackQuery):
    user = await User.get(call.from_user.id)
    place = await Place.get(user.place)
    goal = await Goal.get(user.goal)
    week = {1: 'Понедельник', 2: 'Вторник', 3: 'Среда', 4: "Четверг", 5: "Пятница", 6: "Суббота", 7: "Воскресение"}
    days = ''
    for one in list(user.days_of_week):
        for number, day in week.items():
            if int(one) == int(number):
                days = days + f'{day} '
    text = f'Ваше имя: {user.fullname}\nЦель : {goal.name}\nМесто тренировок : {place.name}\n' \
           f'Количество тренировок в неделю: {user.training_times}\nДни тренировок: {days}'
    await call.message.answer(text, reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Изменить цель', callback_data='edit_goal'),
                InlineKeyboardButton(text='Изменить место тренировок', callback_data='edit_place')
            ],
            [
                InlineKeyboardButton(text='Изменить количество тренировок', callback_data='edit_training_times'),
                InlineKeyboardButton(text='Изменить дни тренировки', callback_data='choice_days_of_training'),
                InlineKeyboardButton(text='Изменить время тренировок', callback_data='edit_time_training')
            ],
            [
                InlineKeyboardButton(text='Тестовая кнопка Изменить программу',callback_data='edit_user_set')
            ],
            [
                InlineKeyboardButton(text='На главную', callback_data='main')
            ]
        ]
    ))


@dp.callback_query_handler(text='edit_goal')
async def choice_goal(call: CallbackQuery):
    goals = await Goal.query.gino.all()
    markup = InlineKeyboardMarkup(row_width=1)
    for one in goals:
        markup.insert(InlineKeyboardButton(text=one.name, callback_data=goals_cd.new(goal=one.id)))
    markup.row(InlineKeyboardButton(text='Назад', callback_data='edit_info'))
    await call.message.answer('Выбери подходящую цель. Не забывай, что цели тренировок очень разные,поэтому упражнения'
                              ' будут другими', reply_markup=markup)


@dp.callback_query_handler(goals_cd.filter())
async def edit_goal(call: CallbackQuery, callback_data: dict):
    goal = int(callback_data.get('goal'))
    user = await User.get(call.from_user.id)
    await user.update(goal=goal).apply()
    await call.message.answer('Отлично! Ваша цель изменена!', reply_markup=
    InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='На главную', callback_data='main')
            ]
        ]
    ))


@dp.callback_query_handler(text='edit_place')
async def choice_place(call: CallbackQuery):
    places = await Place.query.gino.all()
    markup = InlineKeyboardMarkup(row_width=1)
    for one in places:
        markup.insert(InlineKeyboardButton(text=one.name, callback_data=place_cd.new(place=one.id)))
    markup.row(InlineKeyboardButton(text='Назад', callback_data='edit_info'))
    await call.message.answer('Выбери подходящее место для тренировок.'
                              'Не забывай, что тренировки очень разные,поэтому упражнения'
                              ' будут другими', reply_markup=markup)


@dp.callback_query_handler(place_cd.filter())
async def edit_place(call: CallbackQuery, callback_data: dict):
    place = int(callback_data.get('place'))
    user = await User.get(call.from_user.id)
    await user.update(place=place).apply()
    await call.message.answer('Отлично! Ваше место тренировок изменилось!', reply_markup=
    InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='На главную', callback_data='main')
            ]
        ]
    ))


@dp.callback_query_handler(text='edit_training_times')
async def choice_time(call: CallbackQuery):
    markup = InlineKeyboardMarkup(row_width=1)
    for one in range(2,7):
        markup.insert(
            InlineKeyboardButton(text=f'{one} раза',callback_data=time_cd.new(
                time=one
            ))
        )
    markup.row(
        InlineKeyboardButton(text='Назад',callback_data='edit_info')
    )
    await call.message.answer('Выбери подходящее место для тренировок.'
                              'Не забывай, что тренировки очень разные,поэтому упражнения'
                              ' будут другими', reply_markup=markup)


@dp.callback_query_handler(time_cd.filter())
async def edit_time(call: CallbackQuery, callback_data: dict):
    time = int(callback_data.get('time'))
    user = await User.get(call.from_user.id)
    await user.update(training_times=time).apply()
    await call.message.answer('Отлично! Количество тренировок в неделю изменилось!'
                              'Не забудь изменить дни тренировок', reply_markup=
                              InlineKeyboardMarkup(
                                  inline_keyboard=[
                                      [
                                          InlineKeyboardButton(text='На главную', callback_data='main')
                                      ]
                                  ]
                              ))

@dp.callback_query_handler(text='edit_user_set')
async def check_sets(call: CallbackQuery):
    sets = await Set.query.gino.all()
    markup = InlineKeyboardMarkup(row_width=1)
    for one in sets:
        goal = await Goal.get(one.goal)
        markup.insert(
            InlineKeyboardButton(text=f'{goal.name}',
                                 callback_data=sets_cd.new(set=one.id))
        )
    markup.row(
        InlineKeyboardButton(text='Назад',callback_data='edit_info')
    )
    await call.message.answer('Выбери Программу упражения',reply_markup=markup)

@dp.callback_query_handler(sets_cd.filter())
async def edit_sets(call: CallbackQuery,callback_data: dict):
    set = int(callback_data.get('set'))
    user = await UserActivity.query.where(UserActivity.user==call.from_user.id).gino.first()
    await user.update(set=set).apply()
    set = await Set.get(set) or 0
    all = await Activity.query.where((Activity.user==user.id)&(Activity.set==set.id)).gino.first() or 0
    if all == 0:
        exerices = (set.exception_1, set.exception_2, set.exception_3, set.exception_4, set.exception_5,
                    set.exception_6, set.exception_7, set.exception_8, set.exception_9, set.exception_10)
        for exercise in exerices:
            exercise = await Exercise.get(exercise) or 0
            if exercise != 0:
                repeats = (
                    exercise.repeats_1, exercise.repeats_2, exercise.repeats_3, exercise.repeats_4,
                    exercise.repeats_5)
                for repeat in repeats:
                    repeat = await Repeat.get(repeat) or 0
                    if repeat != 0:
                        total = await db.func.count(Activity.id).gino.scalar()
                        await Activity.create(
                            id=total + 1,
                            set=set.id,
                            user=call.from_user.id,
                            exercise=exercise.id,
                            repeat=repeat.id,
                            weight=None)
    await call.message.answer('Программа изменена',reply_markup=
                              InlineKeyboardMarkup(
                                  inline_keyboard=[
                                      [
                                          InlineKeyboardButton(text='На главную', callback_data='main')
                                      ]
                                  ]))

@dp.callback_query_handler(text='edit_time_training')
async def update_time_training(call: CallbackQuery):
    markup = InlineKeyboardMarkup(row_width=4)
    for time in range(25):
        if len(str(time)) < 2:
            time = f'0{time}'
        markup.insert(InlineKeyboardButton(
            text=f'{time}:00',
            callback_data=hour_cd.new(hour=time)
        ))
    markup.row(InlineKeyboardButton(text='Назад', callback_data='edit_info'))
    await call.message.answer('Выбери, во сколько у тебя будут проходить тренировки', reply_markup=markup)


@dp.callback_query_handler(hour_cd.filter())
async def edit_time_training(call: CallbackQuery, callback_data: dict):
    time = int(callback_data.get('hour'))
    user = await UserActivity.query.where(UserActivity.user == call.from_user.id).gino.first()
    await user.update(time=time).apply()
    await call.message.answer(f'Отлично! Теперь твои тренировки будут проходить в {time}:00', reply_markup=
    InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='На главную', callback_data='main')
            ]
        ]))