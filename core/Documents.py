import re
from core.Obj import Obj
from core.File import DocFile


class Doc(Obj):
    def __init__(self, params, config):
        super().__init__(params, config)
        self.date = params["date"]
