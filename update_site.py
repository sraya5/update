from os.path import isfile, isdir, split, join
from os import scandir, makedirs, stat
from datetime import datetime
from PyLyX.base.lyx import LYX
from PyLyX.lyx2xhtml.xhtml_correct import export2xhtml
from PyLyX.lyx2xhtml.sraya_xhtml_correct import CSS_FILE, addition_func


def dir_play(full_path: str, func, args=(), index=None, skip=None):
    if skip and full_path in skip:
        return None
    elif index is None:
        index = {}

    if isfile(full_path) and full_path.endswith('.lyx'):
        name = split(full_path)[1]
        result = func(full_path, *args)
        if result:
            print(name)
            index[name] = True
        else:
            index[name] = False
    elif isdir(full_path):
        print(f'\ndirectory: {full_path}')
        index[full_path] = {}
        for entry in scandir(full_path):
            dir_play(join(full_path, entry.name), func, args, index[full_path], skip)
    return index


def up_macros(file_path: str, macros_old: str, macros_new: str):
    path, name = split(file_path)
    f = LYX(path, name)
    f.find_and_replace(macros_old, macros_new)


def up_all_macros(input_path, macros_old, macros_new):
    dir_play(input_path, up_macros, (macros_old, macros_new))


def translate_name(name: str):
    if name.endswith('- d.lyx'):
        new_name = 'definitions.lyx'
    elif name.endswith('- c.lyx'):
        new_name = 'claims.lyx'
    elif name.endswith('- p.lyx'):
        new_name = 'proofs.lyx'
    else:
        new_name = name
    return new_name


def up_output(input_path: str, output_path: str, fmt: str, last_play: datetime, depth=-1):
    last_edit = datetime.fromtimestamp(stat(input_path).st_mtime)

    if last_edit > last_play:
        path, name = split(input_path)
        output_path = output_path.replace(' ', '_')
        output_path, output_name = split(output_path)
        makedirs(output_path, exist_ok=True)

        if fmt == 'xhtml':
            output_name = translate_name(output_name)
            result = export2xhtml(input_path, join(output_path, output_name), CSS_FILE, depth, addition_func)
        else:
            f = LYX(path, name)
            result = f.export(fmt, join(output_path, output_name))

    else:
        result = False

    return result


def print_index(index: dict):
    for name, value in index:
        if value is False:
            print(name)
        elif type(value) is dict:
            print_index(index[name])


def up_all(input_path: str, xhtml_path='', pdf_path=''):
    with open('last_play.txt', 'r') as lp:
        time = lp.readline()
        time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')

    index_xhtml, index_pdf = {}, {}
    if xhtml_path:
        print('\n******start convert to xhtml******')
        dir_play(input_path, up_output, (xhtml_path, 'xhtml', time), index_xhtml)
        print('\n******end convert to xhtml******')
    if pdf_path:
        print('\n******start convert to pdf******')
        dir_play(input_path, up_output, (pdf_path, 'pdf4', time), index_pdf)
        print('\n******end convert to pdf******')

    print('\nThe convert to xhtml of the following file failed:')
    print_index(index_xhtml)
    print('\nThe convert to pdf of the following file failed:')
    print_index(index_pdf)

    with open('last_play.txt', 'w') as lp:
        now = datetime.now()
        now = str(now)
        lp.write(now[:19])


INPUT_PATH = 'C:\\Users\\sraya\\Documents\\HUJI\\The Completeness Axiom'
XHTML_PATH = 'C:\\Users\\sraya\\Documents\\GitHub\\math'
PDF_PATH = ''
# MACROS_OLD = 'C:/Users/sraya/Documents/LyX/MacrosStandard.lyx'
# MACROS_NEW = 'C:/Users/sraya/AppData/Roaming/LyX2.4/macros/MacrosStandard.lyx'


if __name__ == '__main__':
    up_all(INPUT_PATH, XHTML_PATH, PDF_PATH)
