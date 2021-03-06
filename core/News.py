import re
from core.Obj import Obj
from core.File import NewsMediaFile, NewsIndexImgFile


class News(Obj):
    def __init__(self, params, config):
        super().__init__(params, config)
        self.date = self.transform_date(params["date"])
        self.image_index = self.transform_index_image(params["image_index"])
        self.resume = self.clean_resume(params["resume"])
        self.isPublish = 'Да'
        self.pubmain = 'Да'

    def transform_index_image(self, raw_path):
        if raw_path:
            path = str(raw_path).replace("^", "#")
        else:
            path = None
        return path

    def clean_resume(self, raw_text):
        # TODO проверить почему не полностью работает strip
        resume = re.sub(r'(?:</?[a-z]{1,3}\s?(?:\/|style=\"text-align: justify;\"|)>|\r|\n|\t)','',str(raw_text).strip("").replace("^", "#"))
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

    def get_index_file(self):
        re_file = r'([^>\"\/]{1,450}\.[a-zA-Z0-9]{2,5})'
        pattern_file_genum = r'(\\(PublicationItem\\Image\\src\\[0-9]{1,5}\\)([^>\\]{1,75}))'
        pattern_file_drupal = fr'(\/?(sites\/default\/files\/(?:[^\"\/]{{1,100}}\/|){{0,4}}\/?){re_file})'
        pattern_list = {
            "indeximage_genum": pattern_file_genum,         # паттерн 1
            "indeximage_drupal": pattern_file_drupal,         # паттерн 1
        }
        old_path = self.image_index
        index_file = []
        # print(old_path)
        # Проверка пустой ли путь у файлв Новостей (запись есть, но значение пустое, то добавлять в список пуcтых)

        # if self.image_index:
        #     print(f'test {self.image_index}')
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

    def get_data(self):
        row = {
            'structure':        self.structure,
            'title':            self.title,
            'resume':           re.sub(r'[\n]{2,3}', r'', self.resume),
            'body':             re.sub(r'[\n]{2,3}', r'', self.body),
            'classification':   self.classification,
            'isPublish':        self.isPublish,
            'pubmain':          self.pubmain,
            "publ_date":        self.date_publication,
            "date":             self.date,
            'image_index':      self.image_index,
            'mediaFiles':       self.objFiles
        }
        return row
