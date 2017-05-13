import os
# import sys
# import logging

# import numpy as np
# import pandas

import datetime

from bokeh.io import curdoc
from bokeh.plotting import figure, output_file, show
from bokeh.layouts import row, column, layout
from bokeh.models import Button, ColumnDataSource, Span, Range1d
from bokeh.models.glyphs import Circle

import matplotlib.pyplot as plt

from imports.import_csv import CsvFile
from imports.import_netCDF import NetCDFFile
from imports.import_xml import XmlFile
from utils import logger, to_bokeh_timestamp


def create_plot(files):
    Tools_x = "xwheel_zoom, xpan"

    p = figure(x_axis_type="datetime", tools=Tools_x,
               active_scroll="xwheel_zoom", active_drag="xpan")

    colors = ["blue", "red", "green"]
    sizes = [3, 2, 1]

    for file_, color, sz in zip(files, colors, sizes):
        logger.info("%s %s %s", file_.fname, color, sz)
        if file_.plot_type == "line":
            p.line(file_.df["date"], file_.df["val"], color=color,
                   line_width=sz)
        elif file_.plot_type == "point":
            p.circle(file_.df["date"], file_.df["val"], color=color,
                     marker_size=sz)

    return p


def fill_between(files):
    Tools_x = "xwheel_zoom, xpan"

    p = figure(x_axis_type="datetime", tools=Tools_x,
               active_scroll="xwheel_zoom", active_drag="xpan")

    colors = ["red", "red", "green"]
    sizes = [1, 1, 1]

    for file_, color, sz in zip(files, colors, sizes):
        logger.info("%s %s %s", file_.fname, color, sz)
        if file_.plot_type == "line":
            p.line(file_.df["date"], file_.df["val"], color=color,
                   line_width=sz)
        elif file_.plot_type == "point":
            p.circle(file_.df["date"], file_.df["val"], color=color,
                     marker_size=sz)

    if len(files) < 2:
        return p

    if len(files) > 2:
        files = files[:2]

    # Stappen
    # 1. bekijk of ze even lang zijn, met zelfde tijdstappen
    # 2. Snij bij indien niet even lang 
    #       (pak maximale minimum en minimale maximum)
    # 3. interpoleer indien verschillende tijdstappen
    #       zoek tijdstip en bepaalmet interpolatie de waarde
    # 4. Wat gebeurt er als ze kruisen?
    # Moet het mogelijk zijn om er ook 3 te tonen? Dat lijkt mij onzin
    # Wel zorgen dat dit op de achtergrond ligt.

    x1 = list(files[0].df["date"].map(to_bokeh_timestamp).values)
    x2 = list(files[1].df["date"].map(to_bokeh_timestamp).values)
    # x2 = list(files[1].df["date"].map(to_bokeh_timestamp).values)[::-1]

    y1 = list(files[0].df["val"].values)
    y2 = list(files[1].df["val"].values)
    # y2 = list(files[1].df["val"].values)[::-1]

    check_same_length()
    check_same_values()
    clip_series()
    add_dummy_interpolation()

    xs = x1 + x2
    ys = y1 + y2

    p.patches([xs], [ys], alpha=0.3)
    return p


def create_matplot(files):
    fig = plt.figure()

    colors = ["blue", "red", "green"]
    sizes = [3, 2, 1]

    for file_, color, sz in zip(files, colors, sizes):
        logger.info("%s %s %s", file_.fname, color, sz)
        if file_.plot_type == "line":
            plt.plot(file_.df["date"], file_.df["val"], color=color, lw=sz)
        elif file_.plot_type == "point":
            plt.plot(file_.df["date"], file_.df["val"], color=color, ms=sz,
                     marker="o")
    # fig.xfmtautodate()
    return fig


def check_filetype_and_data(fpana):
    if fpana.endswith(".csv"):
        file_ = CsvFile(fpana, sep=";")
        file_.get_data()

    elif fpana.endswith(".nc"):
        loc = "MA_210.00"
        param = "water_level"
        file_ = NetCDFFile(fpana)
        file_.get_data(param)
        file_.get_timeseries(loc)
        # logger.info(file_.loc_var_map[loc])
        logger.info(file_.var_loc_map[param])

    elif fpana.endswith(".xml"):
        loc = "Maasmond"
        param = "H"
        file_ = XmlFile(fpana)
        file_.get_data(param, loc)
        # logger.info(file_.loc_var_map[loc])
        # logger.info(file_.var_loc_map[param])
    return file_


if __name__ == "__main__":
    # input parameters
    fpath_root = os.path.abspath(os.path.dirname(__file__))
    fpath_data = os.path.join(fpath_root, "data")
    # fpath_data = r"d:\RWsOS\RMM\Documenten\SobekRestart\dimr_ndb\dflow1d\output"
    # fname = "observations.nc"

    fname = "test.nc"
    # initialize
    fpana = os.path.join(fpath_data, fname)
    files = [fpana]

    Files_list = []
    for fname_path in files:
        file_name = os.path.basename(fname_path)
        Files_list.append(check_filetype_and_data(fname_path))

    output_file("Visualize_test.html")
    p = create_plot(Files_list)
    show(p)
