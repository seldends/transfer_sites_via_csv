import re
from core.Obj import Obj
from core.File import NpaFile


class Npa(Obj):
    def __init__(self, params, config):
        super().__init__(params, config)
        self.date = self.transform_date(params["date"])
        self.number = params["number"]

    def get_data(self):
        data = {
                'structure':        self.structure,
                'title':            self.title,
                # 'text':             re.sub(r'[\n]{2,3}', r'', self.body),
                'text':             self.body,
                'classification':   self.classification,
                "publ_date":        self.date_publication,
                "date":             self.date,
                "number":           self.number,
                'npaFiles':         self.objFiles,
            }
        return data
