from pathlib import Path
import re
import urllib.parse
from utils import copy_file


class Obj():
    def __init__(self, config):
        self.config = config
        self.folder_name = config["new_name"]
        self.old_sitename = config["old_name"]
        self.body = ''
        # TODO Подумать можно ли сделать лучше, нужен
        self.section_title = ''

    # Удалить ссылки в объекте
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
        bitrix_pattern_page = r'(<a\s(?:(?:class|alt|target|id)=\"[^\"]{1,50}\"\s|){0,5}href=\"((?:https?:\/\/(?:www\.|)imchel\.ru|)(?:\/?(?:[^\/\"]{1,50}\/|)(?:[^\/\"]{1,50}\/|)(?:[^\/\"]{1,250}|)\/?)|)\"[^>]{0,100}>)'

        pattern_list = {
            "genum_page":           genum_pattern_page,         # genum паттерн для поиска ссылок на страницы
            "genum_npa":            genum_pattern_npa,          # genum паттерн для поиска ссылок на НПА
            "genum_single_page":    genum_pattern_single_page,  # genum паттерн для поиска ссылок на приемнуюкорневые страницы
            "genum_news":           genum_pattern_id,           # genum паттерн для поиска ссылок на новости
            "sinta_npa":            sinta_pattern_npa,          # sinta паттерн для поиска ссылок на НПА
            "sinta_news":           sinta_pattern_news,         # sinta паттерн для поиска ссылок на новости
            "sinta_page":           sinta_pattern_page,         # sinta паттерн для поиска ссылок на страницы
            "bitrix_page":          bitrix_pattern_page,
        }
        for link_type, pattern in pattern_list.items():
            try:
                links = re.findall(pattern, self.body)
                if len(links) > 0:
                    for link in links:
                        # print(link,self.a_body)
                        page_link = link[1]
                        self.body = str(self.body).replace(page_link, '')
            # TODO сделать нормальную обработку
            except Exception as e:
                print(e, 'test')

    # TODO подумать как можно объединить общий функционал на функции обработки файлов
    # Получение файла Новостей из описания Новостей
    def update_body(self, FileClass):
        old_sitename = self.old_sitename
        # TODO сделать передачу имени в регулярку
        genum_pattern_file_1 = fr'(<a href=\"((?:http:\/\/(?:www\.|){old_sitename}|)\/(((?:dokumentydok\/[^\/]{{1,75}}|upload\/iblock\/[^\/]{{0,4}}|Upload\/files|Files\/DiskFile\/(?:|[0-9]{{4}}\/)[a-zA-Z]{{1,10}}|opendata|Storage\/Image\/PublicationItem\/Image\/src\/[0-9]{{1,5}})\/)([^>]{{1,450}}\.[a-zA-Z]{{3,5}})))\s?\"[^>]{{0,250}}>)'
        genum_pattern_file_2 = fr'(<(?:img|input)\s(?:(?:id|class|alt)=\"[^\"]{{0,50}}\"\s|)(?:class=\"[^\/]{{0,50}}\"\s|)src=\"((?:https?:\/\/(?:www\.|){old_sitename}|)\/(((?:Upload\/(?:files|images)\/|Storage\/Image\/PublicationItem\/(?:Article|Image)\/src\/[0-9]{{1,5}}\/))([^>\/]{{1,450}}\.[a-zA-Z]{{3,5}})))\"[^>]{{0,550}}>)'
        genum_pattern_file_3 = r'(<a href=\"((?:http:\/\/(?:www\.|)szn74.ru|)\/((Files\/VideoFiles\/)([^>]{1,450}\.[a-zA-Z]{3,5})))\s?\"[^>]{0,250}>)'
        sinta_pattern_file_1 = r'(<a href=\"((?:http:\/\/(?:ruk\.|)pravmin74.ru|)\/((sites\/default\/files\/imceFiles\/user-[0-9]{1,4}\/)([^>]{1,450}\.[a-zA-Z]{3,5})))\"[^>]{0,550}>)'
        bitrix_pattern_file_1 = r'(<img\s(?:width=\"[0-9]{1,4}\"\s|)(?:alt=\"[^\"]{1,50}\"\s|)src=\"((?:http:\/\/imchel\.ru|)\/((upload\/(?:medialibrary\/[^\/]{1,5}\/|))([^>\"]{1,450}\.[a-zA-Z]{3,5})))\"[^>]{0,550}>)'
        bitrix_pattern_file_2 = r'(<a\s(?:(?:class|alt|target|id)=\"[^\"]{1,50}\"\s|){0,5}href=\"((?:http:\/\/imchel\.ru|)\/((upload\/(?:[^\"\/]{1,100}\/|){0,4})([^>\"]{1,450}\.[a-zA-Z]{3,5})))\"[^>]{0,550}>)'
        pattern_list = {
            "genum_file_1":    genum_pattern_file_1,         # паттерн 1 файлы
            "genum_file_2":    genum_pattern_file_2,         # паттерн 2 img
            "genum_file_3":    genum_pattern_file_3,         # паттерн 2 видео
            "sinta_file_1":    sinta_pattern_file_1,         # паттерн 2
            "bitrix_file_1":   bitrix_pattern_file_1,         # паттерн 2
            "bitrix_file_2":   bitrix_pattern_file_2,         # паттерн 2
        }
        files = []
        for link_type, pattern in pattern_list.items():
            try:
                links = re.findall(pattern, self.body)
                # print(links, pattern)
                # Если есть совпадения
                if len(links) > 0:
                    for link in links:
                        print(link)
                        data = {
                            "full_link":            link[0],    # Полная ссылка с a href и стилями. Пример:     <a href="http://ruk.pravmin74.ru/sites/default/files/imceFiles/user-333/soglasie_rk_2020.docx">
                            "file_full_path":       link[1],    # Ссылка на файл.                   Пример:     http://ruk.pravmin74.ru/sites/default/files/imceFiles/user-333/soglasie_rk_2020.docx
                            "file_path":            link[2],    # Полный путь до файла.             Пример:     sites/default/files/imceFiles/user-333/soglasie_rk_2020.docx
                            "file_relative_path":   link[3],    # Папка файла.                      Пример:     sites/default/files/imceFiles/user-333/
                            "file":                 link[4],    # Имя файла с расширением.          Пример:     soglasie_rk_2020.docx
                            "section_title":        self.section_title,
                        }
                        file = FileClass(self.config, data)
                        files.append(file)
                        # TODO разобраться
                        # self.a_body = str(self.a_body).replace(file.file_full_path, file.str_new_link)     # Замены ссылки
                        self.body = str(self.body).replace(file.file_full_path, file.new_link)
                        # self.body = re.sub(r'[\n]{2,3}', r'', self.body)
                        # temp_a_resume = re.sub(r'(?:<|)(?:\/|)[a-z]{1,5}>', r'', str(self.a_resume))
                        # temp2_a_resume = re.sub(r'[\n]{2,3}', r'', temp_a_resume)
                        # self.a_resume = temp2_a_resume
            # TODO сделать нормальную обработку
            except Exception as e:
                print(e, 'test')
        return files


