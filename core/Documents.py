import re
from core.Obj import Obj
from core.File import DocFile


class Doc(Obj):
    def __init__(self, params, config):
        super().__init__(params, config)
        self.date = params["date"]

    def get_data(self):
        data = {
                'page':             self.structure,
                'classification':   self.classification,
                'title':            self.title,
                'description':      re.sub(r'[\n]{2,3}', r'', self.body),
                "publ_date":        self.date_publication.strftime("%d.%m.%Y %H:%M:%S"),
                'file':             self.objFiles,
            }
        return data
