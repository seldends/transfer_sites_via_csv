import re
from core.Obj import Obj
from core.File import NpaFile


class Npa(Obj):
    def __init__(self, params, config):
        super().__init__(params, config)
        self.date = params["date"]
        self.number = params["number"]

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
            "genum_file_1":    genum_pattern_file_1,        # паттерн 1 файлы
            "genum_file_2":    genum_pattern_file_2,        # паттерн 2 img
            "genum_file_3":    genum_pattern_file_3,        # паттерн 3 видео
            "sinta_file_1":    sinta_pattern_file_1,        # паттерн 1
            "bitrix_file_1":   bitrix_pattern_file_1,       # паттерн 1 картинки
            "bitrix_file_2":   bitrix_pattern_file_2,       # паттерн 2 файлы
            "bitrix_file_3":   bitrix_pattern_file_3,       # паттерн 3 поломанные ссылки
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
                                if self.objFiles != '':
                                    self.objFiles = ','.join((self.objFiles, file.str_new_link))
                                else:
                                    self.objFiles = file.str_new_link
                    except AttributeError as e:
                        print('Ошибка в создании файла Новостей', e)
            else:
                null_npa.append(self.old_id)
                print(f'Отсутствует имя файла ид старой новости : {self.old_id}')
        return npafiles, null_npa
