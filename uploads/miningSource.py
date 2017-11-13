import os

from pyquery import PyQuery as pq

from database.fileDB import FileDB
from database.userDB import UserDB
from util import SleepTimer

timer = None
save_dir = '../data/src/'


def get_source(url):
    timer.sleep(1)
    dom = pq(url)
    timer.reset()
    return dom.find('pre.prettyprint.program-source').text()


def try_get_source(url):
    while True:
        try:
            source = get_source(url)
        except:
            print('Error: getting source. Retry.')
            timer.sleep(4)
        else:
            return source


def save_file(filename, content):
    with open(save_dir+filename, 'w', encoding='utf-8') as f:
        f.write(content)


def mining_source():
    udb = UserDB()
    users = udb.select()
    udb.close()
    fdb = FileDB()
    file_all = fdb.count()
    idx = 0
    for i, user in enumerate(users):
        files = fdb.select({'user_name': user})
        for row in files:
            idx += 1
            url = row['url']
            name = row['file_name']
            if has_file(name):
                continue
            if url == '-':
                continue
            print('%7d/%7d' % (idx, file_all))
            source = try_get_source(url)
            save_file(name, source)


def has_file(filename):
    if os.path.isfile(save_dir+filename):
        return True
    return False


def init():
    global timer
    timer = SleepTimer.SleepTimer()
    if not os.path.isdir(save_dir):
        os.mkdir(save_dir)


if __name__ == '__main__':
    init()
    mining_source()
