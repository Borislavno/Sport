from filters.registered_users import Registered_User, Trainers, Banned_User
from loader import dp



if __name__ == "filters":
    dp.filters_factory.bind(Trainers)
    dp.filters_factory.bind(Registered_User)
    dp.filters_factory.bind(Banned_User)
    pass
