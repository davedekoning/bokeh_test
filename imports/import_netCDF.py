import os
import datetime

import netCDF4
import numpy as np
import pandas
import logging
# import matplotlib.pyplot as plt

from utils import logger, create_mapping
from imports.TemplateFile import TemplateFile


class ncVariable():

    def __init__(self, name, standard_name, long_name, dimensions, data,
                 attdict):
        self.name = name
        self.standard_name = standard_name
        self.long_name = long_name
        self.dimensions = dimensions
        self.data = data
        self.attdict = attdict


class NetCDFFile(TemplateFile):
    default_loc_param = "observation_id"

    def __init__(self, fpana):
        self.fpana = fpana
        self.fpath = os.path.dirname(fpana)
        self.fname = os.path.basename(fpana)
        self._get_variables()
        if self.default_loc_param in self.all_variables:
            self._get_locations(self.default_loc_param)
            self._get_var_loc()
            self._get_loc_var()

    def _get_variables(self):
        self.variables = []
        with netCDF4.Dataset(self.fpana, "r") as nc_file:
            for key in nc_file.variables.keys():
                variable = nc_file.variables[key]
                if "time" in variable.dimensions and key != "time":
                    self.variables.append(key)
            self.all_variables = list(nc_file.variables.keys())

    def get_variables(self):
        with netCDF4.Dataset(self.fpana, "r") as nc_file:
            for key in self.variables:
                variable = nc_file.variables[key]
                vardata = variable[:]
                vd_shp = vardata.shape
                # logger.info("%s %s %s", key, vd_shp, variable.dimensions)
                if len(vd_shp) == 1:
                    # check lat, lon, geom, depth
                    pass
                elif len(vd_shp) == 2:
                    # check geom, else ts
                    pass
                elif len(vd_shp) == 3:
                    # geom ts
                    pass
                elif len(vd_shp) == 4:
                    # geom ts, depth
                    pass
                else:
                    pass

    def add_timedelta(self, timeunit, timesteps, ref_date):
        import datetime
        input_dict = {timeunit: timesteps}
        new_date = ref_date + datetime.timedelta(**input_dict)
        return new_date

    def get_data(self, variable):
        with netCDF4.Dataset(self.fpana, "r") as nc_file:
            self.vardata = nc_file.variables[variable][:]
            if "time" in nc_file.variables.keys():
                self.get_times(nc_file)
            else:
                self.timesteps = range(self.vardata.shape[0])

            # logger.info(nc_file.variables["time"])
            self.data = pandas.DataFrame(data=self.vardata,
                                         index=self.timesteps,
                                         columns=self.locations)

    def get_timeseries(self, column, ts=None):
        if ts is None:
            ts = self.data.index
        self.sr = self.data.loc[ts, column].copy()
        self.df = self.sr.reset_index()
        self.df.rename(columns={"index": "date",
                                column: "val"},
                       inplace=True)

    def get_times(self, nc_file):
        vartime = nc_file.variables["time"][:]
        units_str = nc_file.variables["time"].units
        time_unit = units_str.split()[0]
        date_ = units_str.split()[2]
        time_ = units_str.split()[3]
        ref_date = datetime.datetime.strptime(" ".join([date_, time_]),
                                              "%Y-%m-%d %H:%M:%S")
        self.timesteps = [self.add_timedelta(time_unit, int(timestep),
                                             ref_date)
                          for timestep in vartime]
        self.timesteps

    def get_values(self, variable):
        with netCDF4.Dataset(self.fpana, "r") as nc_file:
            vardata = nc_file.variables[variable][:]
        return vardata

    def search_loc(_list, _name):
        for item in _list:
            if _name.lower() in item.lower():
                logging.info(item)

    def _get_locations(self, variable):
        self.locations = self.combine_strings(variable)

    def combine_strings(self, variable, fmt="csl"):
        with netCDF4.Dataset(self.fpana, "r") as nc_file:
            vardata = nc_file.variables[variable][:]
        if fmt == "csl":
            if isinstance(vardata[0][0], str):
                combined_strings = ["".join(item).strip() for item in vardata]
            elif isinstance(vardata[0][0], np.bytes_):
                combined_strings = ["".join(np.array(item, dtype=str)).strip()
                                    for item in vardata]
        return combined_strings

    def _get_loc_var(self):
        self.loc_var_map = {}
        for param in self.variables:
            loc_list = self.var_loc_map[param]
            for loc_id in loc_list:
                self.loc_var_map[loc_id] = create_mapping(loc_id, param,
                                                          self.loc_var_map)

    def _get_var_loc(self):
        self.var_loc_map = {}
        with netCDF4.Dataset(self.fpana, "r") as nc_file:
            for param in self.variables:
                print(param)
                vardata = nc_file.variables[param][:]
                new_df = pandas.DataFrame(vardata, columns=self.locations)
                loc_list = list(new_df.dropna(how="all", axis=1).columns)
                self.var_loc_map[param] = loc_list
