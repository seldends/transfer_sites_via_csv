from pathlib import Path
import urllib.parse
# from utils.util import copy_file
import shutil


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
        root = Path.cwd()
        self.path_root_new_file = root / 'new_files' / self.sitename / self.new_link
        self.path_root_new_folder = self.path_root_new_file.parent
        self.path_root_new_folder.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copy2(self.path_root_old_file, self.path_root_new_folder)
        except FileNotFoundError as e:
            print(self.file_full_path, self.file, self.path_root_old_file)
            print(f'{e} Нет файла "{self.path_root_old_file}" {self.path_root_new_folder}')

class NewsIndexImgFile(File):
    def __init__(self, config, data):
        super().__init__(config, data)
        folder_name = Path(self.file_relative_path).name
        self.new_link = "".join(("files/ogvspb/pictures/", self.sitename, "/", folder_name, "/", self.file))
        self.str_new_link = "".join(("/ogvspb/pictures/", self.sitename, "/", folder_name, "/", self.file, "@cmsFile.doc"))


class NewsFile(File):
    def __init__(self, config, data):
        super().__init__(config, data)
        # TODO подумать могут ли быть в разлинчных директориях файлы с одинаковым именем
        self.new_link = "".join(("files/news_mediafiles/", self.sitename, "/", self.file))
        self.str_new_link = "".join(("files/news_mediafiles/", self.sitename, "/", self.file))


class NewsMediaFile(File):
    def __init__(self, config, data):
        super().__init__(config, data)
        # TODO подумать могут ли быть в разлинчных директориях файлы с одинаковым именем
        folder_name = Path(self.file_relative_path).name
        self.new_link = "".join(("files/news_mediafiles/", self.sitename, "/", folder_name, "/", self.file))
        self.str_new_link = "".join(("/news_mediafiles/", self.sitename, "/", folder_name, "/", self.file, "@cmsFile.doc"))


class NpaFile(File):
    def __init__(self, config, data):
        super().__init__(config, data)
        # TODO подумать могут ли быть в разлинчных директориях файлы с одинаковым именем
        self.new_link = "".join(("files/norm_act/", self.sitename, "/", self.file))
        self.str_new_link = "".join(("/norm_act/", self.sitename, "/", self.file, "@cmsFile.doc"))


class VacancyFile(File):
    def __init__(self, config, data):
        super().__init__(config, data)
        # TODO подумать могут ли быть в разлинчных директориях файлы с одинаковым именем
        self.new_link = "".join(("files/vacancies/", self.sitename, "/", self.file))
        self.str_new_link = "".join(("/vacancies/", self.sitename, "/", self.file, "@cmsFile.doc"))


class AuctionFile(File):
    def __init__(self, config, data):
        super().__init__(config, data)
        # TODO подумать могут ли быть в разлинчных директориях файлы с одинаковым именем
        self.new_link = "".join(("files/auctions/", self.sitename, "/", self.file))
        self.str_new_link = "".join(("/auctions/", self.sitename, "/", self.file, "@cmsFile.doc"))


class PageFile(File):
    def __init__(self, config, data):
        super().__init__(config, data)
        # TODO проверить правильность ссылок
        self.new_link = "".join(("files/upload/", self.sitename, "/", self.section_title, '/', self.file))
        self.str_new_link = "".join(("files/upload/", self.sitename, "/", self.section_title, '/', self.file))


class DocFile(File):
    def __init__(self, config, data):
        super().__init__(config, data)
        # TODO подумать могут ли быть в разлинчных директориях файлы с одинаковым именем
        self.new_link = "".join(("files/documents/", self.sitename, "/", self.file))
        self.str_new_link = "".join(("/documents/", self.sitename, "/", self.file, "@cmsFile.doc"))