from datetime import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message, ReplyKeyboardMarkup, \
    KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.callback_data import CallbackData

from loader import dp, bot
from utils.db_api.gino import Goal, User, Trainer, Place, Progress, Week, db
from utils.states import Newbie

gender_cd = CallbackData('user', 'sex')


async def format_phone_number(phone_number: str) -> str:
    """
    Оствляет в сроке только числа и если первое число в строке 8, то заменяет его на 7.
    :param phone_number:
    :return:
    """
    phone_number = ''.join(i for i in phone_number if i.isdigit())
    phone_number = phone_number[:1].replace('8', '7') + phone_number[1:]
    return phone_number


@dp.callback_query_handler(text='cancel_reg', state='*')
async def cancel(call: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        await state.finish()
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Я смогу, ещё раз!', callback_data='user_registration')],
        ]
    )
    reply = 'Ты не смог ответить на такие простые вопросы!?'
    await call.message.answer_sticker(sticker='CAACAgIAAxkBAAIFeF-MOIbW2h50MT8-zV0lNghLaeMQAAKcAQACJQNSD4NGjRGcwhDcGwQ')
    await call.message.answer(text=reply, reply_markup=keyboard_markup)


@dp.callback_query_handler(text='user_registration')
async def user_registration(call: CallbackQuery, state: FSMContext):
    await Newbie.Name.set()
    reply = 'Давай начнём твой пусть к здоровому и красивому телу со знакомства. Как тебя зовут?'
    await call.message.answer_sticker(sticker='CAACAgIAAxkBAAIFfF-MOL11XOMpkauOiYToE06-yYO4AAKWAQACJQNSD1GYpaVpXb4FGwQ')
    await call.message.answer(text=reply)


@dp.message_handler(text='/start')
async def user_register(message: types.Message, state: FSMContext):
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    reply = 'Давай начнём твой пусть к здоровому и красивому телу со знакомства. Как тебя зовут?'
    await message.answer_sticker(sticker='CAACAgIAAxkBAAIFfF-MOL11XOMpkauOiYToE06-yYO4AAKWAQACJQNSD1GYpaVpXb4FGwQ')
    await message.answer(text=reply)
    await Newbie.Name.set()


@dp.message_handler(state=Newbie.Name)
async def user_name(message: types.Message, state: FSMContext):
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 2)
    keyboard_markup = InlineKeyboardMarkup()
    name = message.text
    if name and len(name) <= 50:
        await state.update_data(name=name)
        reply = f'Приятно познакомиться, {name}!\n' \
                f'Твой пол?\U0001F447'
        keyboard_markup.add(
            InlineKeyboardButton(text='\U0001F468', callback_data=gender_cd.new(sex='Мужчина')),
            InlineKeyboardButton(text='\U0001F469', callback_data=gender_cd.new(sex='Женщина')),
        )
        await message.answer_sticker(sticker='CAACAgIAAxkBAAIFiF-MOY4VLOoEn9Y1XmBKsVzszxM6AAKbAQACJQNSDyYGRRDR6Z3GGwQ')
        await Newbie.Gender.set()
    else:
        reply = 'К сожалению, слишком длинное имя, не более 50 символов, введи ещё раз.'

    await message.answer(text=reply, reply_markup=keyboard_markup)


@dp.callback_query_handler(gender_cd.filter(), state=Newbie.Gender)
async def user_sex(call: CallbackQuery, state: FSMContext, callback_data: dict):
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id - 1)
    user_sex = callback_data.get('sex')
    await state.update_data(gender=user_sex)
    reply = f'Отлично!\n' \
            f'Сколько тебе лет?'
    await call.message.answer(text=reply)
    await Newbie.Age.set()


@dp.message_handler(state=Newbie.Age)
async def user_age(message: Message, state: FSMContext):
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    age = message.text
    if age.isdigit() and len(age) <= 3:
        await state.update_data(age=age)
        await Newbie.Weight.set()
        reply = 'Какой у тебя вес сейчас? Укажи цифрами в кг. Например 84.200'
        sticker = await message.answer_sticker(
            sticker='CAACAgIAAxkBAAIFdF-MOFyrWxfeaz4VsxqA-L0cMglzAAKKAQACJQNSDxuo4MQYC7YyGwQ')
        await message.answer(text=reply)
    else:
        reply = 'Укажи пожалуйста возраст в цифрах. Например 21'
        await message.answer(text=reply)



