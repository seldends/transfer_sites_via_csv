from pathlib import Path
from utils.util import save_file
from core.Obj import Obj


class Page(Obj):
    def __init__(self, params, config):
        super().__init__(params, config)
        self.parent_id = params["parent_id"]
        self.alias = params["alias"]
        self.path = params["path"]
        self.level = params["level"]
        self.folder_path = params["folder_path"]
        self.path_from_titles = []

    def get_data(self):
        data = (
            self.old_id, self.parent_id, self.title,
            self.body, self.alias, self.path,
            self.level
        )
        return data

# Возвращает путь составленный из заголовков страниц
    def get_title_from_path(self, db_local):
        path_titles = []
        page_path = self.path.split('/')
        for parent_path in page_path:
            page_title = db_local.get_title_from_path(parent_path)
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
            save_file(full_path / page_name_txt, self.body)
            save_file(full_path / page_name_html, self.body)
        except OSError as e:
            print(e, self.path_from_titles)
            # print(f"{fspath(full_path)} len {len(fspath(full_path).encode('utf-8'))}")
            # print(f"{fspath(full_path / page_name_txt)} len {len(fspath(full_path / page_name_txt).encode('utf-8'))}")
            # print(f"{fspath(full_path / page_name_html)} len {len(fspath(full_path / page_name_html).encode('utf-8'))}")