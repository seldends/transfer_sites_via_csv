from pathlib import Path
import urllib.parse
import logging
import csv
import re
from utils import time_test, get_config, get_csv_path, save_csv


# Проверка есть ли файл txt в директории
def check_file(page_path, not_file):
    if len(list(page_path.glob('*.txt'))) == 0:
        if page_path not in not_file:
            not_file.append(page_path)
            print(f'Нет файла {page_path}')


def recursive_subdir_count(path):
    parent_path = path.parent.parent
    glob_result = Path(parent_path).glob('*/')
    dirs = list(glob_result)
    dirs_str = [str(i) for i in dirs]
    # print(dirs_str)
    #print(f'длина исходн {len(path.parts)} {path}')
    for dir in dirs:
        result = re.search(r'\.(?:txt|html)$', str(dir.name))
        if result:
            index = dirs.index(dir)
            # print(result, dir)
            del dirs[index]
        # if len(dirs) != len(path.parts)+1:
    try:
        index = dirs.index(path.parent)
    except ValueError as error:
        print(f'21 {dirs}')
        print(f'22 {error} {path} {path.parent}')
    #print(f'{path} {dirs[index]}')
    # del dirs[index]

        #     
    return dirs
        # print(dir)
        # pattern = re.compile(pattern)

    #     result = re.search(r'\.(?:txt|html)$', str(dir.name))
    #     if result:
    #         
    #         print(result, dir, index)
    #         
    #print(f'обработанный {len(dirs)}-{dirs}')
        # if dir.name 
        # del dirs[dir]
    # print(len(list(dirs)[1:]))
    #for dir in dirs:
    #     print(dir)
    # result = sum(1 for dir in dirs)
    # result -= 1  # discount `path` itself
    # print(result)


# Считывание содержимого страниц из файлов
@time_test
def make_structure_csv(config):
    sitename = config["old_name"]
    new_sitename = config["new_name"]

    root_path = Path.cwd()
    path_site = root_path / 'pages' / sitename

    not_file = []
    query_list = []
    for path in path_site.rglob('*.txt'):
        page_name = path.parent.name            # Имя страницы
        test_dirs = recursive_subdir_count(path)
        number = 9999
        try:
            test_index = test_dirs.index(path.parent)
            print(test_index)
            number = 10*(test_index+1)
        except ValueError as error:
            print(f'11 {error}, {test_dirs} {path.parent}')
        dirs = [Path(*path.parts[:-1])]         # Список всех директорий до файла
        relative_len = len(path.parts[5:-2])    # Глубина вложенности страницы
        test = 0
        while test < relative_len:
            parent_folder = Path(*path.parts[:-test-2])     # Путь родительской страницы
            dirs.append(parent_folder)
            test += 1
        eng_path = []       # Спсиок для кодов страницы и родительских страниц
        for page_path in dirs:
            check_file(page_path, not_file)
            for path in page_path.glob('*.txt'):            # поиск txt в директории
                last_part = path.parts[-1]                  # Имя найденного txt
                eng_path.append(last_part[:-4].lower())     # Добавление имени txt

        eng_path.append(new_sitename)           # Добавление имени сайта (кода главной страницы)
        eng_path.reverse()                      # изменение порядка списка
        # print(eng_path)
        parent_path = '/'.join([str(elem) for elem in eng_path[:-1]])
        page_code = '/'.join([str(elem) for elem in eng_path])
        row = {
                'code': page_code,
                'name': page_name,
                'description': page_name,
                'parent': parent_path,
                'num': number
            }
        fieldnames = row.keys()
        if row not in query_list:
            query_list.append(row)

    if len(not_file) == 0:
        print(len(query_list))
        path_csv = get_csv_path(config, 'structure')         # Получение пути для csv
        save_csv(path_csv, fieldnames, query_list)      # Сохранение словаря в csv
    else:
        print(f'Отсутсвуют txt в некоторых папках, csv не создан')


@time_test
def main():
    # Суммарно 73 НПА
    # Указывается список конфигураций сайтов
    sites = [
        # "deti74",
        # "mindortrans74"
        # "mininform74"
        # "mincult74",
        # "forest74",
        # "chelarhiv74",
        # "ugzhi",
        "szn74",
        # "minstroy74",
        # "gk74",
        # "chelarhiv74",
        # "okn74"
    ]
    for site in sites:
        # Получение конфигурации
        config = get_config(site)
        make_structure_csv(config)


if __name__ == "__main__":
    main()
