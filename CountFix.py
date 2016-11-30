from Database import Connector as Con

wa = {}


def count(dic, name, cnt):
    if not name in dic:
        dic[name] = cnt
    else:
        dic[name] += cnt


def countFix(user_data):
    pass


if __name__ == '__main__':
    con = Con()
    data = con.get('filetable', ['file_name', 'user_name', 'verdict'])
    preName = data[0]['user_name']
    user = []

    for file_data in data:
        if file_data['user_name'] == preName:
            user.append(file_data)
        else:
            avg = countFix(user)
            user = []
            

    print(wa)