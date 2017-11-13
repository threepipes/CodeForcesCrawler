import json
import os
from path import root_path


def load_data(path):
    with open(path) as f:
        text = f.read().replace("'", '"') \
                .replace('/', r'\/') \
                .replace('(', '[') \
                .replace(')', ']') \
                .replace('None', 'null')
        data = json.loads(text)
    return data


def iter_data():
    modification_dir = root_path + '/../data/modification_cache/'
    for path in os.listdir(modification_dir):
        yield path, load_data(modification_dir + path)


def iter_src_info(data):
    for changes_list, src_list, prob in zip(data[2], data[1], data[0]):
        for i, (change_types, src, src_nx) in enumerate(zip(changes_list, src_list, src_list[1:])):
            yield prob, src, src_nx, change_types, i
