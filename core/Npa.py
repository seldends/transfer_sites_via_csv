import re
from core.Obj import Obj
from core.File import NpaFile


class Npa(Obj):
    def __init__(self, params, config):
        super().__init__(params, config)
        self.date = params["date"]
        self.number = params["number"]