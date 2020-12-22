from pathlib import Path
# import sys
import re
from os import fspath
import urllib.parse
import shutil
from datetime import datetime
from utils import save_file
from csv_objects import Obj


class Text(Obj):
    def __init__(self, data, config, page_path):
        super().__init__(config)
        self.body = data.replace("\n\n\n", "\n").replace("\n\n", "\n")
        self.section_title = self.split_path(page_path)
        self.page_path = page_path
        self.updated_data = self.body

    def split_path(self, path):
        # Пути могут быть как виндовые так и линуксовые, поэтому нужна проверка
        split_linux = path.split('/')
        split_windows = path.split('\\')
        section_title = ''
        if len(split_linux) > 1:
            section_title = split_linux[0]
        elif len(split_windows) > 1:
            section_title = split_windows[0]
        return section_title

    def get_data(self):
        return self.body


class Page:
    def __init__(self, params, db_local, config):
        self.id = params["old_id"]
        self.parent_id = params["parent_id"]
        self.title = params["title"]
        self.article = params["article"]
        self.alias = params["alias"]
        self.path = params["path"]
        self.level = params["level"]
        self.folder_path = params["folder_path"]
        self.sitename = config["old_name"]
        self.path_from_titles = self.get_title_from_path(db_local)

    def get_data(self):
        data = (
            self.id, self.parent_id, self.title,
            self.article, self.alias, self.path,
            self.level
        )
        return data

# Возвращает путь составленный из заголовков страниц
    def get_title_from_path(self, db_local):
        select_page_title = '''
            SELECT "Title"
            FROM public."sd4_HtmlPage"
            WHERE "Alias"=%s
            ORDER BY id DESC;
            '''
        path_titles = []
        page_path = self.path.split('/')
        for parent_path in page_path:
            page_title = db_local.select_rows(select_page_title, parent_path)
            if page_title is not None:
                try:
                    path_title = str(page_title[0][0]).replace('/', '.')
                    # TODO
                    # forest 134
                    # ugzhi 125
                    # Нужно делать обрезку количества символов в пути, т.к. есть ограницение на 255 символов в пути
                    # опытным путем подбираю количество символов имени так, чтобы сумма с путем была меньше 255
                    # path_titles.append(path_title[:125])
                    # path_titles.append(path_title[:134])
                    # .replace('«','').replace('»','')
                    path_titles.append(path_title.replace('<a href=http..gk74.ru.Upload.prikazy.prikaz_34_03.03.20.pdf>', '').replace('?', '').replace('"', '').replace('\t','').replace("'", '').replace(":", '').replace('...','').strip())
                except IndexError as e:
                    print(f'У страниц с адресом состоящим из {page_path}, нет названий {page_title} Ошибка: {e}')
                    print('Проверить соответствует ли в бд путь алиасам страниц')
                    # print(e)
        return (path_titles)

    def save_page_title(self):
        page_name_txt = self.alias + '.txt'
        page_name_html = self.alias + '.html'
        path_string = '/'.join(self.path_from_titles)
        page_path = Path(path_string)
        full_path = self.folder_path / page_path
        try:
            Path(full_path).mkdir(parents=True, exist_ok=True)
            save_file(full_path / page_name_txt, self.article)
            save_file(full_path / page_name_html, self.article)
        except OSError as e:
            print(e, self.path_from_titles)
            # print(f"{fspath(full_path)} len {len(fspath(full_path).encode('utf-8'))}")
            # print(f"{fspath(full_path / page_name_txt)} len {len(fspath(full_path / page_name_txt).encode('utf-8'))}")
            # print(f"{fspath(full_path / page_name_html)} len {len(fspath(full_path / page_name_html).encode('utf-8'))}")