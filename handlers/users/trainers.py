from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from data import config
from filters import Trainers
from loader import dp, bot
from utils.db_api.gino import Trainer, User, Progress

trainer_conrirm_cd = CallbackData('confirmed', 'id_trainer')
delete_trainer_cd = CallbackData('delete', 'id_trainer')
apprentice_trainer_cd = CallbackData('apprentice', 'id_apprentice')


@dp.callback_query_handler(trainer_conrirm_cd.filter(), state='*')
async def update_trainer_status(call: CallbackQuery, callback_data: dict):
    id_trainer = int(callback_data.get('id_trainer'))
    trainer = await Trainer.query.where(Trainer.user == id_trainer).gino.first()
    await trainer.update(confirmed=True).apply()
    await call.message.answer('Тренер подтвержен')
    await bot.send_message(chat_id=id_trainer, text='Поздравляем! Ваша заявка на тренера подтверждена',
                           reply_markup=InlineKeyboardMarkup(
                               inline_keyboard=[
                                   [
                                       InlineKeyboardButton(text='На главную',callback_data='main')
                                   ]
                               ]
                           ))


@dp.callback_query_handler(delete_trainer_cd.filter())
async def delete_trainer(call: CallbackQuery, callback_data: dict):
    id_trainer = int(callback_data.get('id_trainer'))
    trainer = await Trainer.query.where(Trainer.user == id_trainer).gino.first() or None
    user = await User.get(id_trainer) or None
    if trainer and user == None:
        await call.message.answer('Заявка уже рассмотрена и отказана')
    else:
        progress = await Progress.query.where(Progress.user ==id_trainer).gino.first()
        await progress.delete()
        await trainer.delete()
        await user.delete()
        await call.message.answer('Заявка отклонена. Пользователь удален')
        await bot.send_message(chat_id=id_trainer, text='К сожалению Вашу заявку отклоники!\n'
                                                        'Зарегистрируйтесь в боте заново')


@dp.callback_query_handler(Trainers(), text='main')
async def test(call: CallbackQuery, state: FSMContext):
    trainer = await Trainer.query.where(Trainer.user == call.from_user.id).gino.first()
    user = await User.get(call.from_user.id)
    markup = InlineKeyboardMarkup(row_width=1)
    if trainer.confirmed == False:
        markup.insert(
            InlineKeyboardButton(text='Оставить заявку на тренера',
                                 callback_data='confirm_trainer')
        )
        await call.message.answer(f'Привет {user.fullname}! Я должен проверить что ты достаточно классифицирован,'
                                  f' чтобы доверить здоровье пользователю',
                                  reply_markup=markup)
    if trainer.confirmed == True and user.timezone == None and user.days_of_week == None:
        markup.insert(
            InlineKeyboardButton(text='Настроить часовой пояс',
                                 callback_data='user_timezone')
        )
        await call.message.answer(f'Привет {user.fullname}! Осталось настроить наши часовые пояса,'
                                  f' чтобы могли работать слаженно', reply_markup=markup)
    if trainer.confirmed == True and user.timezone != None and user.days_of_week != None:
        markup.insert(InlineKeyboardButton(text='Мои тренировки', callback_data='my_training'))
        markup.insert(InlineKeyboardButton(text='Мои ученики', callback_data='my_stydies'))
        markup.insert(InlineKeyboardButton(text='Изменить мои данные', callback_data='edit_info'))
        await call.message.answer(f'Привет {user.fullname}! Ты можешь самостоятельно составить программу для себя,'
                                  f'посмотреть список твоих учеников, отредактировать собственные данные',
                                  reply_markup=markup)



@dp.message_handler(Trainers(), CommandStart())
async def trainer_menu(message: Message, state: FSMContext):
    trainer = await Trainer.query.where(Trainer.user == message.from_user.id).gino.first()
    user = await User.get(message.from_user.id)
    markup = InlineKeyboardMarkup(row_width=1)
    if trainer.confirmed == False:
        markup.insert(
            InlineKeyboardButton(text='Оставить заявку на тренера',callback_data='confirm_trainer')
        )
        await message.answer(f'Привет {user.fullname}! Я должен проверить что ты достаточно классифицирован,'
                             f' чтобы доверить здоровье пользователю',
                             reply_markup=markup)
    if trainer.confirmed == True and user.timezone == None and user.days_of_week == None:
        markup.insert(
            InlineKeyboardButton(text='Настроить часовой пояс',callback_data='user_timezone')
        )
        await message.answer(f'Привет {user.fullname}! Осталось настроить наши часовые пояса,'
                             f' чтобы могли работать слаженно', reply_markup=markup)
    if trainer.confirmed == True and user.timezone != None and user.days_of_week != None:
        markup.insert(InlineKeyboardButton(text='Мои тренировки', callback_data='my_training'))
        markup.insert(InlineKeyboardButton(text='Мои ученики', callback_data='my_stydies'))
        markup.insert(InlineKeyboardButton(text='Изменить мои данные', callback_data='edit_info'))
        await message.answer(f'Привет {user.fullname}! Ты можешь самостоятельно составить программу для себя,'
                             f'посмотреть список твоих учеников, отредактировать собственные данные',
                             reply_markup=markup)



