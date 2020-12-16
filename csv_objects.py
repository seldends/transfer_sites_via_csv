from pathlib import Path
import re
import urllib.parse
from utils import copy_file


class News:
    def __init__(self, row, config):
        self.folder_name = config["new_name"]
        self.a_structure = config["news_type"][row[1]]
        self.old_id = row[0]
        self.a_title = row[2]
        self.a_date = row[9]
        self.a_image_index = str(row[7]).replace("^", "#")
        # self.a_body = str(row[4]).replace('<p style="text-align: justify;">&nbsp;</p>', '')
        self.a_body = str(row[4]).replace("^", "#").replace("\r", "").replace("\n", "")
        self.a_publ_date = row[5]
        self.a_resume = row[3]
        self.config = config
        self.a_classification = config["classification"]
        self.isPublish = 'Да'
        self.pubmain = 'Да'
        self.mediaFiles = ''

    def transform_body(self):
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
        for pattern in pattern_list:
            try:
                match_list = re.findall(pattern, self.a_body)
                if len(match_list) > 0:
                    for element in match_list:
                        # Если элемент строка - то заменять строку
                        if type(element) == str:
                            self.a_body = str(self.a_body).replace(element, '')
                        # Если элемент кортеж - то заменять 2й элемент (путь до картинки)
                        if type(element) == tuple:
                            # print(element[1])
                            self.a_body = str(self.a_body).replace(element[1], '')
            except Exception as e:
                print(e)
    # TODO Разобраться
    def make_mediafiles(self):
        image_list = []
        image_name_list = []
        # fromid = self.a_ouid
        description = ""
        for pattern in self.pattern_list:
            try:
                pattern_image_list = re.findall(pattern, self.a_body)
                # Если есть совпадения
                if len(pattern_image_list) > 0:
                    for temp_image in pattern_image_list:
                        # Проверка если кортеж - то значит 2м объектом идет путь до картинки
                        if type(temp_image) == tuple and temp_image[1] != 'www.':
                            # if type(temp_image) == tuple:
                            # print(type(temp_image))
                            toid = str(temp_image[1])
                            image = NewsFile(toid, description, fromid, self.folder_name)
                            image_name_list.append(str(temp_image[1]).replace("/Upload/images/", "").replace("/Storage/Image/PublicationItem/Article/src/", ""))
                            image_list.append(image)
            except Exception as e:
                print(e)
        return image_list, image_name_list

    # TODO Разобраться
    def get_news_data(self):
        data = (
            self.a_title, self.a_date, self.a_image_index, self.a_body,
            self.a_publ_date, self.a_resume, self.a_structure
        )
        return data

    # TODO Разобраться
    def delete_links(self):
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
            try:
                if self.a_body:
                    links = re.findall(pattern, self.a_body)
                    # Если есть совпадения
                    if len(links) > 0:
                        # print(links)
                        for link in links:
                            full_link = link[0]         # Полная ссылка с a href и стилями. Пример:     <a href="http://forest74.ru/htmlpages/Show/activities/Protivodejstviekorrupcii">
                            page_link = link[1]         # Ссылка                            Пример:     http://forest74.ru/htmlpages/Show/activities/Protivodejstviekorrupcii
                            # relative_page_link = link[2]         # Относительная страница          Пример:     htmlpages/Show/activities/Protivodejstviekorrupcii
                            # updated_text = str(self.self.a_body).replace(page_link, '').replace('<p><a href="">ТЕКСТ</a></p>', '').replace('None', '')      # Убирается путь до файла из ссылки
                            # self.self.a_body = updated_text.replace('<p><a href="">ТЕКСТ</a></p>', '').replace('None', '')
            except Exception as e:
                print(e, 'test')


class File:
    def __init__(self, config, data, category):
        root = Path.cwd()
        self.sitename = config["new_name"]
        self.category = category
        self.file_full_path = data["file_full_path"]
        self.file_relative_path = data["file_relative_path"]
        self.file = data["file"]
        if self.category == 'news':
            # self.new_link = "".join(("files/upload/", self.sitename, "/", "Файлы новостей", '/', self.file))
            # self.str_new_link = "".join(("files/upload/", self.sitename, "/", "Файлы новостей", '/', self.file, "@cmsFile.doc"))
            self.new_link = "".join(("files/news_mediafiles/", self.sitename, "/", self.file))
            self.str_new_link = "".join(("/news_mediafiles/", self.sitename, "/", self.file, "@cmsFile.doc"))
        if self.category == 'news2':
            self.new_link = "".join(("files/news_mediafiles/", self.sitename, "/", self.file))
            self.str_new_link = "".join(("/news_mediafiles/", self.sitename, "/", self.file, "@cmsFile.doc"))
        elif self.category == 'mediafiles':
            folder_name = Path(self.file_relative_path).name
            self.new_link = "".join(("files/news_mediafiles/", self.sitename, "/", folder_name, "/", self.file))
            self.str_new_link = "".join(("/news_mediafiles/", self.sitename, "/", folder_name, "/", self.file, "@cmsFile.doc"))
        elif self.category == 'indeximage':
            folder_name = Path(self.file_relative_path).name
            self.new_link = "".join(("files/ogvspb/pictures/", self.sitename, "/", folder_name, "/", self.file))
            self.str_new_link = "".join(("/ogvspb/pictures/", self.sitename, "/", folder_name, "/", self.file, "@cmsFile.doc"))
        elif self.category == 'npafiles':
            self.str_new_link = "".join(("/norm_act/", self.sitename, "/", self.file, "@cmsFile.doc"))

        self.encoded_filename = urllib.parse.unquote(self.file)
        self.path_root_old_file = root / 'source_files' / self.sitename / self.file_relative_path / self.encoded_filename

    def copy_news_file(self):
        # Копирование файлов
        root = Path.cwd()
        self.path_root_new_file = root / 'new_files' / self.sitename / self.new_link
        self.path_root_new_folder = self.path_root_new_file.parent
        copy_file(self.path_root_old_file,  self.path_root_new_folder)
