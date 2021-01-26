from time import perf_counter
import yaml
from datetime import datetime
import csv
from pathlib import Path
import shutil


def connection(config):
    if config["type"] == 'genum':
        from utils.Genum import DatabaseGenum as Database
    elif config["type"] == 'bitrix':
        from utils.Bitrix import DatabaseBitrix as Database
    elif config["type"] == 'sinta':
        from utils.Sinta import DatabaseSinta as Database
    db_local = Database(config["db_type"], config["db_name"])
    return db_local


# Декоратор для подсчета времени выполнения
def time_test(func):
    def wrapper(*args, **kwargs):
        start = perf_counter()
        result = func(*args, **kwargs)
        print(perf_counter() - start)
        return result
    return wrapper


def save_text_to_file(filename, data):
    with open(filename+".txt", "a") as text_file:
        temp_str = str(data)
        text_file.write(temp_str)
        text_file.write("\n")


def create_file(filename):
    with open(filename+".txt", "w") as text_file:
        text_file.write("\n")


def get_config(site):
    with open("configs/config.yml", "r", encoding='utf-8') as ymlfile:
        try:
            config = yaml.safe_load(ymlfile)
            return config[site]
        except yaml.YAMLError as exc:
            print(exc)


def print_list(list):
    for elements in list:
        print(elements)


# Сохранение словаря в csv
def save_csv(path_csv, fieldnames, query_list):
    with open(path_csv, 'w', encoding="utf-8", newline='') as csvfile:
        writer = csv.DictWriter(csvfile, delimiter="^", fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(query_list)
    print("writing complete")


# Сохранение отчета
def save_report(path, data):
    with open(path, 'a+', encoding="utf-8") as file:
        file.write(str(data))
        file.write("\n")
    print("writing complete")


def get_csv_path(config, type):
    new_sitename = config["new_name"]
    now = datetime.now()    # current date and time
    time_now = now.strftime("%m-%d-%Y %H-%M-%S")
    root_path = Path.cwd()
    file_name = new_sitename + '_' + type + '_' + time_now + '.csv'
    path_csv_folder = root_path / 'csv_files' / new_sitename
    path_csv_folder.mkdir(parents=True, exist_ok=True)
    path_csv = path_csv_folder / file_name

    return path_csv


def get_report_path(config):
    new_sitename = config["new_name"]
    now = datetime.now()    # current date and time
    time_now = now.strftime("%m-%d-%Y %H-%M-%S")
    root_path = Path.cwd()
    file_name = new_sitename + '_' + 'report_' + time_now + '.md'
    path_folder = root_path / 'reports' / new_sitename
    path_folder.mkdir(parents=True, exist_ok=True)
    path = path_folder / file_name
    return path


# TODO Доделать проверку на длину файла
def copy_file(old_path, new_path):
    # Длины новых путей файлов
    # print(str(len(new_file_path_str.encode('utf-8'))) + ' - ' + new_file_path_str)
    # if len(new_file_path_str.encode('utf-8')) > 250:
    #     print(str(len(new_file_path_str.encode('utf-8'))) + ' - ' + new_file_path_str)
    # Копирование файлов
    new_path.mkdir(parents=True, exist_ok=True)
    try:
        shutil.copy2(old_path, new_path)
    except IOError as e:
        print(f'{e} Нет файла "{old_path}" {new_path}')


def copy_files(files):
    for file in files:
        # print(file.new_link)
        file.copy_file()


# TODO
def save_file(path, data):
    # with open(path, 'w', encoding='utf-8') as file:
    with open(path, 'w') as file:
        if data is not None:
            # Ошибка возникает при попытке записи кодировки 1251 в utf-8 , и возникают ошибки из за того что в 1251 есть символлы, которых нет в utf-8
            try:
                file.write(data)
            # Для обратоки этой ошибки нужно перекодировать 1251, заменив символы которых нет (по умолчанию будут заменяться на знак вопроса)
            except UnicodeEncodeError as e:
                temp_text = data.encode("cp1251", errors='replace')
                encoded_text = temp_text.decode("cp1251")
                # print(self.path)
                file.write(encoded_text)
                print(e, f'Исправлено {path}')