class Npa(Obj):
    def __init__(self, params, config):
        super().__init__(config)
        self.body = params["body"]
        self.a_structure = params["structure"]
        self.old_id = params["old_id"]
        self.a_title = params["title"]
        self.a_date = params["date"]
        self.a_publ_date = params["publ_date"]
        self.a_classification = config["classification"]
        self.a_number = params["number"]
        self.npaFiles = ''

    def get_npafile_from_body(self, FileClass):
        old_sitename = self.old_sitename
        # TODO сделать передачу имени в регулярку
        genum_pattern_file_1 = fr'(<a href=\"((?:http:\/\/(?:www\.|){old_sitename}|)\/(((?:dokumentydok\/[^\/]{{1,75}}|upload\/iblock\/[^\/]{{0,4}}|Upload\/files|Files\/DiskFile\/(?:|[0-9]{{4}}\/)[a-zA-Z]{{1,10}}|opendata|Storage\/Image\/PublicationItem\/Image\/src\/[0-9]{{1,5}})\/)([^>]{{1,450}}\.[a-zA-Z]{{3,5}})))\s?\"[^>]{{0,250}}>)'
        genum_pattern_file_2 = fr'(<(?:img|input)\s(?:(?:id|class|alt)=\"[^\"]{{0,50}}\"\s|)(?:class=\"[^\/]{{0,50}}\"\s|)src=\"((?:https?:\/\/(?:www\.|){old_sitename}|)\/(((?:Upload\/(?:files|images)\/|Storage\/Image\/PublicationItem\/(?:Article|Image)\/src\/[0-9]{{1,5}}\/))([^>\/]{{1,450}}\.[a-zA-Z]{{3,5}})))\"[^>]{{0,550}}>)'
        genum_pattern_file_3 = r'(<a href=\"((?:http:\/\/(?:www\.|)szn74.ru|)\/((Files\/VideoFiles\/)([^>]{1,450}\.[a-zA-Z]{3,5})))\s?\"[^>]{0,250}>)'
        sinta_pattern_file_1 = r'(<a href=\"((?:http:\/\/(?:ruk\.|)pravmin74.ru|)\/((sites\/default\/files\/imceFiles\/user-[0-9]{1,4}\/)([^>]{1,450}\.[a-zA-Z]{3,5})))\"[^>]{0,550}>)'
        bitrix_pattern_file_1 = r'(<img\s(?:width=\"[0-9]{1,4}\"\s|)(?:alt=\"[^\"]{1,50}\"\s|)src=\"((?:http:\/\/imchel\.ru|)\/((upload\/(?:medialibrary\/[^\/]{1,5}\/|))([^>\"]{1,450}\.[a-zA-Z]{3,5})))\"[^>]{0,550}>)'
        bitrix_pattern_file_2 = r'(<a\s(?:(?:class|alt|target|id)=\"[^\"]{1,50}\"\s|){0,5}href=\"((?:http:\/\/imchel\.ru|)\/((upload\/(?:[^\"\/]{1,100}\/|){0,4})([^>\"]{1,450}\.[a-zA-Z]{3,5})))\"[^>]{0,550}>)'
        bitrix_pattern_file_3 = r'(<a\s(?:(?:class|alt|target|id)=\"[^\"]{1,50}\"\s|){0,5}href=\"((?:http:\/\/imchel\.ru|)\/(?:bitrix\/redirect\.php\?event1=download&amp;event2=update&amp;event3=[^\/\"]{1,100};goto=\/|)((upload\/(?:[^\"\/]{1,100}\/|){0,4})([^>\"]{1,450}\.[a-zA-Z]{3,5})))\"[^>]{0,550}>)'
        pattern_list = {
            "genum_file_1":    genum_pattern_file_1,         # паттерн 1 файлы
            "genum_file_2":    genum_pattern_file_2,         # паттерн 2 img
            "genum_file_3":    genum_pattern_file_3,         # паттерн 2 видео
            "sinta_file_1":    sinta_pattern_file_1,         # паттерн 2
            "bitrix_file_1":   bitrix_pattern_file_1,         # паттерн 2
            "bitrix_file_2":   bitrix_pattern_file_2,         # паттерн 2
            "bitrix_file_3":   bitrix_pattern_file_3,         # паттерн 2
        }
        files = []
        for link_type, pattern in pattern_list.items():
            try:
                links = re.findall(pattern, self.body)
                # print(links, pattern)
                # Если есть совпадения
                if len(links) > 0:
                    for link in links:
                        print(link)
                        data = {
                            "full_link":            link[0],    # Полная ссылка с a href и стилями. Пример:     <a href="http://ruk.pravmin74.ru/sites/default/files/imceFiles/user-333/soglasie_rk_2020.docx">
                            "file_full_path":       link[1],    # Ссылка на файл.                   Пример:     http://ruk.pravmin74.ru/sites/default/files/imceFiles/user-333/soglasie_rk_2020.docx
                            "file_path":            link[2],    # Полный путь до файла.             Пример:     sites/default/files/imceFiles/user-333/soglasie_rk_2020.docx
                            "file_relative_path":   link[3],    # Папка файла.                      Пример:     sites/default/files/imceFiles/user-333/
                            "file":                 link[4],    # Имя файла с расширением.          Пример:     soglasie_rk_2020.docx
                            "section_title":        self.section_title,
                        }
                        file = FileClass(self.config, data)
                        files.append(file)
                        # TODO разобраться
                        if self.npaFiles != '':
                            self.npaFiles = ','.join((self.npaFiles, file.str_new_link))
                        else:
                            self.npaFiles = file.str_new_link
                        self.body = str(self.body).replace(file.file_full_path, '')
            # TODO сделать нормальную обработку
            except Exception as e:
                print(e, 'test')
        return files

    # Получение медиафайлов из таблицы
    def get_npafile_from_table(self, db_local):
        null_npa = []
        pattern_file_genum = r'(\/(PublicationItemImage\/Image\/src\/[0-9]{1,5}\/)([^>]{1,75}))'
        pattern_file_bitrix = r'(\/?(upload\/(?:[^\"\/]{1,100}\/|){0,4})([^>\"]{1,450}\.[a-zA-Z]{3,5}))'
        pattern_list = {
            "npafiles_genum":   pattern_file_genum,         # паттерн 1
            "npafiles_bitrix":  pattern_file_bitrix,         # паттерн 1
        }
        npafiles_list = db_local.get_npa_files_list(self.old_id)
        npafiles = []
        for npafile in npafiles_list:
            old_path = npafile[0]
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
                                    "section_title":        '',    # Имя файла с расширением.          Пример:     IMG_2038.JPG
                                }
                                file = NpaFile(self.config, data)
                                npafiles.append(file)
                                # TODO запись в атрибут медиафайлы объектов через запятую
                                if self.npaFiles != '':
                                    self.npaFiles = ','.join((self.npaFiles, file.str_new_link))
                                else:
                                    self.npaFiles = file.str_new_link
                    except AttributeError as e:
                        print('Ошибка в создании файла Новостей', e)
            else:
                null_npa.append(self.old_id)
                print(f'Отсутствует имя файла ид старой новости : {self.old_id}')
        return npafiles, null_npa


