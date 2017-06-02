import re


with open('test.src', encoding='utf-8') as f:
    buff = f.read()

reg = r'/\*([^*]|\*[^/])*\*/'
with open('out.cpp', 'w', encoding='utf-8') as f:
    f.write(re.sub(reg, '', buff))
