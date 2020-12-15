from time import perf_counter
import yaml
from datetime import datetime
import csv
from pathlib import Path
import shutil


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
    with open(path_csv, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, delimiter="^", skipinitialspace = True, quotechar='~', fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(query_list)
    print("writing complete")


def get_csv_path(config, type):
    new_sitename = config["new_name"]
    now = datetime.now() # current date and time
    time_now = now.strftime("%m-%d-%Y %H-%M-%S")
    root_path = Path.cwd()
    file_name = new_sitename + '_' + type + '_' + time_now + '.csv'
    path_csv_folder = root_path / 'csv_files' / new_sitename
    path_csv_folder.mkdir(parents=True, exist_ok=True)
    path_csv = path_csv_folder / file_name

    return path_csv


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
