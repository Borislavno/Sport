from aiogram import Dispatcher

from utils.db_api.gino import User, UserActivity, Activity, Set, Exercise, Repeat, db


async def check_user_active(dp: Dispatcher):
    users = await UserActivity.query.gino.all()
    for one in users:
        user = await User.get(one.user)
        set = await Set.get(one.set) or 0
        if set != 0:
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
                                    user=user.id,
                                    exercise=exercise.id,
                                    repeat=repeat.id,
                                    weight=None
                                )
