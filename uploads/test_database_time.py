import time

from database.userDB import UserDB


def test_generate_dict(user_names):
    udb = UserDB()
    user_dict = udb.get_dict(force_generate=True)
    ratings = []

    for user_name in user_names:
        ratings.append(user_dict[user_name])

    return ratings


def test_raw_db(user_names):
    udb = UserDB()
    ratings = []

    for user_name in user_names:
        user = list(udb.select(where={'user_name': user_name}))[0]
        ratings.append(user['rating'])

    return ratings


if __name__ == '__main__':
    udb = UserDB()
    user_names = [user['user_name'] for user in udb.select()]
    timesec = time.time()
    test_raw_db(user_names)
    print(time.time() - timesec)
