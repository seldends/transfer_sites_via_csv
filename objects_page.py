from pathlib import Path
# import sys
import re
from os import fspath
import urllib.parse
import shutil
from datetime import datetime
from utils import save_file


class Link:
    def __init__(self, config, data, section_title):
        root = Path.cwd()
        self.sitename = config["new_name"]
        self.file_full_path = data[1]
        self.file_relative_path = data[2]
        self.file = data[3]
        self.encoded_filename = urllib.parse.unquote(self.file)
        self.section_title = section_title
        self.path_root_old_file = root / 'source_files' / self.sitename / self.file_relative_path / self.encoded_filename
        self.path_root_new_file = root / 'page_files' / 'files/upload/' / self.sitename / self.section_title / self.encoded_filename
        self.path_root_new_folder = self.path_root_new_file.parent
        self.str_new_link = "".join(("files/upload/", self.sitename, "/", self.section_title, '/', self.file))
        self.str_old_link = "".join((self.file_full_path, self.encoded_filename))

    def get_data(self):
        data = (
            self.path_root_old_file, self.path_root_new_folder, self.path_root_new_file
        )
        return data

    def get_str(self):
        data = (
            self.str_old_link, self.str_new_link
        )
        return data

    def get_path(self):
        data = (
            self.path_root_old_file, self.path_root_new_folder
        )
        return data

    def copy_file(self, page):
        # Длины новых путей файлов
        # print(str(len(new_file_path_str.encode('utf-8'))) + ' - ' + new_file_path_str)
        # if len(new_file_path_str.encode('utf-8')) > 250:
        #     print(str(len(new_file_path_str.encode('utf-8'))) + ' - ' + new_file_path_str)
        # Копирование файлов
        self.path_root_new_folder.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copy2(self.path_root_old_file, self.path_root_new_folder)
        except IOError as e:
            # print(new_file_path, file, new_file_path_str)
            print(e)
            print(f'Нет файла "{self.path_root_old_file}" | Страница : "{page}"')


# Функция разбиват путь до файла на отдельные имена страниц по иерархии, и возвращает имя родительской страницы
def split_path(path):
    # Пути могут быть как виндовые так и линуксовые, поэтому нужна проверка
    split_linux = path.split('/')
    split_windows = path.split('\\')
    section_title = ''
    if len(split_linux) > 1:
        section_title = split_linux[0]
    elif len(split_windows) > 1:
        section_title = split_windows[0]
    return section_title


