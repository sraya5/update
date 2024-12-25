from os.path import isfile, isdir, split, join, exists
from os import scandir, makedirs, stat, remove
from datetime import datetime
from PyLyX import LyX


def dir_play(input_path: str, func, args=(), output_path='', index=None, skip=None):
    if skip and input_path in skip:
        return None
    elif index is None:
        index = {}

    if exists(input_path):
        if isfile(input_path) and input_path.endswith('.lyx'):
            name = split(input_path)[1]
            file = LyX(input_path)
            result, error = func(file, output_path, *args)
            if result:
                print(f'\t\t   {name}')
                index[name] = True
            elif error:
                index[name] = False
        elif isdir(input_path):
            print(f'\ndirectory: {input_path}')
            index[input_path] = {}
            for entry in scandir(input_path):
                dir_play(join(input_path, entry.name), func, args, join(output_path, entry.name), index[input_path], skip)
    else:
        raise FileNotFoundError(f'not found such file or directory: {input_path}')
    return index


def translate_name(name: str):
    if name.endswith('#d.lyx'):
        return 'definitions.xhtml'
    elif name.endswith('#c.lyx'):
        return 'claims.xhtml'
    elif name.endswith('#p.lyx'):
        return 'proofs.xhtml'
    else:
        return name


def up_output(file: LyX, output_path: str, fmt: str, last_play: datetime):
    input_path = file.get_path()
    last_edit = datetime.fromtimestamp(stat(input_path).st_mtime)

    if last_edit > last_play:
        path, name = split(output_path)
        name = translate_name(name)
        output_path = join(path, name)
        # output_path = output_path.replace(' ', '_')
        makedirs(path, exist_ok=True)
        if fmt == 'xhtml':
            if exists(output_path):
                remove(output_path)
            result = file.export2xhtml(output_path, False)
        else:
            result = file.export(fmt, output_path)
        return result, not result
    else:
        return False, False


def index2string(index: dict):
    lst = []
    for name in index:
        if index[name] is False:
            lst.append(name)
        elif type(index[name]) is dict:
            index2string(index[name])
    return '\n'.join(lst)


def up_all(input_path: str, xhtml_path='', pdf_path=''):
    # with open('last_play.txt', 'r') as lp:
    #     time = lp.readline()
    #     time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
    time = datetime.strptime('2000-10-31 13:46:34', '%Y-%m-%d %H:%M:%S')

    index_xhtml, index_pdf = {}, {}
    if xhtml_path:
        print('\n******start convert to xhtml******')
        dir_play(input_path, up_output, ('xhtml', time), xhtml_path, index_xhtml)
        print('\n******end convert to xhtml******')
        index_string = index2string(index_xhtml)
        if index_string:
            print('\n\nThe convert to xhtml of the following file failed:')
            print(index_string)
    if pdf_path:
        print('\n******start convert to pdf******')
        dir_play(input_path, up_output, ('pdf4', time), pdf_path, index_pdf)
        print('\n******end convert to pdf******')
        index_string = index2string(index_pdf)
        if index_string:
            print('\n\nThe convert to pdf of the following file failed:')
            print(index_string)

    with open('last_play.txt', 'w') as lp:
        now = datetime.now()
        now = str(now)
        lp.write(now[:19])


INPUT_PATH = 'C:\\Users\\sraya\\Documents\\HUJI\\summaries'
XHTML_PATH = 'C:\\Users\\sraya\\Documents\\GitHub\\math'
PDF_PATH = ''
MACROS_OLD = 'C:\\Users\\sraya\\AppData\\Roaming\\LyX2.4\\macros\\MacrosStandard.lyx'
MACROS_NEW = 'C:\\Users\\sraya\\AppData\\Roaming\\LyX2.4\\macros\\MKmacros.lyx'


if __name__ == '__main__':
    up_all(INPUT_PATH, XHTML_PATH, PDF_PATH)
