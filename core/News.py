import re
from core.Obj import Obj
from core.File import NewsMediaFile, NewsIndexImgFile


class News(Obj):
    def __init__(self, params, config):
        super().__init__(params, config)
        self.date = params["date"]
        self.image_index = str(params["image_index"]).replace("^", "#")
        self.resume = self.clean_resume(params["resume"])
        self.isPublish = 'Да'
        self.pubmain = 'Да'

    def clean_resume(self, raw_text):
        resume = re.sub(r'(?:</?[a-z]{1,3}\\s?(?:\/|style=\"text-align: justify;\"|)>|\r|\n|\t)','',str(raw_text).strip("").replace("^", "#"))
        return resume

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
                                    "section_title":        '',    # Имя файла с расширением.          Пример:     IMG_2038.JPG
                                }
                                file = NewsMediaFile(self.config, data)
                                mediafiles.append(file)
                                # TODO запись в атрибут медиафайлы объектов через запятую
                                if self.objFiles != '':
                                    self.objFiles = ','.join((self.objFiles, file.str_new_link))
                                else:
                                    self.objFiles = file.str_new_link
                    except AttributeError as e:
                        print('Ошибка в создании файла Новостей', e)
            else:
                null_news.append(self.old_id)
                print(f'Отсутствует имя файла ид старой новости : {self.old_id}')
        return mediafiles, null_news

    def get_index_file(self):
        pattern_file_1 = r'(\\(PublicationItem\\Image\\src\\[0-9]{1,5}\\)([^>\\]{1,75}))'
        pattern_list = {
            "indeximage": pattern_file_1,         # паттерн 1
        }
        old_path = self.image_index
        index_file = []
        # print(old_path)
        # Проверка пустой ли путь у файлв Новостей (запись есть, но значение пустое, то добавлять в список пуcтых)
        for link_type, pattern in pattern_list.items():
            try:
                links = re.findall(pattern, str(old_path))
                # Если есть совпадения
                if len(links) > 0:
                    for link in links:
                        data = {
                            "file_full_path":       link[0],    # Ссылка на файл.                   Пример:     \PublicationItem\Image\src\10836\images (24).jpg
                            "file_relative_path":   link[1],    # Папка файла.                      Пример:     PublicationItem\Image\src\10836\
                            "file":                 link[2],    # Имя файла с расширением.          Пример:     images (24).jpg
                            "section_title":        '',    # Имя файла с расширением.          Пример:     IMG_2038.JPG
                        }
                        file = NewsIndexImgFile(self.config, data)
                        self.image_index = file.str_new_link
                        index_file.append(file)
            except AttributeError as e:
                print('Ошибка в создании файла Новостей', e)
        return index_file
