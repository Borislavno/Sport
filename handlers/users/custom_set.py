from datetime import timedelta, datetime

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiogram.utils.callback_data import CallbackData

from handlers.users.user_trainings import update_set
from loader import dp, bot
from utils.db_api.gino import Section, Practice, Subsection, Set, db, Activity, User
from utils.states import Custom_Set

sunsection_cd = CallbackData('subsection', 'id_section')
practice_cd = CallbackData('practice', 'id_section', 'id_subsection','video')
choice_app_cd = CallbackData('choice', 'id_section', 'id_subsection', 'id_practice')
new_cd = CallbackData('new', 'id_practice')


@dp.callback_query_handler(state='finish_exception', text='new_exception')
@dp.callback_query_handler(text='custom_set',state='*')
async def begin_custom_set(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_state = await state.get_state()
    if current_state =='finish_exception':
        all = await Section.query.gino.all() or 0
        markup = InlineKeyboardMarkup(row_width=2)
        for one in all:
            button = one.name
            markup.insert(
                InlineKeyboardButton(
                    text=button, callback_data=sunsection_cd.new(id_section=one.id)
                )
            )
        await call.message.answer('Выбери категорию упражнений', reply_markup=markup)
    if len(data.keys()) > 39:
        await call.message.answer('Программа слишком большая для меня! Пока обойдемся 10 упражнениями', reply_markup=
        InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='Создать программу',
                                         callback_data='days_of_set')
                ],
                [
                    InlineKeyboardButton(text='Сбросить программу тренировок',
                                         callback_data='reset')
                ]
            ]
        ))
    if data == {}:
        all = await Section.query.gino.all() or 0
        markup = InlineKeyboardMarkup(row_width=2)
        for one in all:
            button = one.name
            markup.insert(
                InlineKeyboardButton(
                    text=button, callback_data=sunsection_cd.new(id_section=one.id)
                )
            )
        markup.row(
            InlineKeyboardButton(text='На главную',callback_data='main')
        )
        await call.message.answer('Выбери категорию упражнений', reply_markup=markup)


@dp.callback_query_handler(sunsection_cd.filter(), state='*')
async def all_sunsections(call: CallbackQuery, callback_data: dict):
    id_section = int(callback_data.get('id_section'))
    all_sub = await Subsection.query.where(Subsection.section==id_section).gino.all() or 0
    if all_sub ==0:
        await call.message.answer('Упражнений нет',reply_markup=
                                  InlineKeyboardMarkup(
                                      inline_keyboard=[
                                          InlineKeyboardButton(
                                              text='Назад', callback_data='custom_set'
                                          )
                                      ]
                                  ))
    else:
        markup = InlineKeyboardMarkup(row_width=2)
        for one in all_sub:
            markup.insert(
                InlineKeyboardButton(
                    text=f'{one.name}', callback_data=practice_cd.new(id_section=id_section,
                                                                      id_subsection=one.id,
                                                                      video=0)
                )
            )
        markup.row(
            InlineKeyboardButton(
                text='Назад', callback_data='custom_set'
            )
        )
        await call.message.answer(text='Выбери подкатегорию', reply_markup=markup)


@dp.callback_query_handler(practice_cd.filter(), state='*')
async def all_practice(call: CallbackQuery, callback_data: dict):
    id_section = int(callback_data.get('id_section'))
    id_subsection = int(callback_data.get('id_subsection'))
    video = int(callback_data.get('video'))
    user = await User.get(call.from_user.id)
    all_practice = await Practice.query.where((Practice.place==user.place)&(Practice.section==id_section)&(Practice.subsection==id_subsection)).gino.all() or 0
    if video > 0:
        await bot.delete_message(chat_id=call.message.chat.id,message_id=video)
    markup = InlineKeyboardMarkup(row_width=2)
    if all_practice ==0:
        await call.message.answer('Упражнений нет',reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text='Вернуться к выбору категорий', callback_data=sunsection_cd.new(id_section=id_section)
                    )
                ]
            ]
        ))
    else:
        for one in all_practice:
            markup.insert(
                InlineKeyboardButton(
                    text=f'{one.name}', callback_data=choice_app_cd.new(id_section=id_section,
                                                                        id_subsection=id_subsection,
                                                                        id_practice=one.id)
                )
            )
        markup.row(
            InlineKeyboardButton(
                text='Вернуться к выбору категорий', callback_data=sunsection_cd.new(id_section=id_section)
            )
        )
        await call.message.answer('Выбери упражнение', reply_markup=markup)



