import json


def loadData(filename):
    data = None
    with open(filename, encoding='utf-8') as f:
        data = json.loads(f.read())
    return data

clm = [
    'rating', 'registrationTimeSeconds', 'country'
]
userdata = loadData('data/users.json')['result']

with open('user.csv', 'w', encoding='utf-8') as f:
    for user in userdata:
        data = []
        for c in clm:
            if not c in user:
                data.append('')
            else:
                data.append(str(user[c]))
        f.write(','.join(data)+'\n')
