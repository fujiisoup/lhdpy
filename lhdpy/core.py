import numpy as np
from urllib import request
import xarray as xr
import os

from . import eg


def exists(diag, shotnumber):
    r"""Returns True if the diagnostic exists for a given shotnumber."""
    raise NotImplementedError


def diag_list(shotnumber):
    r"""Returns a list of diagnostics for a given shotnumber"""
    raise NotImplementedError


def download(diag, shotnumbers):
    r"""Downloads the diagnostic data from the LHD data archive site """
    if hasattr(shotnumbers, '__iter__'):
        return [download(diag, shot) for shot in shotnumbers]
    
    url = 'https://exp.lhd.nifs.ac.jp/opendata/LHD/webapi.fcgi?cmd=getfile&diag={}&shotno={}&subno=1'.format(
        diag, shotnumbers
    )
    filename = request.urlretrieve(url)[0]
    data = eg.load_robust(filename, diag, shotnumbers)
    return data