@dp.callback_query_handler(choice_app_cd.filter(), state='*')
async def all_sections(call: CallbackQuery, callback_data: dict):
    id_section = int(callback_data.get('id_section'))
    id_subsection = int(callback_data.get('id_section'))
    id_practice = int(callback_data.get('id_practice'))
    practice = await Practice.get(id_practice)
    video = await call.message.answer_animation(animation=practice.image)
    text = f'Упражнение : {practice.name}\n'
    markup = InlineKeyboardMarkup(row_width=2)
    markup.insert(
        InlineKeyboardButton(
            text='Выбрать это упражнение', callback_data=new_cd.new(id_practice=id_practice)
        )
    )
    markup.row(
        InlineKeyboardButton(
            text='Вернуться к выбору упражнений',
            callback_data=practice_cd.new(id_section=id_section,
                                          id_subsection=id_subsection,
                                          video=video.message_id))
    )
    await call.message.answer(text=text, reply_markup=markup)


@dp.callback_query_handler(new_cd.filter(), state='*')
async def custom_set(call: CallbackQuery, state: FSMContext, callback_data: dict):
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id - 1)
    id_practice = int(callback_data.get('id_practice'))
    data = await state.get_data()
    if len(data.keys()) == 0:
        await state.update_data(exception_1=id_practice)
    if len(data.keys()) == 4:
        await state.update_data(exception_2=id_practice)
    if len(data.keys()) == 8:
        await state.update_data(exception_3=id_practice)
    if len(data.keys()) == 12:
        await state.update_data(exception_4=id_practice)
    if len(data.keys()) == 16:
        await state.update_data(exception_5=id_practice)
    if len(data.keys()) == 20:
        await state.update_data(exception_6=id_practice)
    if len(data.keys()) == 24:
        await state.update_data(exception_7=id_practice)
    if len(data.keys()) == 28:
        await state.update_data(exception_8=id_practice)
    if len(data.keys()) == 32:
        await state.update_data(exception_9=id_practice)
    if len(data.keys()) == 36:
        await state.update_data(exception_10=id_practice)
    await call.message.answer('Введи количество подходов')
    await Custom_Set.Approaches.set()
    if len(data.keys()) > 40:
        await call.answer('Программа слишком большая для меня! Пока обойдемся 10 упражнениями')
        await state.set_state('finish_custom_set')


@dp.message_handler(state=Custom_Set.Approaches)
async def users_approaches(message: Message, state: FSMContext):
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    data = await state.get_data()
    approaches = message.text
    if approaches.isdigit():
        if len(data.keys()) == 37:
            await state.update_data(approaches_10=approaches)
        if len(data.keys()) == 33:
            await state.update_data(approaches_9=approaches)
        if len(data.keys()) == 29:
            await state.update_data(approaches_8=approaches)
        if len(data.keys()) == 25:
            await state.update_data(approaches_7=approaches)
        if len(data.keys()) == 21:
            await state.update_data(approaches_6=approaches)
        if len(data.keys()) == 17:
            await state.update_data(approaches_5=approaches)
        if len(data.keys()) == 13:
            await state.update_data(approaches_4=approaches)
        if len(data.keys()) == 9:
            await state.update_data(approaches_3=approaches)
        if len(data.keys()) == 5:
            await state.update_data(approaches_2=approaches)
        if len(data.keys()) == 1:
            await state.update_data(approaches_1=approaches)
        await message.answer('Введи количество упражнений в подходе')
        await Custom_Set.Repeats.set()
    else:
        await message.answer('Введи числовое значение')
        return


