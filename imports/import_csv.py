import os

import pandas

from imports.TemplateFile import TemplateFile


class CsvFile(TemplateFile):

    def __init__(self, fpana, sep=","):
        self.fpana = fpana
        self.fpath = os.path.dirname(fpana)
        self.fname = os.path.basename(fpana)
        self.sep = sep

    def read_file(self):
        self.df = pandas.read_csv(self.fpana, sep=self.sep)

    def get_data(self):
        self.df = pandas.read_csv(self.fpana, sep=";", names=["date", "val"])
        self.df["date"] = pandas.to_datetime(self.df["date"],
                                             format="%d-%m-%y %H:%M")

    def _get_columns(self):
        self.df = pandas.read_csv(self.fpana, sep=self.sep)
        self.columns = self.df.columns
