from pathlib import Path
from utils import time_test, get_config
from objects_page import Page, Text
from os import fspath
import urllib.parse
from utils_db_local import DatabaseGenum as Database
from datetime import datetime
from csv_objects import PageFile


def get_folder_path(config):
    sitename = config["old_name"]
    path = Path.cwd()
    root_path = path / 'pages'
    now = datetime.now() # current date and time
    time_now = now.strftime("%m-%d-%Y %H-%M-%S")
    site_folder = sitename + '_' + time_now
    folder_path = root_path / site_folder
    return folder_path


def save_all_page(config):
    db_type_local = config["db_type"]
    db_name_local = config["db_name"]
    db_local = Database(db_type_local, db_name_local)       # Объект подключения к бд со старыми данными
    pages_list = db_local.get_pages_list()
    pages = []
    folder_path = get_folder_path(config)
    for row in pages_list:
        params = {
            "old_id":       row[0],
            "parent_id":    row[1],
            "title":        row[2],
            "article":      row[3],
            "alias":        str(row[4]).strip(),
            "path":         str(row[5]).strip(),
            "level":        row[6],
            "folder_path": folder_path,
        }

        page = Page(params, db_local, config)
        page.save_page_title()
        pages.append(page)


# Считывание содержимого страниц из файлов
@time_test
def read_pages(config):
    sitename = config["old_name"]
    path = Path.cwd()
    path_site = path / 'pages' / sitename

    for path in path_site.rglob('*.txt'):
        path_str = fspath(path).replace(fspath(path_site), '')[1:]

        with open(path, mode='r+', encoding='cp1251', errors='replace') as file:
            text = Text(urllib.parse.unquote(file.read()), config, path_str)
            # Заменяются ссылки на новые, фозвращается список ссылок
            links = text.update_body(PageFile)
            # Заменяются сссылки на внутренние страницы на пустое значение
            text.delete_links()
            # Копируются файлы
            # for link in links:
            #     link.copy_file(path_str)

            # Запись будет происходить в начало файла
            file.seek(0)
            # Запись обновленного текста
            file.write(text.body)
            # Для того чтобы отсечь часть со старой записью
            file.truncate()


# Сохранение всех txt в один файл из папки сайта, чтобы по файлу искать необработанные ссылки
def collect_to_file(config):
    sitename = config["old_name"]
    path = Path.cwd()

    full_path = path / 'pages' / sitename
    file_contents = [
        path.read_text()
        for path in full_path.rglob('*.txt')
    ]
    with open(full_path / 'all.txt', 'w') as file:
        for page in file_contents:
            file.write(page)


@time_test
def main():
    # Указывается список конфигураций сайтов
    sites = [
        "szn74",
    ]
    for site in sites:
        # Получение конфигурации
        config = get_config(site)
        # Перенос страниц
        save_all_page(config)     # Сохранение страниц в файлы 
        # collect_to_file()
        # read_pages(config)                  # Чтение страниц из файлов, замена ссылок и копирование файлов


if __name__ == "__main__":
    main()