@dp.message_handler(state=Custom_Set.Repeats)
async def users_repeats(message: Message, state: FSMContext):
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    data = await state.get_data()
    repeats = message.text
    if repeats.isdigit():
        if len(data.keys()) == 38:
            await state.update_data(repeats_10=repeats)
        if len(data.keys()) == 34:
            await state.update_data(repeats_9=repeats)
        if len(data.keys()) == 30:
            await state.update_data(repeats_8=repeats)
        if len(data.keys()) == 26:
            await state.update_data(repeats_7=repeats)
        if len(data.keys()) == 22:
            await state.update_data(repeats_6=repeats)
        if len(data.keys()) == 18:
            await state.update_data(repeats_5=repeats)
        if len(data.keys()) == 14:
            await state.update_data(repeats_4=repeats)
        if len(data.keys()) == 10:
            await state.update_data(repeats_3=repeats)
        if len(data.keys()) == 6:
            await state.update_data(repeats_2=repeats)
        if len(data.keys()) == 2:
            await state.update_data(repeats_1=repeats)
        await message.answer('Введи, сколько минут у тебя будет перерыв между подходами\nЕсли нет перерыва,введи 0')
        await Custom_Set.Breaks.set()
    else:
        await message.answer('Введи числовое значение')
        return


@dp.message_handler(state=Custom_Set.Breaks)
async def users_breaks(message: Message, state: FSMContext):
    data = await state.get_data()
    break_time = message.text
    text = 'Вы выбрали следующие тренировки :\n'
    if break_time.isdigit():
        if len(data.keys()) == 3:
            await state.update_data(break_1=int(break_time))
        if len(data.keys()) == 7:
            await state.update_data(break_2=int(break_time))
        if len(data.keys()) == 11:
            await state.update_data(break_3=int(break_time))
        if len(data.keys()) == 15:
            await state.update_data(break_4=int(break_time))
        if len(data.keys()) == 19:
            await state.update_data(break_5=int(break_time))
        if len(data.keys()) == 23:
            await state.update_data(break_6=int(break_time))
        if len(data.keys()) == 27:
            await state.update_data(break_7=int(break_time))
        if len(data.keys()) == 31:
            await state.update_data(break_8=int(break_time))
        if len(data.keys()) == 35:
            await state.update_data(break_9=int(break_time))
        if len(data.keys()) == 39:
            await state.update_data(break_10=int(break_time))
        data = await state.get_data()
        if len(data.keys()) >= 0:
            approaches_1 = int(data['approaches_1'])
            repeats_1 = int(data['repeats_1'])
            break_1 = int(data['break_1'])
            exception = await Practice.get(int(data['exception_1']))
            text = text + f'{exception.name} по {repeats_1} повторений и {approaches_1} подхода, с перерывом {break_1} минут\n'
        if len(data.keys()) >= 7:
            repeats_2 = int(data['repeats_2'])
            approaches_2 = int(data['approaches_2'])
            break_2 = int(data['break_2'])
            exception = await Practice.get(int(data['exception_2']))
            text = text + f'{exception.name} по {repeats_2} повторений и {approaches_2} подхода, с перерывом {break_2} минут\n'
        if len(data.keys()) >= 11:
            approaches_3 = int(data['approaches_3'])
            repeats_3 = int(data['repeats_3'])
            break_3 = int(data['break_3'])
            exception = await Practice.get(int(data['exception_3']))
            text = text + f'{exception.name} по {repeats_3} повторений и {approaches_3} подхода, с перерывом {break_3} минут\n'
        if len(data.keys()) >= 15:
            approaches_4 = int(data['approaches_4'])
            repeats_4 = int(data['repeats_4'])
            break_4 = int(data['break_4'])
            exception = await Practice.get(int(data['exception_4']))
            text = text + f'{exception.name} по {repeats_4} повторений и {approaches_4} подхода, с перерывом {break_4} минут\n'
        if len(data.keys()) >= 19:
            approaches_5 = int(data['approaches_5'])
            repeats_5 = int(data['repeats_5'])
            break_5 = int(data['break_5'])
            exception = await Practice.get(int(data['exception_5']))
            text = text + f'{exception.name} по {repeats_5} повторений и {approaches_5} подхода, с перерывом {break_5} минут\n'
        if len(data.keys()) >= 23:
            approaches_6 = int(data['approaches_6'])
            repeats_6 = int(data['repeats_6'])
            break_6 = int(data['break_6'])
            exception = await Practice.get(int(data['exception_6']))
            text = text + f'{exception.name} по {repeats_6} повторений и {approaches_6} подхода, с перерывом {break_6} минут\n'
        if len(data.keys()) >= 27:
            approaches_7 = int(data['approaches_7'])
            repeats_7 = int(data['repeats_7'])
            break_7 = int(data['break_7'])
            exception = await Practice.get(int(data['exception_7']))
            text = text + f'{exception.name} по {repeats_7} повторений и {approaches_7} подхода, с перерывом {break_7} минут\n'
        if len(data.keys()) >= 31:
            approaches_8 = int(data['approaches_8'])
            repeats_8 = int(data['repeats_8'])
            break_8 = int(data['break_8'])
            exception = await Practice.get(int(data['exception_8']))
            text = text + f'{exception.name} по {repeats_8} повторений и {approaches_8} подхода, с перерывом {break_8} минут\n'
        if len(data.keys()) >= 35:
            approaches_9 = int(data['approaches_9'])
            repeats_9 = int(data['repeats_9'])
            break_9 = int(data['break_9'])
            exception = await Practice.get(int(data['exception_9']))
            text = text + f'{exception.name} по {repeats_9} повторений и {approaches_9} подхода, с перерывом {break_9} минут\n'
        if len(data.keys()) >= 39:
            approaches_10 = int(data['approaches_10'])
            repeats_10 = int(data['repeats_10'])
            exception = await Practice.get(int(data['exception_10']))
            break_10 = int(data['break_10'])
            text = text + f'{exception.name} по {repeats_10} повторений и {approaches_10} подхода, с перерывом {break_10} минут\n'
        await message.answer(text, reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='Добавить еще одно', callback_data='new_exception')
                ],
                [
                    InlineKeyboardButton(text='Создать программу', callback_data='days_of_set')
                ],
                [
                    InlineKeyboardButton(text='Сбросить программу', callback_data='reset_set')
                ]
            ]
        ))
        await state.set_state('finish_exception')
    else:
        await message.answer('Введи числовое значение')
        return


