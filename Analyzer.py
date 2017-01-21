from fileDB import FileDB
from userDB import UserDB
import random

def getUsers():
    udb = UserDB()
    users = udb.getAllUser()
    udb.close()
    return users

def getFilenames(fdb, username, limit, langfilter=None):
    if not langfilter is None:
        pass # TODO
    return fdb.getFiles({'user_name': username}, limit)


def chooseSampleFiles(user_num=1000, file_num_each=1):
    users = getUsers()
    sample_list = random.sample(users, user_num)
    fdb = FileDB()
    files = []
    for user in users:
        files += getFilenames(fdb, user, file_num_each)


if __name__ == '__main__':
    pass