@dp.message_handler(state=Newbie.Weight)
async def user_weight(message: Message, state: FSMContext):
    weight = message.text
    if weight and len(weight) <= 6:
        await state.update_data(weight=weight)
        await Newbie.Height.set()
        reply = 'Какой у тебя рост? Напиши цифрами в сантиметрах.'
        await message.answer(text=reply)
    else:
        reply = 'Пожалуйста укажи весь только цифрами.'
        await message.answer(text=reply)
        return


@dp.message_handler(state=Newbie.Height)
async def user_height(message: Message, state: FSMContext):
    height = message.text
    if height.isdigit() and len(height) <= 3:
        await state.update_data(height=height)
        await Newbie.Goal.set()
        keyboard_markup = InlineKeyboardMarkup(row_width=1)
        goals = await Goal.query.gino.all()
        for goal in goals:
            keyboard_markup.insert(
                InlineKeyboardButton(text=goal.name, callback_data=goal.id)
            )
        keyboard_markup.row(
            InlineKeyboardButton(text='Слишком сложные вопросы, сдаюсь!', callback_data='cancel_reg')
        )
        reply = 'Отлично! Какая у тебя сейчас цель в тренировках? Выбери нужные вариант.'
        await message.answer(text=reply, reply_markup=keyboard_markup)
    else:
        reply = 'Пожалуйста укажи весь только цифрами.'
        await message.answer(text=reply, reply_markup=keyboard_markup)


@dp.callback_query_handler(state=Newbie.Goal)
async def user_goal(call: CallbackQuery, state: FSMContext):
    keyboard_markup = InlineKeyboardMarkup()
    await state.update_data(goal_id=int(call.data))
    await Newbie.Lifestyle.set()
    reply = 'Хорошая цель! Какой у тебя образ жизни?'
    keyboard_markup.add(InlineKeyboardButton(text='Не очень подвижный', callback_data='неподвижный'))
    keyboard_markup.add(InlineKeyboardButton(text='Малоподвижный', callback_data='малоподвижный'))
    keyboard_markup.add(InlineKeyboardButton(text='Подвижный', callback_data='подвижный'))
    keyboard_markup.add(InlineKeyboardButton(text='Очень подвижный', callback_data='очень подвижный'))
    await call.message.answer(text=reply, reply_markup=keyboard_markup)


@dp.callback_query_handler(state=Newbie.Lifestyle)
async def user_goal(call: CallbackQuery, state: FSMContext):
    keyboard_markup = InlineKeyboardMarkup(row_width=1)
    await state.update_data(lifestyle=call.data)
    await Newbie.Place.set()
    reply = 'Хорошая цель! Ты будешь заниматсья дома или в зале?'
    places = await Place.query.gino.all()
    for place in places:
        keyboard_markup.insert(
            InlineKeyboardButton(text=place.name, callback_data=place.id)
        )
    keyboard_markup.row(
        InlineKeyboardButton(text='Слишком сложные вопросы, сдаюсь!', callback_data='cancel_reg')
    )
    await call.message.answer(text=reply, reply_markup=keyboard_markup)


@dp.callback_query_handler(state=Newbie.Place)
async def workout_times(call: CallbackQuery, state: FSMContext):
    keyboard_markup = InlineKeyboardMarkup()
    place = call.data
    await Newbie.Times.set()
    await state.update_data(place=place)
    keyboard_markup.add(InlineKeyboardButton(text='2 раза', callback_data='2'))
    keyboard_markup.add(InlineKeyboardButton(text='3 раза', callback_data='3'))
    keyboard_markup.add(InlineKeyboardButton(text='4 раза', callback_data='4'))
    keyboard_markup.add(InlineKeyboardButton(text='5 раза', callback_data='5'))
    keyboard_markup.add(InlineKeyboardButton(text='6 раза', callback_data='6'))
    reply = f'Сколько раз в неделю ты сможешь заниматься?'
    await call.message.answer(text=reply, reply_markup=keyboard_markup)


@dp.callback_query_handler(state=Newbie.Times)
async def workout_training(call: CallbackQuery, state: FSMContext):
    training_times = call.data
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True,
                                   keyboard=[
                                       [
                                           KeyboardButton(text="📱",
                                                          request_contact=True)
                                       ]
                                   ])
    await Newbie.PhoneNumber.set()
    await state.update_data(training_times=training_times)
    reply = f'Введи свой номер телефона для связи с трениром или можешь нажать на кнопку снизу,' \
            f' мы получим твой номер телефона\n' \
            f'Можешь не переживать, посторонние не узнают твой номер 😉 .'
    await call.message.answer(text=reply, reply_markup=keyboard)


