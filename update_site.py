from os.path import isfile, isdir, split, join
from os import scandir, makedirs, stat
from datetime import datetime
from json import load
from PyLyX.helper import USER_DIR
from PyLyX.lyx import LyX


def dir_play(full_path: str, func, args=(), index=None, skip=None):
    if skip and full_path in skip:
        return None
    elif index is None:
        index = {}

    if isfile(full_path) and full_path.endswith('.lyx'):
        name = split(full_path)[1]
        result = func(full_path, *args)
        if result:
            print(f'\t\t   {name}')
            index[name] = True
        else:
            index[name] = False
    elif isdir(full_path):
        print(f'\ndirectory: {full_path}')
        index[full_path] = {}
        for entry in scandir(full_path):
            dir_play(join(full_path, entry.name), func, args, index[full_path], skip)
    return index


def translate_name(name: str):
    if name.endswith('- d.lyx'):
        return 'definitions.xhtml'
    elif name.endswith('- c.xhtml'):
        return 'claims.lyx'
    elif name.endswith('- p.lyx'):
        return 'proofs.xhtml'
    else:
        return name


def up_output(input_path: str, output_path: str, fmt: str, last_play: datetime):
    last_edit = datetime.fromtimestamp(stat(input_path).st_mtime)

    if last_edit > last_play:
        path, name = split(input_path)
        output_path = output_path.replace(' ', '_')
        output_path, output_name = split(output_path)
        makedirs(output_path, exist_ok=True)
        f = LyX(path, name)
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


INPUT_PATH = 'C:\\Users\\sraya\\Documents\\HUJI\\complex'
XHTML_PATH = 'C:\\Users\\sraya\\Documents\\GitHub\\complex'
PDF_PATH = ''
MACROS_OLD = 'C:\\Users\\sraya\\AppData\\Roaming\\LyX2.4\\macros\\MacrosStandard.lyx'
MACROS_NEW = 'C:\\Users\\sraya\\AppData\\Roaming\\LyX2.4\\macros\\MKmacros.lyx'


if __name__ == '__main__':
    pass
