from os import scandir
from os.path import exists, isfile, split, isdir, join


def index2string(index: dict, lst: list):
    for name in index:
        if index[name] is False:
            lst.append(name)
        elif type(index[name]) is dict:
            index2string(index[name], lst)
    if lst:
        return '\n'.join(lst)


def dir_play(input_path: str, func, args=(), output_path='', info_print=True, index: dict | None = None):
    if index is None:
        index = {}

    if exists(input_path):
        if isfile(input_path):
            name = split(input_path)[1]
            if output_path:
                result, error = func(input_path, *args, output_path)
            else:
                result, error = func(input_path, *args)
            if result:
                index[name] = True
                if info_print:
                    print(f'\t\t   {name}')
            elif error:
                index[name] = False
        elif isdir(input_path):
            if info_print:
                print(f'\ndirectory: {input_path}')
            index[input_path] = {}
            for entry in scandir(input_path):
                new_output_path = join(output_path, entry.name) if output_path else output_path
                dir_play(join(input_path, entry.name), func, args, new_output_path, info_print, index[input_path])
    else:
        raise FileNotFoundError(f'not found such file or directory: {input_path}')
    return index