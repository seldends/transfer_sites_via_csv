from pathlib import Path
import re
import urllib.parse
from utils import copy_file


class News:
    def __init__(self, params, config):
        self.config = config
        self.folder_name = config["new_name"]
        self.a_structure = params["structure"]
        self.old_id = params["old_id"]
        self.a_title = params["title"]
        self.a_date = params["date"]
        self.a_image_index = params["image_index"]
        self.a_body = params["body"]
        self.a_publ_date = params["publ_date"]
        self.a_resume = params["resume"]
        self.a_classification = config["classification"]
        self.isPublish = 'Да'
        self.pubmain = 'Да'
        self.mediaFiles = ''

    # TODO подумать как можно объединить общий функционал на функции обработки файлов
    # Получение файла Новостей из описания Новостей
    def update_body(self):
        # TODO сделать передачу имени в регулярку
        old_sitename = self.config["old_name"]
        genum_pattern_file_1 = fr'(<a href=\"((?:http:\/\/(?:www\.|){old_sitename}|)\/(((?:dokumentydok\/[^\/]{{1,75}}|upload\/iblock\/[^\/]{{0,4}}|Upload\/files|Files\/DiskFile\/(?:|[0-9]{{4}}\/)[a-zA-Z]{{1,10}}|opendata|Storage\/Image\/PublicationItem\/Image\/src\/[0-9]{{1,5}})\/)([^>]{{1,450}}\.[a-zA-Z]{{3,5}})))\s?\"[^>]{{0,250}}>)'
        genum_pattern_file_2 = fr'(<img alt=\"[^\/]{{0,50}}\"(?:\sclass=\"[^\/]{{0,50}}\"|)\ssrc=\"((?:http:\/\/(?:www\.|){old_sitename}|)\/(((?:Upload\/images\/|Storage\/Image\/PublicationItem\/Article\/src\/[0-9]{{1,5}}\/))([^>\/]{{1,450}}\.[a-zA-Z]{{3,5}})))\"[^>]{{0,550}}>)'
        sinta_pattern_file_1 = r'(<a href=\"((?:http:\/\/(?:ruk\.|)pravmin74.ru|)\/((sites\/default\/files\/imceFiles\/user-[0-9]{1,4}\/)([^>]{1,450}\.[a-zA-Z]{3,5})))\"[^>]{0,550}>)'
        bitrix_pattern_file_1 = r'(<img\s(?:width=\"[0-9]{1,4}\"\s|)(?:alt=\"[^\"]{1,50}\"\s|)src=\"((?:http:\/\/imchel\.ru|)\/((upload\/(?:medialibrary\/[^\/]{1,5}\/|))([^>\"]{1,450}\.[a-zA-Z]{3,5})))\"[^>]{0,550}>)'
        bitrix_pattern_file_2 = r'(<a\s(?:target=\"_blank\"\s|)(?:alt=\"[^\"]{1,50}\"\s|)href=\"((?:http:\/\/imchel\.ru|)\/((upload\/(?:[^\/]{1,20}\/(?:[^\/]{1,5}\/|)|))([^>\"]{1,450}\.[a-zA-Z]{3,5})))\"[^>]{0,550}>)'
        pattern_list = {
            "genum_file_1":    genum_pattern_file_1,         # паттерн 1
            "genum_file_2":    genum_pattern_file_2,         # паттерн 2
            "sinta_file_1":    sinta_pattern_file_1,         # паттерн 2
            "bitrix_file_1":   bitrix_pattern_file_1,         # паттерн 2
            "bitrix_file_2":   bitrix_pattern_file_2,         # паттерн 2
        }
        files = []
        for link_type, pattern in pattern_list.items():
            try:
                links = re.findall(pattern, self.a_body)
                # print(links, pattern)
                # Если есть совпадения
                if len(links) > 0:
                    for link in links:
                        # print(link)
                        data = {
                            "full_link":            link[0],    # Полная ссылка с a href и стилями. Пример:     <a href="http://ruk.pravmin74.ru/sites/default/files/imceFiles/user-333/soglasie_rk_2020.docx">
                            "file_full_path":       link[1],    # Ссылка на файл.                   Пример:     http://ruk.pravmin74.ru/sites/default/files/imceFiles/user-333/soglasie_rk_2020.docx
                            "file_path":            link[2],    # Полный путь до файла.             Пример:     sites/default/files/imceFiles/user-333/soglasie_rk_2020.docx
                            "file_relative_path":   link[3],    # Папка файла.                      Пример:     sites/default/files/imceFiles/user-333/
                            "file":                 link[4],    # Имя файла с расширением.          Пример:     soglasie_rk_2020.docx
                        }
                        file = NewsFile(self.config, data)
                        files.append(file)
                        # TODO разобраться
                        #self.a_body = str(self.a_body).replace(file.file_full_path, file.str_new_link)     # Замены ссылки
                        self.a_body = str(self.a_body).replace(file.file_full_path, file.new_link)
                        self.a_body = re.sub(r'[\n]{2,3}', r'', self.a_body)
                        temp_a_resume = re.sub(r'(?:<|)(?:\/|)[a-z]{1,5}>', r'', str(self.a_resume))
                        temp2_a_resume = re.sub(r'[\n]{2,3}', r'', temp_a_resume)
                        self.a_resume = temp2_a_resume
            # TODO сделать нормальную обработку
            except Exception as e:
                print(e, 'test')
        return files

    def delete_links(self):
        # TODO сделать передачу имени в регулярку
        old_sitename = self.config["old_name"]
        genum_pattern_page = fr'(<a href=\"((?:http:\/\/(?:www\.|){old_sitename}|)\/(htmlpages\/(?:Show|CmsHtmlPageList)\/[^\"]{{1,75}}(?:\/[^\"]{{1,75}}\/[^\"]{{1,75}}|\/[^\"]{{1,75}}|)))\"[^>]{{0,250}}>)'
        genum_pattern_npa = fr'(<a href=\"((?:http:\/\/(?:www\.|){old_sitename}|)\/(LegalActs\/Show\/[^\/>]{{1,10}}))\"[^>]{{0,250}}>)'
        genum_pattern_single_page = fr'(<a href=\"((?:http:\/\/(?:www\.|){old_sitename}|)(?:|\/|\/(?:InternetReception|LegalActs)))\"[^>]{{0,250}}>)'
        genum_pattern_id = fr'(<a href=\"((?:http:\/\/(?:www\.|){old_sitename}|)\/Publications\/[a-zA-Z]{{1,15}}(?:\/Show\?id=[0-9]{{0,10}}|))\"[^>]{{0,250}}>)'
        sinta_pattern_npa = r'(<a href=\"((?:http:\/\/(?:ruk\.|)pravmin74.ru|)(\/normativnye-pravovye-akty\/[^\/]{1,250}\/[^\/\"]{1,250}))\"[^>]{0,100}>)'
        sinta_pattern_news = r'(<a href=\"((?:http:\/\/(?:ruk\.|)pravmin74.ru|)(\/novosti\/[^\/\"]{1,250}))\"[^>]{0,100}>)'
        sinta_pattern_page = r'(<a href=\"((?:http:\/\/(?:ruk\.|)pravmin74.ru|)(\/[^\/\"]{1,100}))\"[^>]{0,100}>)'
        bitrix_pattern_page = r'(<a\s(?:target=\"_blank\"\s|)href=\"((?:https?:\/\/imchel\.ru|)(?:\/?(?:[^\/\"]{1,50}\/|)(?:[^\/\"]{1,50}\/|)(?:[^\/\"]{1,250}|)\/?)|)\"[^>]{0,100}>)'

        pattern_list = {
            "genum_page":           genum_pattern_page,         # genum паттерн для поиска ссылок на страницы
            "genum_npa":            genum_pattern_npa,          # genum паттерн для поиска ссылок на НПА
            "genum_single_page":    genum_pattern_single_page,  # genum паттерн для поиска ссылок на приемнуюкорневые страницы
            "genum_news":           genum_pattern_id,           # genum паттерн для поиска ссылок на новости
            "sinta_npa":            sinta_pattern_npa,          # sinta паттерн для поиска ссылок на НПА
            "sinta_news":           sinta_pattern_news,         # sinta паттерн для поиска ссылок на новости
            "sinta_page":           sinta_pattern_page,         # sinta паттерн для поиска ссылок на страницы
            "bitrix_page":  bitrix_pattern_page,
        }
        for link_type, pattern in pattern_list.items():
            try:
                links = re.findall(pattern, self.a_body)
                if len(links) > 0:
                    for link in links:
                        # print(link,self.a_body)
                        page_link = link[1]
                        self.a_body = str(self.a_body).replace(page_link, '')
            # TODO сделать нормальную обработку
            except Exception as e:
                print(e, 'test')

    def delete_links2(self):
        # TODO сделать передачу имени в регулярку
        old_sitename = self.config["old_name"]
        pattern_page = r'(<a href=\"((http:\/\/(?:ruk\.|)pravmin74.ru)[^\"]{0,500})\"[^>]{0,100}>)'
        pattern_list = {
            "page_link":        pattern_page,           # паттерн для поиска ссылок на страницы
        }
        for link_type, pattern in pattern_list.items():
            try:
                links = re.findall(pattern, self.a_body)
                if len(links) > 0:
                    for link in links:
                        print(link, self.a_body)
            # TODO сделать нормальную обработку
            except Exception as e:
                print(e, 'test')

    # Получение медиафайлов из таблицы
    def get_mediafile_from_table(self, db_local):
        null_news = []
        pattern_file_1 = r'(\/(PublicationItemImage\/Image\/src\/[0-9]{1,5}\/)([^>]{1,75}))'
        pattern_list = {
            "mediafiles": pattern_file_1,         # паттерн 1
        }
        newsfiles_list = db_local.get_news_files_list(self.old_id)
        mediafiles = []
        for mediafile in newsfiles_list:
            old_path = mediafile[0]
            # Проверка пустой ли путь у файлв Новостей (запись есть, но значение пустое, то добавлять в список пуcтых)
            if old_path:
                file_path = str(old_path).replace("\\", "/")
                for link_type, pattern in pattern_list.items():
                    try:
                        links = re.findall(pattern, file_path)
                        # Если есть совпадения
                        if len(links) > 0:
                            for link in links:
                                data = {
                                    "file_full_path":       link[0],    # Ссылка на файл.                   Пример:     /PublicationItemImage/Image/src/178/IMG_2038.JPG
                                    "file_relative_path":   link[1],    # Папка файла.                      Пример:     /PublicationItemImage/Image/src/178/
                                    "file":                 link[2],    # Имя файла с расширением.          Пример:     IMG_2038.JPG
                                }
                                file = NewsMediaFile(self.config, data)
                                mediafiles.append(file)
                                # TODO запись в атрибут медиафайлы объектов через запятую
                                if self.mediaFiles != '':
                                    self.mediaFiles = ','.join((self.mediaFiles, file.str_new_link))
                                else:
                                    self.mediaFiles = file.str_new_link
                    except AttributeError as e:
                        print('Ошибка в создании файла Новостей', e)
            else:
                null_news.append(self.old_id)
                print(f'Отсутствует имя файла ид старой новости : {self.old_id}')
        return mediafiles, null_news


