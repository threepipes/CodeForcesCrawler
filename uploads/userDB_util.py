from userDB import UserDB


def generate_dict(udb: UserDB):
    user_dict = {}
    for user in udb.select():
        user_dict[user['user_name']] = user
    return user_dict
