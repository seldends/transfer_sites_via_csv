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
                'text':             re.sub(r'[\n]{2,3}', r'', self.body),
                'classification':   self.classification,
                "publ_date":        self.date_publication,
                "date":             self.date,
                "number":           self.number,
                'npaFiles':         self.objFiles,
            }
        return data

    def delete_empty(self):
        genum_pattern_1 = fr'(<img\s(?:(?:class|alt|target|id|height|style|width|src)=\"[^\"]{{0,50}}\"\s|){{1,5}}\/>)'
        genum_pattern_2 = fr'(<a href=\"\">(?:СКАЧАТЬ|ПОЛНЫЙ ТЕКСТ ПОСТАНОВЛЕНИЯ|<strong>ПОЛНЫЙ ТЕКСТ ПРИКАЗА<\/strong>)<\/a>)'
        pattern_list = {
            "genum_page":           genum_pattern_1,         # genum паттерн для поиска ссылок на страницы
            "genum_npa":            genum_pattern_2,          # genum паттерн для поиска ссылок на НПА
        }

        for link_type, pattern in pattern_list.items():
            links = re.findall(pattern, self.body)
            if len(links) > 0:
                for link in links:
                    self.body = str(self.body).replace(link, '')
