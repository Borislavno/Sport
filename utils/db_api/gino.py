from aiogram import Dispatcher
from gino import Gino
from gino.schema import GinoSchemaVisitor
from sqlalchemy import Column, BigInteger, String, Boolean, Integer, sql, ForeignKey, Date

from data import config

db = Gino()


# Документация
# http://gino.fantix.pro/en/latest/tutorials/tutorial.html
class User(db.Model):
    __tablename__ = 'users'
    query: sql.Select

    id = Column(BigInteger, primary_key=True)
    name = Column(String(64))
    fullname = Column(String(64))
    banned = Column(Boolean(), default=False)
    gender = Column(String(64))
    age = Column(String(5))
    height = Column(String(7))
    weight = Column(String(7))
    goal = Column(ForeignKey('goals.id', ondelete='RESTRICT'))
    lifestyle = Column(String(64))
    place = Column(ForeignKey('places.id', ondelete='RESTRICT'))
    phone_number = Column(String(64))
    timezone = Column(Integer(), nullable=True)
    training_times = Column(Integer())
    days_of_week = Column(String(32), nullable=True)
    is_trainer = Column(Boolean(), default=False)
    my_trainer = Column(ForeignKey('trainers.user', ondelete='RESTRICT'), nullable=True)


class Place(db.Model):
    """
    Место тренировок для сортировок упражнений
    """

    __tablename__ = 'places'
    query: sql.Select

    id = Column(Integer(), primary_key=True)
    name = Column(String(64))


class Progress(db.Model):
    """
    Прогресс пользоваля
    """
    __tablename__ = 'progress'
    query: sql.Select

    id = Column(Integer(), primary_key=True)
    user = Column(ForeignKey('users.id', ondelete='RESTRICT'))
    week_1 = Column(Integer(), nullable=True)
    week_2 = Column(Integer(), nullable=True)
    week_3 = Column(Integer(), nullable=True)
    week_4 = Column(Integer(), nullable=True)
    update_week = Column(Integer())


class Week(db.Model):
    __tablename__ = 'week'
    query: sql.Select

    id = Column(Integer, primary_key=True)
    progress = Column(ForeignKey('progress.id', onupdate='RESTRICT'))
    begin = Column(Date(), nullable=True)
    day_one = Column(Integer, nullable='True')
    day_two = Column(Integer, nullable='True')
    day_three = Column(Integer, nullable='True')
    day_four = Column(Integer, nullable='True')
    day_five = Column(Integer, nullable='True')
    day_six = Column(Integer, nullable='True')
    day_seven = Column(Integer, nullable='True')


class Trainer(db.Model):
    __tablename__ = 'trainers'
    query: sql.Select

    id = Column(Integer)
    user = Column(ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    experience = Column(Integer())
    education = Column(String(1024))
    confirmed = Column(Boolean(), default=False)
    image = Column(String(128))


class Section(db.Model):
    """
    Разделы упражнений
    """
    __tablename__ = 'sections'
    query: sql.Select

    id = Column(Integer(), primary_key=True)
    name = Column(String(64))


class Subsection(db.Model):
    """
    Подразделы упражнений
    """
    __tablename__ = 'subsections'
    query: sql.Select

    id = Column(Integer(), primary_key=True)
    name = Column(String(64))
    section = Column(ForeignKey('sections.id', ondelete='CASCADE'))


class Practice(db.Model):
    """
    Упражнения
    """
    __tablename__ = 'practices'
    query: sql.Select

    id = Column(Integer(), primary_key=True)
    name = Column(String(64))
    place = Column(ForeignKey('places.id', ondelete='CASCADE'))
    section = Column(ForeignKey('sections.id', ondelete='CASCADE'))
    subsection = Column(ForeignKey('subsections.id', ondelete='CASCADE'))
    image = Column(String(128))


class Goal(db.Model):
    """
    Цели тренировок
    """
    __tablename__ = 'goals'
    query: sql.Select

    id = Column(Integer(), primary_key=True)
    name = Column(String(64))


class UserActivity(db.Model):
    __tablename__ = 'user_activities'
    query: sql.Select

    id = Column(Integer(), primary_key=True)
    set = Column(ForeignKey('sets.id', ondelete='CASCADE'))
    name = Column(String(64))
    user = Column(ForeignKey('users.id', ondelete='CASCADE'))
    begin = Column(Date)
    last_training = Column(Date, nullable=True)
    time = Column(Integer())


class Set(db.Model):
    """
    Комплекс упражнений
    """
    __tablename__ = 'sets'
    query: sql.Select

    id = Column(Integer(), primary_key=True)
    user = Column(BigInteger())
    author = Column(ForeignKey('users.id', ondelete='RESTRICT'))
    # name = Column(String(64))
    goal = Column(ForeignKey('goals.id', ondelete='CASCADE'))
    place = Column(ForeignKey('places.id', ondelete='CASCADE'))
    days = Column(Integer())
    exception_1 = Column(ForeignKey('exercise.id', ondelete='CASCADE'), nullable=True)
    exception_2 = Column(ForeignKey('exercise.id', ondelete='CASCADE'), nullable=True)
    exception_3 = Column(ForeignKey('exercise.id', ondelete='CASCADE'), nullable=True)
    exception_4 = Column(ForeignKey('exercise.id', ondelete='CASCADE'), nullable=True)
    exception_5 = Column(ForeignKey('exercise.id', ondelete='CASCADE'), nullable=True)
    exception_6 = Column(ForeignKey('exercise.id', ondelete='CASCADE'), nullable=True)
    exception_7 = Column(ForeignKey('exercise.id', ondelete='CASCADE'), nullable=True)
    exception_8 = Column(ForeignKey('exercise.id', ondelete='CASCADE'), nullable=True)
    exception_9 = Column(ForeignKey('exercise.id', ondelete='CASCADE'), nullable=True)
    exception_10 = Column(ForeignKey('exercise.id', ondelete='CASCADE'), nullable=True)


class Exercise(db.Model):
    __tablename__ = 'exercise'
    query: sql.Select
    id = Column(Integer(), primary_key=True)
    set = Column(ForeignKey('sets.id', ondelete='CASCADE'))
    practice = Column(ForeignKey('practices.id', ondelete='CASCADE'))
    repeats_1 = Column(Integer())
    repeats_2 = Column(Integer(), nullable=True)
    repeats_3 = Column(Integer(), nullable=True)
    repeats_4 = Column(Integer(), nullable=True)
    repeats_5 = Column(Integer(), nullable=True)


class Repeat(db.Model):
    __tablename__ = 'repeats'
    query: sql.Select
    id = Column(Integer(), primary_key=True)
    exercise = Column(ForeignKey('exercise.id', ondelete='CASCADE'))
    repeats = Column(Integer())
    break_second = Column(Integer())


class Activity(db.Model):
    """
    Упражнение в комплексе
    """
    __tablename__ = 'activities'
    query: sql.Select

    id = Column(Integer(), primary_key=True)
    set = Column(ForeignKey('sets.id', ondelete='CASCADE'))
    user = Column(ForeignKey('users.id', ondelete='CASCADE'))
    exercise = Column(ForeignKey('exercise.id', ondelete='CASCADE'))
    repeat = Column(ForeignKey('repeats.id',ondelete='CASCADE'))
    weight = Column(Integer())


async def create_db(dispatcher: Dispatcher):
    await db.set_bind(config.POSTGRES_URI)
    db.gino: GinoSchemaVisitor
    await db.gino.create_all()
