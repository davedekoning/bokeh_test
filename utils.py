import os
import logging

import datetime


def create_mapping(m1, m2, d1):
    if m1 not in d1.keys():
        d1[m1] = []
    d1[m1].append(m2)
    return d1[m1]


def from_bokeh_timestamp(x, ref_date=datetime.datetime(1970, 1, 1),
                         time_unit="milliseconds"):
    ms = ["milliseconds", "ms"]
    if time_unit in ms:
        time_unit = "seconds"
        x = x / 1000
    new_date = ref_date + datetime.timedelta(**{time_unit: x})
    return new_date


def to_bokeh_timestamp(x, ref_date=datetime.datetime(1970, 1, 1),
                       time_unit="milliseconds"):
    ms = ["milliseconds", "ms"]
    new_timestamp = (x - ref_date).total_seconds()
    if time_unit in ms:
        new_timestamp = new_timestamp * 1000
    return new_timestamp


# def add_timedelta(timeunit, timesteps, ref_date):
#     input_dict = {timeunit: timesteps}
#     new_date = ref_date + datetime.timedelta(**input_dict)
#     return new_date
# 

# setup logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
logger.addHandler(sh)
