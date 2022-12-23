#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 20 10:59:47 2022

@author: mihzou
"""

from datetime import datetime, timedelta

import sys
sys.path.append('./cwb_opendata/')
import cwb_opendata

#################### Download data from CWB Open Data Bank (XML)
out_list = cwb_opendata.download(
    outpath="./cwb_opendata_radar/xml",
    remove_exist=True,
    authorization="CWB-XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX",
    limit=None,
    offset=0,
    timeFrom=(datetime.now()-timedelta(seconds=3600*1)).strftime("%Y-%m-%d %H:%M:%S"),
    timeTo=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

#################### Convert XML to CWB radar binary file
# create array
convert_out = []
for fn1 in out_list:
    # xml2compref will return file path, save to temporary variable
    tmp = cwb_opendata.xml2compref(
        filename_in=fn1,
        filename_out='.'.join(fn1.split('/')[-1].split('.')[:-1]),
        outpath='./cwb_opendata_radar/compref',
        gzipped=True)
    
    convert_out.append(tmp) # append to array

#################### Display CWB radar binary file head info
metadata = cwb_opendata.dump_compref(filename=convert_out[-1], gzipped=True)

# display metadata, also can use "print(metadata)"
for keys, value in metadata.items():
    print('{:9s} : {}'.format(keys, value))

#################### Plot CWB radar binary file
fig_name = cwb_opendata.plot_compref(
    filename=convert_out[-1], gzipped=True, dpi=96, figsize=[49.67,49.67],
    savefig=False, outpath='./cwb_opendata_radar/figure'
    )
print(fig_name)

import importlib
importlib.reload(cwb_opendata)
cwb_opendata.plot_compref('/work1/mihzou/maple/COMPREF/2d/2021/COMPREF.20211127.1420.gz',dpi=72, figsize=[6,6])
