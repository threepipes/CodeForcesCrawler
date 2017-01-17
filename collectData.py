from Database import Connector

def load(filename):
    data = []
    with open(filename) as f:
        for row in f:
            data.append(row.split(','))
    return data

def loadDB():
    con = Connector()
    table = 'filetable'
    filelist = con.get(table, ['lang'])
    cnt = {}
    for d in filelist:
        if d['lang'] in cnt:
            cnt[d['lang']] += 1
        else:
            cnt[d['lang']] = 1
    with open('lang.csv', 'w') as f:
        for k, v in cnt.items():
            f.write('%s,%s\n' % (k, v))

def count(dic, name, cnt):
    if not name in dic:
        dic[name] = cnt
    else:
        dic[name] += cnt

lang = [
'C++', 'Java', 'Python', 'PyPy', 'C#'
]

if __name__=='__main__':
    loadDB()
    data = load('lang.csv')
    res = {}
    sum_all = 0
    for d in data:
        name = d[0].replace('"', '')
        cnt = int(d[1])
        sum_all += cnt
        for l in lang:
            if l in name:
                count(res, l, cnt)
                break
        else:
            count(res, name, cnt)
    res['Python'] += res['PyPy']
    del res['PyPy']
    stat = {}
    for key, value in res.items():
        par = value*100/sum_all
        if par < 1:
            count(stat, 'other', par)
        else:
            count(stat, key, par)

    for d in sorted([(value, key) for (key, value) in stat.items()]):
        print('"%s", %f' % (d[1], d[0]))