@dp.callback_query_handler(Trainers(), text='Repeat', state='trainer_finish')
@dp.callback_query_handler(Trainers(), text='confirm_trainer')
async def begin_confirm(call: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state == 'trainer_finish':
        await state.reset_data()
    await call.message.answer('Напишите сколько у Вас лет опыта работы тренером')
    await state.set_state('Experience')


@dp.message_handler(Trainers(), state='Experience')
async def experience_trainer(message: Message, state: FSMContext):
    Experience = message.text
    if Experience.isdigit():
        await state.update_data(experience=Experience)
        await message.answer('Введите свое образование')
        await state.set_state('Education')
    else:
        await message.answer('Напишите в числовом значении')
        return


@dp.message_handler(Trainers(), state='Education')
async def education_trainers(message: Message, state: FSMContext):
    education = message.text
    if len(education) < 1024:
        data = await state.get_data()
        experience = data['experience']
        await state.update_data(education=education)
        text = f'Вы ввели следующие данные:\nВащ стаж: {experience} лет\nВаше образование: {education}'
        await message.answer(text=text, reply_markup=
        InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='Оставить заявку', callback_data='confirming')
                ],
                [
                    InlineKeyboardButton(text='Ввести данные повторно', callback_data='Repeat')
                ],
                [
                    InlineKeyboardButton(text='Отмена', callback_data='cancel')
                ]
            ]
        ))
        await state.set_state('trainer_finish')
    else:
        await message.answer('Слишком большой текст, введите заново')


@dp.callback_query_handler(Trainers(), state='trainer_finish', text='cancel')
async def cancelling(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.answer('Вы отменили заполнение заявки', reply_markup=
    InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='На главную', callback_data='main')
            ]
        ]
    ))


@dp.callback_query_handler(state='trainer_finish', text='confirming')
async def confirm_trainer(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    experience = int(data.get('experience'))
    education = data.get('education')
    trainer = await Trainer.query.where(Trainer.user == call.from_user.id).gino.first()
    await trainer.update(experience=experience, education=education).apply()
    trainer = await User.get(call.from_user.id)
    await state.finish()
    text = f'{trainer.name} оставил заявку для получения функционала тренера\nСтаж работы: {experience} лет\n' \
           f'Образование тренера: {education}'
    await call.message.answer('Заявка отправлена на рассмотрение')
    for one in config.ADMINS:
        await bot.send_message(chat_id=one, text=text, reply_markup=
        InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='Подтвердить заявку',
                                         callback_data=trainer_conrirm_cd.new(
                                             id_trainer=call.from_user.id
                                         ))
                ],
                [
                    InlineKeyboardButton(text='Отказать и удалить пользователя',
                                         callback_data=delete_trainer_cd.new(
                                             id_trainer=call.from_user.id
                                         ))
                ]
            ]
        ))


@dp.callback_query_handler(Trainers(), text='my_stydies')
async def trainres_stydies(call: CallbackQuery):
    stydies = await User.query.where(User.my_trainer == call.from_user.id).gino.all() or 0
    markup = InlineKeyboardMarkup()
    if stydies != 0:
        text= 'Контакты моих учеников:\n'
        for one in stydies:
            text = text + f" {one.fullname}: @{one.name} "
            # markup.insert(
            #     InlineKeyboardButton(text=f'@{one.name},{one.fullname}',
            #                          callback_data=apprentice_trainer_cd.new(id_apprentice=one.id)
            #                          )
            # )

        markup.row(
            InlineKeyboardButton(text='Назад', callback_data='main')
        )
        await call.message.answer(text,reply_markup=markup)
    else:
        await call.message.answer('У вас нет учеников', reply_markup=
        InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='На главную', callback_data='main')
                ]
            ]
        ))