class Auction(Obj):
    def __init__(self, params, config):
        super().__init__(config)
        self.old_id = params["old_id"]
        self.body = params["body"]
        self.structure = params["structure"]
        self.title = params["title"]
        self.date_publication = params["publ_date"]
        self.date_expiration = params["expirationDate"]
        self.date_trading = params["tradingDate"]
        self.linkTorg = params["linkTorg"]
        self.linkMap = params["linkMap"]
        self.linkUTP = params["linkUTP"]
        self.numberUTP = params["numberUTP"]
        self.classification = config["classification"]
        self.auctionFiles = ''

    def get_auctionfile_from_body(self, FileClass):
        old_sitename = self.old_sitename
        # TODO сделать передачу имени в регулярку
        bitrix_pattern_file_1 = r'(<img\s(?:width=\"[0-9]{1,4}\"\s|)(?:alt=\"[^\"]{1,50}\"\s|)src=\"((?:http:\/\/imchel\.ru|)\/((upload\/(?:medialibrary\/[^\/]{1,5}\/|))([^>\"]{1,450}\.[a-zA-Z]{3,5})))\"[^>]{0,550}>)'
        bitrix_pattern_file_2 = r'(<a\s(?:(?:class|alt|target|id)=\"[^\"]{1,50}\"\s|){0,5}href=\"((?:http:\/\/imchel\.ru|)\/((upload\/(?:[^\"\/]{1,100}\/|){0,4})([^>\"]{1,450}\.[a-zA-Z]{3,5})))\"[^>]{0,550}>)'
        bitrix_pattern_file_3 = r'(<a\s(?:(?:class|alt|target|id)=\"[^\"]{1,50}\"\s|){0,5}href=\"((?:http:\/\/imchel\.ru|)\/(?:bitrix\/redirect\.php\?event1=download&amp;event2=update&amp;event3=[^\/\"]{1,100};goto=\/|)((upload\/(?:[^\"\/]{1,100}\/|){0,4})([^>\"]{1,450}\.[a-zA-Z]{3,5})))\"[^>]{0,550}>)'
        pattern_list = {
            "bitrix_file_1":   bitrix_pattern_file_1,         # паттерн 1
            "bitrix_file_2":   bitrix_pattern_file_2,         # паттерн 2
            "bitrix_file_3":   bitrix_pattern_file_3,         # паттерн 3
        }
        files = []
        for link_type, pattern in pattern_list.items():
            try:
                links = re.findall(pattern, self.body)
                # print(links, pattern)
                # Если есть совпадения
                if len(links) > 0:
                    for link in links:
                        print(link)
                        data = {
                            "full_link":            link[0],    # Полная ссылка с a href и стилями. Пример:     <a href="http://ruk.pravmin74.ru/sites/default/files/imceFiles/user-333/soglasie_rk_2020.docx">
                            "file_full_path":       link[1],    # Ссылка на файл.                   Пример:     http://ruk.pravmin74.ru/sites/default/files/imceFiles/user-333/soglasie_rk_2020.docx
                            "file_path":            link[2],    # Полный путь до файла.             Пример:     sites/default/files/imceFiles/user-333/soglasie_rk_2020.docx
                            "file_relative_path":   link[3],    # Папка файла.                      Пример:     sites/default/files/imceFiles/user-333/
                            "file":                 link[4],    # Имя файла с расширением.          Пример:     soglasie_rk_2020.docx
                            "section_title":        self.section_title,
                        }
                        file = FileClass(self.config, data)
                        files.append(file)
                        # TODO разобраться
                        if self.auctionFiles != '':
                            self.auctionFiles = ','.join((self.auctionFiles, file.str_new_link))
                        else:
                            self.auctionFiles = file.str_new_link
                        self.body = str(self.body).replace(file.file_full_path, '')
            # TODO сделать нормальную обработку
            except Exception as e:
                print(e, 'test')
        return files

    def bitrix_get_utp_from_body(self):
        old_sitename = self.old_sitename
        # TODO сделать передачу имени в регулярку
        bitrix_pattern_file_1 = r'(<a\s(?:(?:class|alt|target|id)=\"[^\"]{1,50}\"\s|){0,5}href=\"(http:\/\/utp\.sberbank-ast\.ru\/AP\/NBT\/PurchaseView\/[0-9]{1,3}\/[0-9]{1,3}\/[0-9]{1,3}\/[0-9]{1,10})\"[^>]{0,550}>([^<]{1,50})<\/a>)'
        pattern_list = {
            "bitrix_file_1":   bitrix_pattern_file_1,         # паттерн 2
        }
        files = []
        for link_type, pattern in pattern_list.items():
            try:
                links = re.findall(pattern, self.body)
                if len(links) > 0:
                    for link in links:
                        print(link)
                        data = {
                            "full_link":        link[0],    # Полная ссылка с a href и стилями. Пример:     <a target="_blank" href="http://utp.sberbank-ast.ru/AP/NBT/PurchaseView/9/0/0/680364">SBR012-2012020056</a>
                            "link_utp":         link[1],    # Ссылка на файл.                   Пример:     http://utp.sberbank-ast.ru/AP/NBT/PurchaseView/9/0/0/680364
                            "number_utp":       link[2],    # Полный путь до файла.             Пример:     SBR012-2012020056
                        }
                        self.linkUTP = data["link_utp"]
                        self.numberUTP = data["number_utp"]
                        # TODO разобраться
                        self.body = str(self.body).replace(data["full_link"], '').replace("Номер извещения на универсальной торговой площадке", '')
            # TODO сделать нормальную обработку
            except Exception as e:
                print(e, 'test')
        return files

    # Получение медиафайлов из таблицы
    def get_auctionfile_from_table(self, db_local):
        null_auction = []
        # pattern_file_genum = r'(\/(PublicationItemImage\/Image\/src\/[0-9]{1,5}\/)([^>]{1,75}))'
        pattern_file_bitrix = r'(\/?(upload\/(?:[^\"\/]{1,100}\/|){0,4})([^>\"]{1,450}\.[a-zA-Z]{3,5}))'
        pattern_list = {
            # "auctionfiles_genum":   pattern_file_genum,         # паттерн 1
            "auctionfiles_bitrix":  pattern_file_bitrix,         # паттерн 1
        }
        auctionfiles_list = db_local.get_auction_files_list(self.old_id)
        auctionfiles = []
        for auctionfile in auctionfiles_list:
            old_path = auctionfile[0]
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
                                    "section_title":        '',    # Имя файла с расширением.          Пример:     IMG_2038.JPG
                                }
                                file = AuctionFile(self.config, data)
                                auctionfiles.append(file)
                                # TODO запись в атрибут медиафайлы объектов через запятую
                                if self.auctionFiles != '':
                                    self.auctionFiles = ','.join((self.auctionFiles, file.str_new_link))
                                else:
                                    self.auctionFiles = file.str_new_link
                    except AttributeError as e:
                        print('Ошибка в создании файла Новостей', e)
            else:
                null_auction.append(self.old_id)
                print(f'Отсутствует имя файла ид старой новости : {self.old_id}')
        return auctionfiles, null_auction