@dp.callback_query_handler(state='finish_exception',text='reset_set')
async def cancel_create_set(call: CallbackQuery,state: FSMContext):
    await state.finish()
    await call.message.answer('Ты отменил(a) создание собственной программы тренировок',
                              reply_markup=InlineKeyboardMarkup(
                                  inline_keyboard=[
                                      [
                                          InlineKeyboardButton(text='На главную', callback_data='main')
                                      ]
                                  ]
                              ))



@dp.callback_query_handler(text='days_of_set', state='finish_exception')
async def days_set(call: CallbackQuery, state: FSMContext):
    await state.set_state('finish')
    markup = InlineKeyboardMarkup(row_width=4)
    for one in range(1, 21):
        markup.insert(
            InlineKeyboardButton(
                text=f'{one}', callback_data=f'{one}')
        )
    await call.message.answer('Выбери,сколько тренировочных дней будет в твоей программе', reply_markup=markup)


@dp.callback_query_handler(state='finish')
async def confirming_set(call: CallbackQuery, state: FSMContext):
    days = call.data
    data = await state.get_data()
    count_set = int(await db.func.count(Set.id).gino.scalar()) + 1
    count_activity = int(await db.func.count(Activity.id).gino.scalar()) + 1
    user = await User.get(call.from_user.id)
    exception_1 = data.get('exception_1')
    set = await Set.create(id=count_set,
                           author=call.from_user.id,
                           goal=int(user.goal),
                           days=int(days),
                           exception_1=count_activity)
    await Activity.create(id=count_activity,
                          set=count_set,
                          practice=exception_1,
                          count_approaches=int(data['approaches_1']),
                          count_repeats=int(data['repeats_1']),
                          breaks=int(data['break_1']))


    if len(data.keys()) >= 7:
        count_activity = int(await db.func.count(Activity.id).gino.scalar()) + 1
        await Activity.create(id=count_activity,
                              set=count_set,
                              practice=int(data.get('exception_2')),
                              count_approaches=int(data['approaches_2']),
                              count_repeats=int(data['repeats_2']),
                              breaks=int(data['break_2']))
        await set.update(exception_2=count_activity).apply()

    if len(data.keys()) >= 11:
        count_activity = int(await db.func.count(Activity.id).gino.scalar()) + 1
        await Activity.create(id=count_activity,
                              set=count_set,
                              practice=int(data.get('exception_3')),
                              count_approaches=int(data['approaches_3']),
                              count_repeats=int(data['repeats_3']),
                              breaks=int(data['break_3']))
        await set.update(exception_3=count_activity).apply()
    if len(data.keys()) >= 15:
        count_activity = int(await db.func.count(Activity.id).gino.scalar()) + 1
        await Activity.create(id=count_activity,
                              set=count_set,
                              practice=int(data.get('exception_4')),
                              count_approaches=int(data['approaches_4']),
                              count_repeats=int(data['repeats_4']),
                              breaks=int(data['break_4']))
        await set.update(exception_4 = count_activity).apply()
    if len(data.keys()) >= 19:
        count_activity = int(await db.func.count(Activity.id).gino.scalar()) + 1
        await Activity.create(id=count_activity,
                              set=count_set,
                              practice=int(data.get('exception_5')),
                              count_approaches=int(data['approaches_5']),
                              count_repeats=int(data['repeats_5']),
                              breaks=int(data['break_5']))
        await set.update(exception_5 = count_activity).apply()
    if len(data.keys()) >= 23:
        count_activity = int(await db.func.count(Activity.id).gino.scalar()) + 1
        await Activity.create(id=count_activity,
                              set=count_set,
                              practice=int(data.get('exception_6')),
                              count_approaches=int(data['approaches_6']),
                              count_repeats=int(data['repeats_6']),
                              breaks=int(data['break_6']))
        await set.update(exception_6 = count_activity).apply()
    if len(data.keys()) >= 27:
        count_activity = int(await db.func.count(Activity.id).gino.scalar()) + 1
        await Activity.create(id=count_activity,
                              set=count_set,
                              practice=int(data.get('exception_7')),
                              count_approaches=int(data['approaches_7']),
                              count_repeats=int(data['repeats_7']),
                              breaks=int(data['break_7']))
        await set.update(exception_7 = count_activity).apply()
    elif len(data.keys()) >= 31:
        count_activity = int(await db.func.count(Activity.id).gino.scalar()) + 1
        await Activity.create(id=count_activity,
                              set=count_set,
                              practice=int(data.get('exception_8')),
                              count_approaches=int(data['approaches_8']),
                              count_repeats=int(data['repeats_8']),
                              breaks=int(data['break_8']))
        await set.update(exception_8 = count_activity).apply()
    elif len(data.keys()) >= 35:
        count_activity = int(await db.func.count(Activity.id).gino.scalar()) + 1
        await Activity.create(id=count_activity,
                              set=count_set,
                              practice=int(data.get('exception_9')),
                              count_approaches=int(data['approaches_9']),
                              count_repeats=int(data['repeats_9']),
                              breaks=int(data['break_9']))
        await set.update(exception_9 = count_activity).apply()
    elif len(data.keys()) >= 39:
        count_activity = int(await db.func.count(Activity.id).gino.scalar()) + 1
        await Activity.create(id=count_activity,
                              set=count_set,
                              practice=int(data.get('exception_10')),
                              count_approaches=int(data['approaches_10']),
                              count_repeats=int(data['repeats_10']),
                              breaks=int(data['break_10']))
        await set.update(exception_10 = count_activity).apply()
    now = datetime.utcnow()
    today = now.date()
    tomorrow = today + timedelta(days=1)
    day_after_tomorrow = tomorrow + timedelta(days=1)
    await state.finish()
    await call.message.answer('Выбери день, когда начнешь заниматься',
                              reply_markup=InlineKeyboardMarkup(
                                  inline_keyboard=[
                                      [
                                          InlineKeyboardButton(text=f'Сегодня, {today.day}.{today.month}',
                                                               callback_data=update_set.new(
                                                                   id_set=count_set,
                                                                   begin_day=today.day,
                                                                   begin_month=today.month
                                                               ))
                                      ],
                                      [
                                          InlineKeyboardButton(text=f'Завтра, {tomorrow.day}.{tomorrow.month}',
                                                               callback_data=update_set.new(
                                                                   id_set=count_set,
                                                                   begin_day=tomorrow.day,
                                                                   begin_month=tomorrow.month
                                                               ))
                                      ],
                                      [
                                          InlineKeyboardButton(
                                              text=f'Послезавтра, {day_after_tomorrow.day}.{day_after_tomorrow.month}',
                                              callback_data=update_set.new(
                                                  id_set=count_set,
                                                  begin_day=day_after_tomorrow.day,
                                                  begin_month=day_after_tomorrow.month
                                              ))
                                      ]
                                  ]
                              ))