class File:
    def __init__(self, config, data):
        root = Path.cwd()
        self.sitename = config["new_name"]
        self.file_full_path = data["file_full_path"]
        self.file_relative_path = data["file_relative_path"]
        self.file = data["file"]
        self.encoded_filename = urllib.parse.unquote(self.file)
        self.path_root_old_file = root / 'source_files' / self.sitename / self.file_relative_path / self.encoded_filename
        self.new_link = ""
        self.str_new_link = ""

    def copy_news_file(self):
        # Копирование файлов
        root = Path.cwd()
        self.path_root_new_file = root / 'new_files' / self.sitename / self.new_link
        self.path_root_new_folder = self.path_root_new_file.parent
        copy_file(self.path_root_old_file,  self.path_root_new_folder)


class NewsIndexImgFile(File):
    def __init__(self, config, data):
        super().__init__(config, data)
        folder_name = Path(self.file_relative_path).name
        self.new_link = "".join(("files/ogvspb/pictures/", self.sitename, "/", folder_name, "/", self.file))
        self.str_new_link = "".join(("/ogvspb/pictures/", self.sitename, "/", folder_name, "/", self.file, "@cmsFile.doc"))


class NewsFile(File):
    def __init__(self, config, data):
        super().__init__(config, data)
        # TODO проверить правильность ссылок
        # TODO подумать могут ли быть в разлинчных директориях файлы с одинаковым именем
        self.new_link = "".join(("files/news_mediafiles/", self.sitename, "/", self.file))
        self.str_new_link = "".join(("files/news_mediafiles/", self.sitename, "/", self.file))


class NewsMediaFile(File):
    def __init__(self, config, data):
        super().__init__(config, data)
        # TODO проверить правильность ссылок
        # TODO подумать могут ли быть в разлинчных директориях файлы с одинаковым именем
        folder_name = Path(self.file_relative_path).name
        self.new_link = "".join(("files/news_mediafiles/", self.sitename, "/", folder_name, "/", self.file))
        self.str_new_link = "".join(("/news_mediafiles/", self.sitename, "/", folder_name, "/", self.file, "@cmsFile.doc"))


class NpaFile(File):
    def __init__(self, config, data):
        super().__init__(config, data)
        # TODO проверить правильность ссылок
        # TODO подумать могут ли быть в разлинчных директориях файлы с одинаковым именем
        self.new_link = "".join(("files/norm_act/", self.sitename, "/", self.file))
        self.str_new_link = "".join(("/norm_act/", self.sitename, "/", self.file, "@cmsFile.doc"))