class Text:
    def __init__(self, data, config, page_path):
        self.data = data.replace("\n\n\n", "\n").replace("\n\n", "\n")
        self.sitename = config["new_name"]
        # self.old_sitename = config["old_name"]
        self.section_title = split_path(page_path)
        self.page_path = page_path
        self.config = config
        self.updated_data = self.data

    # Замены ссылок на файлы
    def update_file_links(self):
        old_sitename = self.config["old_name"]
        # TODO Попробовать разбить регулярку на части, чтобы стало понятнее
        pattern_links = fr'(<a href=\"((?:http:\/\/(?:www\.|){old_sitename}|)\/((?:dokumentydok\/[^\/]{{1,75}}|upload\/iblock\/[^\/]{{0,4}}|Upload\/files|Files\/DiskFile\/(?:|[0-9]{4}\/)[a-zA-Z]{{1,10}}|opendata|Storage\/Image\/PublicationItem\/Image\/src\/[0-9]{{1,5}})\/))([^>]{{1,450}}\.[a-zA-Z]{{3,5}})\s?\"[^>]{{0,250}}>)'
        pattern_img = fr'(<(?:img|input) (?:alt=\"\"|(?:id|class|alt)=\"[^\"]{{0,20}}\"|)\s?src=\"((?:http:\/\/(?:www\.|){old_sitename}|)\/((?:Upload\/(?:files|images)|Files\/images|Storage\/Image\/PublicationItem\/Image\/src\/[0-9]{{1,5}})\/))([^>]{{1,450}}\.[a-zA-Z]{{3,5}})\s?\"[^>]{{0,250}}>)'
        pattern_video = fr'(<a href=\"((?:http:\/\/(?:www\.|){old_sitename}|)\/(Files\/VideoFiles\/))([^>]{{1,450}}\.[a-zA-Z]{{3,5}})\s?\"[^>]{{0,200}}>)'

        pattern_list = {
            "файлы": pattern_links,         # паттерн для поиска ссылок
            "картинки": pattern_img,        # паттерн для поиска картинок
            "видео": pattern_video          # паттерн для поиска видео
        }
        link_list = []
        for link_type, pattern in pattern_list.items():
            match_list = re.findall(pattern, self.data)
            for element in match_list:
                try:
                    # Проверка если в списке больше 4х элементов
                    print(f'элемент {element}, файл {element[4]}')
                except IndexError as e:
                    # Нормальное поведение 4 элемента в списке
                    pass
                    # print(f'{e}')
                # Объект ссылки
                link = Link(self.config, element, self.section_title)
                # Замена ссылок
                self.replace_link(link.str_old_link, link.str_new_link)
                # Список ссылок
                link_list.append(link)
            if len(match_list) == 0:
                # print(f"Ссылок {link_type} на странице '{page_path}' нет")
                pass
        return link_list

    # Убираются ссылки на страницы
    def update_page_links(self):
        # TODO Попробовать разбить регулярку на части, чтобы стало понятнее
        old_sitename = self.config["old_name"]
        pattern_page = fr'(<a href=\"((?:http:\/\/(?:www\.|){old_sitename}|)\/(htmlpages\/(?:Show|CmsHtmlPageList)\/[^\"]{{1,75}}(?:\/[^\"]{{1,75}}\/[^\"]{{1,75}}|\/[^\"]{{1,75}}|)))\"[^>]{{0,250}}>)'
        pattern_npa = fr'(<a href=\"((?:http:\/\/(?:www\.|){old_sitename}|)\/(LegalActs\/Show\/[^\/>]{{1,10}}))\"[^>]{{0,250}}>)'
        pattern_single_page = fr'(<a href=\"((?:http:\/\/(?:www\.|){old_sitename}|)(?:|\/|\/(?:InternetReception|LegalActs)))\"[^>]{{0,250}}>)'
        pattern_id = fr'(<a href=\"((?:http:\/\/(?:www\.|){old_sitename}|)\/Publications\/[a-zA-Z]{{1,15}}(?:\/Show\?id=[0-9]{{0,10}}|))\"[^>]{{0,250}}>)'

        pattern_list = {
            "страницы":         pattern_page,           # паттерн для поиска ссылок на страницы
            "НПА":              pattern_npa,            # паттерн для поиска ссылок на НПА
            "приемная":         pattern_single_page,    # паттерн для поиска ссылок на приемнуюкорневые страницы
            "страницы с id":    pattern_id,             # паттерн для поиска ссылок на страницы mainnew
        }
        for link_type, pattern in pattern_list.items():
            match_list = re.findall(pattern, self.data)
            # print(f'{len(match_list)} : {match_list}')
            for element in match_list:
                # Ссылки в документе
                full_link = element[1]
                empty_link = ""
                self.data = self.data.replace(full_link, empty_link)
            if len(match_list) == 0:
                # print(f"Ссылок {link_type} на странице '{page_path}' нет")
                pass

    def replace_link(self, old_link, new_link):
        # Замена ссылок
        self.data = self.data.replace(old_link, new_link, 1)

    def get_data(self):
        return self.data

    def get_updated_data(self):
        return self.updated_data


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
            save_file(full_path / page_name_txt, self.article )
            save_file(full_path / page_name_html, self.article )
        except OSError as e:
            print(e, self.path_from_titles)
            # print(f"{fspath(full_path)} len {len(fspath(full_path).encode('utf-8'))}")
            # print(f"{fspath(full_path / page_name_txt)} len {len(fspath(full_path / page_name_txt).encode('utf-8'))}")
            # print(f"{fspath(full_path / page_name_html)} len {len(fspath(full_path / page_name_html).encode('utf-8'))}")