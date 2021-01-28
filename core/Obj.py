from pathlib import Path
import re
import urllib.parse
from datetime import datetime


class Obj():
    def __init__(self, params, config):
        self.config = config
        self.folder_name = config["new_name"]
        self.old_sitename = config["old_name"]
        self.classification = config["classification"]
        self.body = self.clean_body(params["body"])
        self.structure = params["structure"]
        self.old_id = params["old_id"]
        self.title = params["title"]
        self.date_publication = self.transform_date(params["publ_date"])
        self.objFiles = ''
        # TODO Подумать можно ли сделать лучше, нужен
        self.section_title = ''

        self.re_file = r'([^>\"\/]{1,450}\.[a-zA-Z0-9]{2,5})'
        self.re_sitename = fr'(?:https?:\/\/(?:www\.|ruk\.|){self.old_sitename}|(?://|){self.old_sitename}|)'
        self.re_prefix = r'(?:(?:id|class|alt|height|target|width|style|type)=\"[^\"]{0,50}\"\s|){0,5}'

    # TODO
    def transform_date(self, raw_date):
        date = []
        if type(raw_date) == int:
            date = datetime.fromtimestamp(raw_date).strftime("%d.%m.%Y %H:%M:%S")
        elif raw_date is None:
            date = ''
            print(f'Пустая дата в объекте id {self.old_id}')
        elif isinstance(raw_date, datetime):
            date = raw_date.strftime("%d.%m.%Y %H:%M:%S")
        else:
            print(f'error date {date} {type(raw_date)}')
        return date

    def clean_body(self, raw_text):
        # print(raw_text)
        # print(updated_test)
        if raw_text:
            updated_test = urllib.parse.unquote(raw_text).strip("").replace("^", "#")
            body = re.sub(r'(?:<p style=\"text-align: justify;\">\s?(?:<[a-z]{1,2}>|\s?\&nbsp;|)<\/p>|\r|\n|<div>\s{0,3}<br \/>\s{0,3}<\/div>)', '', updated_test)
        else:
            body = ''
        return body

    def get_patterns_file(self):
        # TODO сделать передачу имени в регулярку
        genum_pattern_file_1 = fr'(<a href=\"({self.re_sitename}\/(((?:dokumentydok\/[^\/]{{1,75}}|upload\/iblock\/[^\/]{{0,4}}|Upload\/files|Files\/DiskFile\/(?:|[0-9]{{4}}\/)[a-zA-Z]{{1,10}}|opendata|Storage\/Image\/PublicationItem\/Image\/src\/[0-9]{{1,5}})\/){self.re_file}))\s?\"[^>]{{0,250}}>)'
        genum_pattern_file_2 = fr'(<(?:img|input)\s{self.re_prefix}src=\"({self.re_sitename}\/(((?:Upload\/(?:files|images)\/|Storage\/Image\/PublicationItem\/(?:Article|Image)\/src\/[0-9]{{1,5}}\/)){self.re_file}))\"[^>]{{0,550}}>)'
        genum_pattern_file_3 = fr'(<a href=\"({self.re_sitename}\/((Files\/VideoFiles\/){self.re_file}))\s?\"[^>]{{0,250}}>)'

        # TODO проверить регулярки для битрикса по файлам
        bitrix_pattern_file_1 = fr'(<img\s{self.re_prefix}src=\"({self.re_sitename}\/(([^\"\/]{{1,40}}\/(?:medialibrary\/[^\/]{{1,5}}\/|)){self.re_file}))\"[^>]{{0,550}}>)'
        bitrix_pattern_file_2 = fr'(<a\s{self.re_prefix}href=\"({self.re_sitename}\/(?:bitrix\/redirect\.php\?event1=download&amp;event2=update&amp;event3=[^\/\"]{{1,100}};goto=\/|)(([^\"\/]{{1,40}}\/(?:[^\"\/]{{1,100}}\/|){{0,4}}){self.re_file}))\"[^>]{{0,550}}>)'

        drupal_pattern_file_1 = fr'(<a\s{self.re_prefix}href=\"({self.re_sitename}\/((sites\/default\/files\/(?:imceFiles\/user-[0-9]{{1,4}}\/|imce\/|)){self.re_file}))\"[^>]{{0,550}}>)'
        drupal_pattern_file_2 = fr'(<img\s{self.re_prefix}src=\"({self.re_sitename}\/((sites\/default\/files\/(?:imceFiles\/user-[0-9]{{1,4}}\/|imce\/|)){self.re_file}))\"[^>]{{0,550}}>)'
        # print(drupal_pattern_file_1)

        pattern_list = {
            "genum_file_1":    genum_pattern_file_1,        # паттерн 1 файлы
            "genum_file_2":    genum_pattern_file_2,        # паттерн 2 img
            "genum_file_3":    genum_pattern_file_3,        # паттерн 3 видео
            "drupal_file_1":   drupal_pattern_file_1,       # паттерн
            "drupal_file_2":   drupal_pattern_file_2,       # паттерн
            # "bitrix_file_1":   bitrix_pattern_file_1,       # паттерн
            # "bitrix_file_2":   bitrix_pattern_file_2,       # паттерн
        }
        return pattern_list

    def get_patterns_image(self):
        # TODO сделать передачу имени в регулярку

        genum_pattern_file_1 = fr'(<(?:img|input)\s{self.re_prefix}src=\"({self.re_sitename}\/(((?:Upload\/(?:files|images)\/|Storage\/Image\/PublicationItem\/(?:Article|Image)\/src\/[0-9]{{1,5}}\/)){self.re_file}))\"[^>]{{0,550}}>)'

        bitrix_pattern_file_1 = fr'(<img\s{self.re_prefix}src=\"({self.re_sitename}\/(([^\"\/]{{1,40}}\/(?:medialibrary\/[^\/]{{1,5}}\/|)){self.re_file}))\"[^>]{{0,550}}>)'

        pattern_list = {
            "genum_file_1":    genum_pattern_file_1,         # паттерн 1 img
            "bitrix_file_1":   bitrix_pattern_file_1,        # паттерн 1 img
        }
        return pattern_list

    def get_patterns_link(self):

        genum_pattern_page = fr'(<a href=\"({self.re_sitename}\/(htmlpages\/(?:Show|CmsHtmlPageList)\/[^\"]{{1,75}}(?:\/[^\"]{{1,75}}\/[^\"]{{1,75}}|\/[^\"]{{1,75}}|)))\"[^>]{{0,250}}>)'
        genum_pattern_npa = fr'(<a href=\"({self.re_sitename}\/(LegalActs\/Show\/[^\/>]{{1,10}}))\"[^>]{{0,250}}>)'
        genum_pattern_single_page = fr'(<a href=\"({self.re_sitename}(?:|\/|\/(?:InternetReception|LegalActs)))\"[^>]{{0,250}}>)'
        genum_pattern_id = fr'(<a href=\"({self.re_sitename}\/Publications\/[a-zA-Z]{{1,15}}(?:\/Show\?id=[0-9]{{0,10}}|))\"[^>]{{0,250}}>)'

        drupal_pattern_npa = fr'(<a href=\"({self.re_sitename}(\/normativnye-pravovye-akty\/[^\/]{{1,250}}\/[^\/\"]{{1,250}}))\"[^>]{{0,100}}>)'
        drupal_pattern_news = fr'(<a href=\"({self.re_sitename}(\/novosti\/[^\/\"]{{1,250}}))\"[^>]{{0,100}}>)'
        drupal_pattern_page = fr'(<a href=\"({self.re_sitename}(\/[^\/\"]{{1,100}}))\"[^>]{{0,100}}>)'

        # TODO Протестировать заменяются ссылки на файлы
        bitrix_pattern_page = fr'(<a\s{self.re_prefix}href=\"({self.re_sitename}(?:\/?(?:[^\/\"]{{1,50}}\/|){{2}}(?:[^\/\"]{{1,250}}|)\/?)|)\"[^>]{{0,100}}>)'

        pattern_list = {
            "genum_page":           genum_pattern_page,         # genum паттерн для поиска ссылок на страницы
            "genum_npa":            genum_pattern_npa,          # genum паттерн для поиска ссылок на НПА
            "genum_single_page":    genum_pattern_single_page,  # genum паттерн для поиска ссылок на приемнуюкорневые страницы
            "genum_news":           genum_pattern_id,           # genum паттерн для поиска ссылок на новости
            "drupal_npa":           drupal_pattern_npa,          # drupal паттерн для поиска ссылок на НПА
            "drupal_news":          drupal_pattern_news,         # drupal паттерн для поиска ссылок на новости
            "drupal_page":          drupal_pattern_page,         # drupal паттерн для поиска ссылок на страницы
            "bitrix_page":          bitrix_pattern_page,        # bitrix паттерн для поиска ссылок на страницы
        }
        return pattern_list

    # Удалить ссылки в объекте
    def delete_page_links(self):
        pattern_list = self.get_patterns_link()
        for link_type, pattern in pattern_list.items():
            links = re.findall(pattern, self.body)
            if len(links) > 0:
                for link in links:
                    # print(link,self.a_body)
                    page_link = link[1]
                    self.body = str(self.body).replace(page_link, '')

    def replace_file_link(self, files):
        # Заменяется путь на файл в описании
        for file in files:
            self.body = str(self.body).replace(file.file_full_path, file.new_link)

    def delete_file_link(self, files):
        # Заменяется путь на файл в описании
        for file in files:
            self.body = str(self.body).replace(file.file_full_path, '')

    # TODO подумать как можно объединить общий функционал на функции обработки файлов
    # Получение файлов из описания
    def get_files_from_body(self, FileClass):
        pattern_list = self.get_patterns_file()
        files = []
        for link_type, pattern in pattern_list.items():
            links = re.findall(pattern, self.body)
            if len(links) > 0:
                for link in links:
                    data = {
                        "full_link":            link[0],    # Полная ссылка с a href и стилями. Пример:     <a href="http://ruk.pravmin74.ru/sites/default/files/imceFiles/user-333/soglasie_rk_2020.docx">
                        "file_full_path":       link[1],    # Ссылка на файл.                   Пример:     http://ruk.pravmin74.ru/sites/default/files/imceFiles/user-333/soglasie_rk_2020.docx
                        "file_path":            link[2],    # Полный путь до файла.             Пример:     sites/default/files/imceFiles/user-333/soglasie_rk_2020.docx
                        "file_relative_path":   link[3],    # Папка файла.                      Пример:     sites/default/files/imceFiles/user-333/
                        "file":                 link[4],    # Имя файла с расширением.          Пример:     soglasie_rk_2020.docx
                        "section_title":        self.section_title,
                    }
                    print(link[0])
                    file = FileClass(self.config, data)
                    files.append(file)
        return files

    # Обработка файлов из таблицы
    def get_files_from_table(self, files_raw, FileClass):
        null_files = []
        files = []
        pattern_file_genum = r'(\/(PublicationItemImage\/Image\/src\/[0-9]{1,5}\/)([^>]{1,75}))'
        pattern_file_bitrix = fr'(\/?(upload\/(?:[^\"\/]{{1,100}}\/|){{0,4}}){self.re_file})'
        # pattern_file_drupal = fr'(\/?(public:\/\/(?:[^\"\/]{{1,100}}\/|){{0,4}}){self.re_file})'
        pattern_file_drupal = fr'(\/?(sites\/default\/files\/(?:[^\"\/]{{1,100}}\/|){{0,4}}\/?){self.re_file})'

        pattern_list = {
            "files_genum":      pattern_file_genum,             # паттерн 1
            "files_bitrix":     pattern_file_bitrix,            # паттерн 1
            "files_drupal":     pattern_file_drupal,            # паттерн 1
        }
        for file in files_raw:
            old_path = file[0]
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
                                    "file_relative_path":   link[1],    # Папка файла.                      Пример:     PublicationItemImage/Image/src/178/
                                    "file":                 link[2],    # Имя файла с расширением.          Пример:     IMG_2038.JPG
                                    "section_title":        '',         # Для имени раздела
                                }
                                file = FileClass(self.config, data)
                                files.append(file)
                    except AttributeError as e:
                        print('Ошибка в создании файла Новостей', e)
            else:
                null_files.append(self.old_id)
                print(f'Отсутствует имя файла ид старой новости : {self.old_id}')
        return files, null_files

    def update_files(self, files):
        # TODO запись в атрибут медиафайлы объектов через запятую
        for file in files:
            if self.objFiles != '':
                if file.str_new_link not in self.objFiles:
                    self.objFiles = ','.join((self.objFiles, file.str_new_link))
            else:
                self.objFiles = file.str_new_link
