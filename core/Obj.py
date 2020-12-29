from pathlib import Path
import re
import urllib.parse


class Obj():
    def __init__(self, params, config):
        self.config = config
        self.folder_name = config["new_name"]
        self.old_sitename = config["old_name"]
        self.classification = config["classification"]
        self.body = params["body"]
        self.structure = params["structure"]
        self.old_id = params["old_id"]
        self.title = params["title"]
        self.date_publication = params["publ_date"]
        self.objFiles = ''
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
            links = re.findall(pattern, self.body)
            if len(links) > 0:
                for link in links:
                    # print(link,self.a_body)
                    page_link = link[1]
                    self.body = str(self.body).replace(page_link, '')

    # TODO подумать как можно объединить общий функционал на функции обработки файлов
    # Получение файла Новостей из описания Новостей
    def update_body(self, FileClass):
        old_sitename = self.old_sitename
        # TODO сделать передачу имени в регулярку
        genum_pattern_file_1 = fr'(<a href=\"((?:http:\/\/(?:www\.|){old_sitename}|)\/(((?:dokumentydok\/[^\/]{{1,75}}|upload\/iblock\/[^\/]{{0,4}}|Upload\/files|Files\/DiskFile\/(?:|[0-9]{{4}}\/)[a-zA-Z]{{1,10}}|opendata|Storage\/Image\/PublicationItem\/Image\/src\/[0-9]{{1,5}})\/)([^>]{{1,450}}\.[a-zA-Z]{{3,5}})))\s?\"[^>]{{0,250}}>)'
        genum_pattern_file_2 = fr'(<(?:img|input)\s(?:(?:id|class|alt)=\"[^\"]{{0,50}}\"\s|)(?:class=\"[^\/]{{0,50}}\"\s|)src=\"((?:https?:\/\/(?:www\.|){old_sitename}|)\/(((?:Upload\/(?:files|images)\/|Storage\/Image\/PublicationItem\/(?:Article|Image)\/src\/[0-9]{{1,5}}\/))([^>\/]{{1,450}}\.[a-zA-Z]{{3,5}})))\"[^>]{{0,550}}>)'
        genum_pattern_file_3 = r'(<a href=\"((?:http:\/\/(?:www\.|)szn74.ru|)\/((Files\/VideoFiles\/)([^>]{1,450}\.[a-zA-Z]{3,5})))\s?\"[^>]{0,250}>)'
        sinta_pattern_file_1 = r'(<a href=\"((?:http:\/\/(?:ruk\.|)pravmin74.ru|)\/((sites\/default\/files\/imceFiles\/user-[0-9]{1,4}\/)([^>]{1,450}\.[a-zA-Z]{3,5})))\"[^>]{0,550}>)'
        bitrix_pattern_file_1 = r'(<img\s(?:width=\"[0-9]{1,4}\"\s|)(?:alt=\"[^\"]{1,50}\"\s|)src=\"((?:https?:\/\/imchel\.ru|)\/(([^\"\/]{1,40}\/(?:medialibrary\/[^\/]{1,5}\/|))([^>\"]{1,450}\.[a-zA-Z]{3,5})))\"[^>]{0,550}>)'
        # bitrix_pattern_file_2 = r'(<a\s(?:(?:class|alt|target|id)=\"[^\"]{1,50}\"\s|){0,5}href=\"((?:https?:\/\/imchel\.ru|)\/(([^\"\/]{1,40}\/(?:[^\"\/]{1,100}\/|){0,4})([^>\"]{1,450}\.[a-zA-Z]{3,5})))\"[^>]{0,550}>)'
        bitrix_pattern_file_3 = r'(<a\s(?:(?:class|alt|target|id)=\"[^\"]{1,50}\"\s|){0,5}href=\"((?:https?:\/\/imchel\.ru|)\/(?:bitrix\/redirect\.php\?event1=download&amp;event2=update&amp;event3=[^\/\"]{1,100};goto=\/|)(([^\"\/]{1,40}\/(?:[^\"\/]{1,100}\/|){0,4})([^>\"]{1,450}\.[a-zA-Z]{3,5})))\"[^>]{0,550}>)'
        pattern_list = {
            "genum_file_1":    genum_pattern_file_1,         # паттерн 1 файлы
            "genum_file_2":    genum_pattern_file_2,         # паттерн 2 img
            "genum_file_3":    genum_pattern_file_3,         # паттерн 2 видео
            "sinta_file_1":    sinta_pattern_file_1,         # паттерн 2
            "bitrix_file_1":   bitrix_pattern_file_1,         # паттерн 2
            # "bitrix_file_2":   bitrix_pattern_file_2,         # паттерн 2
            "bitrix_file_3":   bitrix_pattern_file_3,       # паттерн 3 поломанные ссылки
        }
        files = []
        for link_type, pattern in pattern_list.items():
            links = re.findall(pattern, self.body)
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
        return files
