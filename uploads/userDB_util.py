from userDB import UserDB


def generate_dict(udb: UserDB):
    user_dict = {}
    for user in udb.select():
        user_dict[user['user_name']] = user
    return user_dict


def get_user(user_name: str, udb: UserDB):
    user = list(udb.select(where={'user_name': user_name}))
    if len(user) == 0:
        return None
    return user[0]
