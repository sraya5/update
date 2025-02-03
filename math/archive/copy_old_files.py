from os.path import isfile, isdir, join, exists, split
from os import scandir, makedirs, remove, rename
from PyLyX import LyX
from PyLyX.objects.Environment import Environment, Container

LYX_FILES_OLD = r'C:\Users\sraya\Documents\HUJI\archive\for_LyX\summaries'
LYX_FILES_NEW = r'C:\Users\sraya\Desktop\summaries'


def dir_play(input_path: str, func, args=(), extension='.lyx'):
    if exists(input_path):
        if isfile(input_path) and input_path.endswith(extension):
            result = func(input_path, *args)
            if result:
                print(f'\t\t   {split(input_path)[1]}')
        elif isdir(input_path):
            print(f'\ndirectory: {input_path}')
            for entry in scandir(input_path):
                dir_play(join(input_path, entry.name), func, args, extension)
    else:
        raise FileNotFoundError(f'not found such file or directory: {input_path}')


def scan(path):
    for branch in scandir(path):
        if isdir(branch):
            for course in scandir(join(path, branch.name)):
                if isdir(course):
                    for part in scandir(join(path, branch.name, course.name)):
                        if isdir(part):
                            part_path = join(path, branch.name, course.name, part.name)
                            def_path = join(part_path, f'{part.name.split('#')[-1]}-definitions.lyx')
                            prf_path = join(part_path, f'{part.name.split('#')[-1]}-proofs.lyx')
                            if exists(def_path):
                                if not exists(prf_path):
                                    prf_path = join(part_path, f'{part.name.split('#')[-1]}-theorems.lyx')
                                if not exists(prf_path):
                                    print(f'invalid proofs: {part_path}')
                                else:
                                    definitions = LyX(def_path).get_doc()
                                    proofs = LyX(prf_path).get_doc()
                                    merge(definitions, proofs, part_path)
                            else:
                                print(f'invalid definitions: {part_path}')


def merge(definitions: Environment, proofs: Environment, part_path):
    lst1 =  [_ for _ in definitions.iter() if _.is_category('Section') and _.tag == 'container']
    lst2 = [_ for _ in proofs.iter() if _.is_category('Section') and _.tag == 'container']
    if len(lst1) == len(lst2):
        for i in range(len(lst1)):
            defs = Container(Environment('layout', 'Subsection', text='הגדרות'))
            for e in lst1[i]:
                if e.is_category('Subsection') or e.is_category('Subsection*'):
                    for _ in e:
                        if not (_.is_category('Subsection') or _.is_category('Subsection*')):
                            defs.append(_)
                elif not (e.is_category('Section') or e.is_category('Section*')):
                    defs.append(e)
            lst2[i].open()
            lst2[i].insert(1, defs)
        part_path = part_path.replace(LYX_FILES_OLD, LYX_FILES_NEW)
        path, name = split(part_path)
        makedirs(path, exist_ok=True)
        file = LyX(part_path + '.lyx', doc_obj=proofs)
        file.save()
        with open(part_path + '.lyx', 'r', encoding='utf8') as old:
            with open(part_path + '.lyx_', 'x', encoding='utf8') as new:
                for line in old:
                    if line == '\\font_osf false\n':
                        line = '\\font_roman_osf false\n\\font_sans_osf false\n\\font_typewriter_osf false\n'
                    new.write(line)
        remove(part_path + '.lyx')
        rename(part_path + '.lyx_', part_path + '.lyx')
    else:
        print(f'invalid length: {part_path}')


def update(path: str):
    file = LyX(path)
    body = file.get_doc()[1]
    for e in list(body):
        if not e.is_category('Section'):
            body.remove(e)
    file.find_and_replace(LYX_FILES_OLD, LYX_FILES_NEW)
    macros = Environment('layout', 'Standard')
    macros.append(Environment('inset', 'CommandInset', 'include', attrib={'LatexCommand': 'include', 'filename': 'C:/Users/sraya/AppData/Roaming/LyX2.4/macros/MKmacros.lyx'}))
    body.open()
    body.insert(0, macros)
    file.save()
    return True


if __name__ == '__main__':
    scan(LYX_FILES_OLD)
    dir_play(LYX_FILES_NEW, update)
