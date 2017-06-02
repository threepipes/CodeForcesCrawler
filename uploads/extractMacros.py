import os
import re
import subprocess
from multiprocessing import Pool

from fileDB import FileDB


lang_list = [
    'GNU C++',
    'GNU C++11',
    'GNU C++14',
]
src_path = '../data/src/'
dst_path = '../data/src_ext/'


reg = r'/\*([^*]|\*[^/])*\*/'
def copy_ext_file(filename):
    src = os.path.join(src_path, filename)
    dst = os.path.join(dst_path, filename).replace('.src', '.cpp')
    # if os.path.exists(dst):
    #     return

    buff = ''
    with open(src, encoding='utf-8-sig') as sf:
        buff = sf.read()

    buff = re.sub(reg, '', buff.replace('\n\n', '\n'))

    code = buff
    buff = ''
    for row in code.split('\n'):
        if row.strip().startswith('#') and not 'define' in row:
            continue
        buff += row + '\n'

    with open(dst, 'w', encoding='utf-8') as df:
        df.write(buff)


def copy_files(filename):
    if not os.path.exists(dst_path):
        os.makedirs(dst_path)

    fdb = FileDB()
    file_list = fdb.select()
    size = len(file_list)

    print('begin copy files')

    with Pool(4) as p:
        p.map(copy_ext_file, list(map(lambda x: x['file_name'], file_list)))

    fdb.close()


def extract_macro(filename):
    p = subprocess.Popen(['g++', '-E', filename], stdout=subprocess.PIPE)
    stdout, stderr = p.communicate()
    result = ''
    for row in stdout.decode('utf-8').split('\r\n'):
        if row.startswith('#'):
            continue
        result += row + '\n'
    return result


new_path = '../data/extracted/'
def extract_to_path(filename):
    src = os.path.join(dst_path, filename)
    dst = os.path.join(new_path, filename)
    src_data = extract_macro(src)
    with open(dst, 'w', encoding='utf-8') as f:
        f.write(src_data)


def extract_macros():
    file_list = os.listdir(dst_path)
    if not os.path.exists(new_path):
        os.makedirs(new_path)

    with Pool(4) as p:
        p.map(extract_to_path, file_list)


def filter_failed_files():
    cnt = 0
    for i, _file in enumerate(os.listdir(dst_path)):
        if (i + 1) % 1000 == 0:
            print('searched %d' % (i + 1))
        dst = os.path.join(new_path, _file)
        if os.path.getsize(dst) < 1024 * 50:
            continue
        # org = os.path.join(src_path, _file)
        # src = os.path.join(dst_path, _file)
        cnt += 1
        if (cnt + 1) % 20 == 0:
            print(cnt)
        copy_ext_file(_file.replace('.cpp', '.src'))
        extract_to_path(_file)


def check_files():
    file_list = os.listdir(new_path)

    for _file in file_list:
        src = os.path.join(dst_path, _file)
        dst = os.path.join(new_path, _file)
        if os.path.getsize(src) / 2 > os.path.getsize(dst):
            print(_file)
            break


if __name__ == '__main__':
    check_files()
