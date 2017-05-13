import os
import xml.etree.ElementTree as ET
import datetime

import pandas

from utils import create_mapping
from imports.TemplateFile import TemplateFile


class XmlFile(TemplateFile):
    default_ns = None

    def __init__(self, fpana):
        self.fpana = fpana
        self.fpath = os.path.dirname(fpana)
        self.fname = os.path.basename(fpana)

        self.tree = ET.parse(self.fpana)
        self._get_default_namespace()
        self.series_list = self.tree.getroot().findall(
            self.default_ns + "series")
        self._get_locations()
        self._get_variables()
        self._get_loc_var()
        self._get_var_loc()

    def _get_default_namespace(self):
        with open(self.fpana, "r") as fx:
            lines = fx.readlines()
        for line in lines:
            if "xmlns" in line:
                split_line = line.split()
                for item in split_line:
                    if "xmlns=" in item:
                        self.default_ns = \
                            "{%s}" % item.split("=")[-1].strip('"')

    def get_data(self, variable, location):
        for series in self.series_list:
            header = series.find(self.default_ns + "header")
            param = header.findtext(self.default_ns + "parameterId")
            loc_id = header.findtext(self.default_ns + "locationId")
            if param == variable and loc_id == location:
                self.get_timeseries(series)

    def get_timeseries(self, series):
        event_list = series.findall(self.default_ns + "event")
        ts_dict = {"date": [],
                   "val": []}
        for event in event_list:
            date_str = " ".join([event.get("date"), event.get("time")])
            val_str = event.get("value")
            date_fmt = "%Y-%m-%d %H:%M:%S"
            ts_dict["date"].append(datetime.datetime.strptime(date_str,
                                                              date_fmt))
            ts_dict["val"].append(float(val_str))
        self.df = pandas.DataFrame(ts_dict)

    def _get_variables(self):
        self.variables = []
        for series in self.series_list:
            header = series.find(self.default_ns + "header")
            param = header.findtext(self.default_ns + "parameterId")
            if param not in self.variables:
                self.variables.append(param)

    def _get_locations(self):
        self.locations = []
        for series in self.series_list:
            header = series.find(self.default_ns + "header")
            loc_id = header.findtext(self.default_ns + "locationId")
            if loc_id not in self.locations:
                self.locations.append(loc_id)

    def _get_loc_var(self):
        self.loc_var_map = {}
        for series in self.series_list:
            header = series.find(self.default_ns + "header")
            param = header.findtext(self.default_ns + "parameterId")
            loc_id = header.findtext(self.default_ns + "locationId")
            # if loc_id not in self.loc_var_map.keys():
            #     self.loc_var_map[loc_id] = []
            # self.loc_var_map[loc_id].append(param)
            self.loc_var_map[loc_id] = create_mapping(loc_id, param,
                                                      self.loc_var_map)

    def _get_var_loc(self):
        self.var_loc_map = {}
        for series in self.series_list:
            header = series.find(self.default_ns + "header")
            param = header.findtext(self.default_ns + "parameterId")
            loc_id = header.findtext(self.default_ns + "locationId")
            # if param not in self.var_loc_map.keys():
            #     self.var_loc_map[param] = []
            # self.var_loc_map[param].append(loc_id)
            self.var_loc_map[param] = create_mapping(param, loc_id,
                                                     self.var_loc_map)
