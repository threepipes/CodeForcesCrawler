import os, os.path

if __name__ == '__main__':
    dirpath = './data/src/'
    print('loading...')
    files = os.listdir(dirpath)
    print('loaded!')
    min_size = 1
    max_size = 10000
    interval = 200
    lis = [0] * (max_size//interval)
    idx = 1
    zeros = 0
    for f in files:
        if idx % 100000 == 0:
            print(idx)
        idx += 1
        size = os.path.getsize(dirpath + str(f))
        if size >= max_size:
            continue
        if size == 0:
            zeros += 1
            continue
        lis[size//interval] += 1

    with open('size.csv', 'w') as f:
        for i, s in enumerate(lis):
            f.write('%d, %d\n' % (i*interval, s))