class News(Obj):
    def __init__(self, params, config):
        super().__init__(config)
        self.body = params["body"]
        self.a_structure = params["structure"]
        self.old_id = params["old_id"]
        self.a_title = params["title"]
        self.a_date = params["date"]
        self.a_image_index = params["image_index"]
        self.a_publ_date = params["publ_date"]
        self.a_resume = params["resume"]
        self.a_classification = config["classification"]
        self.isPublish = 'Да'
        self.pubmain = 'Да'
        self.mediaFiles = ''

    def delete_links2(self):
        # TODO сделать передачу имени в регулярку
        pattern_page = r'(<a href=\"((http:\/\/(?:ruk\.|)pravmin74.ru)[^\"]{0,500})\"[^>]{0,100}>)'
        pattern_list = {
            "page_link":        pattern_page,           # паттерн для поиска ссылок на страницы
        }
        for link_type, pattern in pattern_list.items():
            try:
                links = re.findall(pattern, self.body)
                if len(links) > 0:
                    for link in links:
                        print(link, self.body)
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
        self.file_relative_path = urllib.parse.unquote(data["file_relative_path"])
        self.file = urllib.parse.unquote(data["file"])
        self.section_title = data["section_title"]
        self.path_root_old_file = root / 'source_files' / self.sitename / self.file_relative_path / self.file
        self.new_link = ""
        self.str_new_link = ""

    def copy_file(self):
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

class AuctionFile(File):
    def __init__(self, config, data):
        super().__init__(config, data)
        # TODO проверить правильность ссылок
        # TODO подумать могут ли быть в разлинчных директориях файлы с одинаковым именем
        self.new_link = "".join(("files/auctions/", self.sitename, "/", self.file))
        self.str_new_link = "".join(("/auctions/", self.sitename, "/", self.file, "@cmsFile.doc"))

class PageFile(File):
    def __init__(self, config, data):
        super().__init__(config, data)
        self.new_link = "".join(("files/upload/", self.sitename, "/", self.section_title, '/', self.file))
        self.str_new_link = "".join(("files/upload/", self.sitename, "/", self.section_title, '/', self.file))
