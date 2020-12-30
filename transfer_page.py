from pathlib import Path
from utils.util import time_test, get_config
# from objects_page import Page, Text
from os import fspath
import urllib.parse
from utils.Bitrix import DatabaseBitrix as Database
from core.File import PageFile
from core.Text import Text
from core.Page import Page


def save_all_page(config, db_local):
    path = Path.cwd()
    root_path = path / 'pages'

    pages_list = db_local.get_pages_list()
    pages = []
    sitename = config["old_name"]
    for row in pages_list:
        page = Page(row, db_local, root_path, sitename)
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
            params = {
                "old_id":       '',
                "structure":    '',
                "title":        '',
                "date":         '',
                "body":         urllib.parse.unquote(file.read()),
                "publ_date":    '',
                'page_path':    path_str,
            }
            text = Text(params, config)
            # Заменяются ссылки на новые, фозвращается список ссылок
            files = text.get_files_from_body(PageFile)
                    # Замена ссылок на файлы из текста
            text.replace_file_link(files)
            # text.delete_page_links()
            # Копируются файлы
            for link in files:
                print(link.new_link)
                link.copy_file()
            # Заменяются сссылки на внутренние страницы на пустое значение
            # text.delete_links()
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
def transfer_page(config, db_local):
    # save_all_page(config, db_local)     # Сохранение страниц в файлы 
    # collect_to_file()
    read_pages(config)                  # Чтение страниц из файлов, замена ссылок и копирование файлов


@time_test
def main():
    # Указывается список конфигураций сайтов
    sites = [
        # "deti74",
        # "mindortrans74"
        # "mininform74"
        # "mincult74",
        # "forest74",
        # "chelarhiv74",
        # "ugzhi",
        # "szn74",
        # "minstroy74",
        # "gk74",
        # "chelarhiv74",
        # "okn74"
        "imchel74",
    ]
    for site in sites:
        # Получение конфигурации
        config = get_config(site)

        path = Path.cwd()
        logs_path = path / 'logs' / site
        root_path = path / 'pages' / site

        db_type_local = config["db_type"]
        db_name_local = config["db_name"]
        db_local = Database(db_type_local, db_name_local)

        # Перенос страниц
        transfer_page(config, db_local)


if __name__ == "__main__":
    main()
