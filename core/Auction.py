import re
from core.Obj import Obj
from core.File import AuctionFile


class Auction(Obj):
    def __init__(self, params, config):
        super().__init__(params, config)
        self.date_expiration = params["expirationDate"]
        self.date_trading = params["tradingDate"]
        self.linkTorg = params["linkTorg"]
        self.linkMap = params["linkMap"]
        self.linkUTP = params["linkUTP"]
        self.numberUTP = params["numberUTP"]
        self.objFiles = ''

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
            links = re.findall(pattern, self.body)
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
                    if self.objFiles != '':
                        self.objFiles = ','.join((self.objFiles, file.str_new_link))
                    else:
                        self.objFiles = file.str_new_link
                    self.body = str(self.body).replace(file.file_full_path, '')
        return files

    # Bitrix получение атрибутов ссылки и номер универсальной торговой площадки
    def bitrix_get_utp_from_body(self):
        bitrix_pattern_file_1 = r'(<a\s(?:(?:class|alt|target|id)=\"[^\"]{1,50}\"\s|){0,5}href=\"(http:\/\/utp\.sberbank-ast\.ru\/AP\/NBT\/PurchaseView\/[0-9]{1,3}\/[0-9]{1,3}\/[0-9]{1,3}\/[0-9]{1,10})\"[^>]{0,550}>([^<]{1,50})<\/a>)'
        pattern_list = {
            "bitrix_file_1":   bitrix_pattern_file_1,         # паттерн 2
        }
        for link_type, pattern in pattern_list.items():
            links = re.findall(pattern, self.body)
            if len(links) > 0:
                for link in links:
                    data = {
                        "full_link":        link[0],    # Полная ссылка с a href и стилями. Пример:     <a target="_blank" href="http://utp.sberbank-ast.ru/AP/NBT/PurchaseView/9/0/0/680364">SBR012-2012020056</a>
                        "link_utp":         link[1],    # Ссылка на файл.                   Пример:     http://utp.sberbank-ast.ru/AP/NBT/PurchaseView/9/0/0/680364
                        "number_utp":       link[2],    # Полный путь до файла.             Пример:     SBR012-2012020056
                    }
                    self.linkUTP = data["link_utp"]
                    self.numberUTP = data["number_utp"]
                    self.body = str(self.body).replace(data["full_link"], '').replace("Номер извещения на универсальной торговой площадке", '')

    # Получение медиафайлов из таблицы
    def get_auctionfile_from_table(self, db_local):
        null_auction = []
        # pattern_file_genum = r'(\/(PublicationItemImage\/Image\/src\/[0-9]{1,5}\/)([^>]{1,75}))'
        pattern_file_bitrix = r'(\/?(upload\/(?:[^\"\/]{1,100}\/|){0,4})([^>\"]{1,450}\.[a-zA-Z]{3,5}))'
        pattern_list = {
            # "auctionfiles_genum":   pattern_file_genum,         # паттерн файлы
            "auctionfiles_bitrix":  pattern_file_bitrix,         # паттерн файлы
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
                                    "section_title":        '',         # Раздел страницы.                  Пример:     Деятельность
                                }
                                file = AuctionFile(self.config, data)
                                auctionfiles.append(file)
                                # TODO запись в атрибут медиафайлы объектов через запятую
                                if self.objFiles != '':
                                    self.objFiles = ','.join((self.objFiles, file.str_new_link))
                                else:
                                    self.objFiles = file.str_new_link
                    except AttributeError as e:
                        print('Ошибка в создании файла Новостей', e)
            else:
                null_auction.append(self.old_id)
                print(f'Отсутствует имя файла ид старой новости : {self.old_id}')
        return auctionfiles, null_auction

    def get_data(self):
        data = {
                'category':         self.structure,
                'title':            self.title,
                "publ_date":        self.date_publication.strftime("%d.%m.%Y %H:%M:%S"),
                "expirationDate":   self.date_expiration.strftime("%d.%m.%Y %H:%M:%S"),
                "tradingDate":      self.date_trading.strftime("%d.%m.%Y %H:%M:%S"),
                'text':             re.sub(r'[\n]{2,3}', r'', self.body),
                "linkTorg":         self.linkTorg,
                "linkMap":          self.linkMap,
                "linkUTP":          self.linkUTP,
                "numberUTP":        self.numberUTP,
                'classification':   self.classification,
                'auctionFiles':     self.objFiles,
            }
        return data
