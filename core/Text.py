from core.Obj import Obj


class Text(Obj):
    # def __init__(self, data, config, page_path):
    def __init__(self, params, config):
        super().__init__(params, config)
        self.body = self.body.replace("\n\n\n", "\n").replace("\n\n", "\n")
        self.page_path = params["page_path"]
        self.section_title = self.split_path()

    def split_path(self):
        # Пути могут быть как виндовые так и линуксовые, поэтому нужна проверка
        split_linux = self.page_path.split('/')
        split_windows = self.page_path.split('\\')
        section_title = ''
        if len(split_linux) > 1:
            section_title = split_linux[0]
        elif len(split_windows) > 1:
            section_title = split_windows[0]
        return section_title