@dp.message_handler(content_types=types.ContentType.CONTACT, state=Newbie.PhoneNumber)
@dp.message_handler(state=Newbie.PhoneNumber)
async def user_phone_number(message: Message, state: FSMContext):
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    phone_number = message.text or str(message.contact.phone_number)
    phone = await format_phone_number(phone_number)
    if len(phone) == 11 or 12 and phone.isdigit() == True:
        await state.update_data(phone=phone)
        await Newbie.Trainer.set()
        await message.answer('Ты будешь заниматься для себя, или готов быть тренером для других?', reply_markup=
        InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='Для себя', callback_data='для себя')
                ],
                [
                    InlineKeyboardButton(text='Готов быть тренером', callback_data='тренер')
                ]
            ]
        ))
    else:
        text = 'Пожалуйста укажи свой номер телефона только цифрами, в формате 89211234565 или +79211234565'
        await message.answer(text=text, reply_markup=ReplyKeyboardMarkup(resize_keyboard=True,
                                                                         keyboard=[
                                                                             [
                                                                                 KeyboardButton(text="📱",
                                                                                                request_contact=True)
                                                                             ]
                                                                         ]))


@dp.callback_query_handler(state=Newbie.Trainer)
async def user_final(call: CallbackQuery, state: FSMContext):
    if call.data == 'тренер':
        await state.update_data(is_trainer='True')
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Что-то пошло не так, тренер! Давай сначала!', callback_data='cancel_reg')],
        ]
    )
    keyboard_markup.add(InlineKeyboardButton(text='Да, всё верно!', callback_data='save_reg_user'))
    data = await state.get_data()
    name = data['name']
    gender = data['gender']
    age = data['age']
    height = data['height']
    weight = data['weight']
    goal_id = data['goal_id']
    lifestyle = data['lifestyle']
    place = await Place.get(int(data['place']))
    training_times = data['training_times']
    phone_number = data['phone']
    goal = await Goal.get(int(goal_id))
    reply = 'Давай всё проверим:\n' \
            f'Твоё имя {name} и тебе {age} лет, пол {gender}. \n' \
            f'Твоя цель : {goal.name}, образ жизни {lifestyle}, а параметры рост {height} и вес {weight} кг\n' \
            f'Место тренировок: {place.name} и ты можешь заниматься {training_times} раз(а) в неделю\n' \
            f'А для дополнительной связи телефон {phone_number}\n' \
            f'Всё верно?'
    await call.message.answer_sticker(
        sticker='CAACAgIAAxkBAAIFdl-MOILVpRMiJVvY7hMUqbQHKWLuAAKQAQACJQNSD00wsDgYgXCMGwQ')
    await call.message.answer(text=reply, reply_markup=keyboard_markup)
    await state.set_state('confirm')


@dp.callback_query_handler(text='save_reg_user', state='confirm')
async def save_reg_user(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    now = datetime.utcnow()
    user = await User.create(id=int(call.from_user.id),
                             name=call.from_user.username or str(call.from_user.id),
                             fullname=data['name'],
                             gender=data['gender'],
                             banned=False,
                             age=data['age'],
                             height=data['height'],
                             weight=data['weight'],
                             goal=int(data['goal_id']),
                             lifestyle=data['lifestyle'],
                             place=int(data['place']),
                             training_times=int(data['training_times']),
                             phone_number=data['phone'])
    for one in data.keys():
        if one == 'is_trainer':
            total = await db.func.count(Trainer.id).gino.scalar() or 0
            await user.update(is_trainer=True).apply()
            await Trainer.create(id=total+1,
                                 user=call.from_user.id)

    total = await db.func.count(Progress.id).gino.scalar() or 0
    progress = await Progress.create(
        id=total+1,
        user=call.from_user.id,
        update_week=1
    )
    total = await db.func.count(Week.id).gino.scalar() or 0
    week = await Week.create(
        id=total+1,
        progress=progress.id,
        begin=now.date(),
        day_one=int(data['weight'])
    )
    await progress.update(week_1=week.id).apply()
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='На главную', callback_data='main')],
        ]
    )
    reply = 'Молодец! Это твой первый шаг к здоровому и красивому телу! ' \
            'Пока я составляю для тебя подходящую программу тренировок, можешь почитать полезную информацию в ' \
            'разделе "Федя в чём твой секрет!?" на главной странице. Когда тренировка будет готова, она появится в ' \
            'разделе "Мои тренировки".'
    await state.finish()
    await call.message.answer_sticker(sticker='CAACAgIAAxkBAAIFjF-MPNEUNfyG9YCZ3desbosToUwNAAKAAQACJQNSD7tHz-822-uaGwQ')
    await call.message.answer(text=reply, reply_markup=keyboard_markup)
