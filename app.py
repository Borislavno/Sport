from handlers.users.progress import progress
from handlers.users.training import training
from loader import scheduler
from utils.db_api import gino
from utils.notify_admins import on_startup_notify

def scheduler_jobs():
    scheduler.add_job(training, "interval", minutes=1, args=(dp,))
    scheduler.add_job(progress, "interval", minutes=1, args=(dp,))

async def on_startup(dispatcher):
    await gino.create_db(dispatcher)
    # await on_startup_notify(dispatcher)
    scheduler_jobs()


if __name__ == '__main__':
    scheduler.start()
    from aiogram import executor, Dispatcher
    from handlers import dp
    from middlewares import dp

    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
