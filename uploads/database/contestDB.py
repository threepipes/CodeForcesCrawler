from datetime import datetime

import requests as req

from database.Database import Database
from util.SleepTimer import SleepTimer


class ContestDB(Database):
    table_name = 'Competition'
    column = [
        'competition_id',
        'name',
        'start_time',
        'duration_time',
        'participants'
    ]
    key = 'competition_id'
    data_table = {
        'competition_id': 'INT(4)',
        'name': 'VARCHAR(200)',
        'start_time': 'DATETIME',
        'duration_time': 'INT(10)',
        'participants': 'INT(6)'
    }

    def __init__(self):
        super(ContestDB, self).__init__(self.table_name, self.key, self.column, self.data_table)


timer = SleepTimer()

def access_api(api, option={}):
    base_url = 'http://codeforces.com/'
    url = base_url + 'api/'
    timer.sleep(0.4)
    request = req.get(url+api, params=option)
    timer.reset()
    return request.json()


def set_participants(db):
    contests = db.select()
    cid_name = 'contestId'
    con_id_name = 'competition_id'
    for i, con in enumerate(contests):
        print('%d/%d' % (i+1, len(contests)))
        success = True
        num = 0
        while True:
            try:
                data = access_api('contest.ratingChanges', {cid_name: con[con_id_name]})
                if data['status'] == 'OK' and len(data['result']) > 0:
                    num = len(data['result'])
                    break
                else:
                    data = access_api(
                        'contest.standings',
                        {cid_name: con[con_id_name], 'showUnofficial': 'false'}
                    )
                    if data['status'] == 'OK':
                        num = len(data['result']['rows'])
                        break
                    else:
                        print('cannot get data:'+str(con))
                        success = False
                        break
            except:
                print('error:')
            timer.sleep(5)
        if not success:
            continue
        update = {con_id_name: con[con_id_name], 'participants': num}
        db.update(con[con_id_name], update)
        db.commit()
    db.close()


def mining_contest(contest_db):
    print('mining competition')
    response = access_api('contest.list', {'gym': 'false'})
    if response['status'] != 'OK':
        print('failed get competitions')
        return False

    contest_list = response['result']
    for contest in contest_list:
        start_time = 0
        if 'startTimeSeconds' in contest:
            start_time = contest['startTimeSeconds']
        name = contest['name']
        div = -1
        if 'Div. 1' in name and 'Div. 2' in name:
            div = -1
        elif 'Final' in name:
            div = 0
        elif 'Div. 1' in name:
            div = 1
        elif 'Div. 2' in name:
            div = 2
        attr = {
            'competition_id': contest['id'],
            'name': str(name),
            'start_time': str(datetime.fromtimestamp(start_time)),
            'duration_time': contest['durationSeconds'],
            'division': div,
        }
        contest_db.insert(attr)
    contest_db.commit()
    print('mining participants in each competition')
    set_participants(contest_db)
    print('finish mining competition')
    return True


def test():
    cdb = ContestDB()
    print(list(cdb.select()))

if __name__ == '__main__':
    test()
