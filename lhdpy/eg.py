import numpy as np
from collections import OrderedDict
from copy import deepcopy
from datetime import datetime
from six import string_types
import xarray as xr


_ILLEGAL_CHAR_LIST_ = {
    '/': '_over_',
}
def _replace_illegal_characters(s):
    for key, item in _ILLEGAL_CHAR_LIST_.items():
        s = s.replace(key, item)
    return s

def load_robust(filename, diag, shotnumber):
    # there are several diagnostics that do not follow the format exactly.
    # we need to overwrite them.
    overwrite_params = {}
    if diag == 'ha2':
        overwrite_params['ShotNo'] = shotnumber

    return load(filename, **overwrite_params)


def load(filename, **overwrite_params):
    """
    Load eg-file and returns as xarray.DataSet.

    To load the data from a file,

    >>>  array = eg.load(filename)

    First, we load [Parameters] and [comments] parts of the eg-file.
    Parameters are stored in xarray.DataArray.attrs as an OrderedDict.

    If **overwrite_params is explicitly passed, e.g.

    >>> eg.load(filanema, ShotNo=131000)

    we do not read the corresponding parameter from file but
    adapt the passed value.
    """
    parameters = {}
    comments = {}

    def set_param(name, value, functor=lambda x: x):
        """ Set a param to parameters from file header or overwrite_params """
        if name not in overwrite_params.keys():
            parameters[name] = functor(value)
        else:
            parameters[name] = overwrite_params[name]

    # load [Parameters] and [Comments] section
    try:
        if isinstance(filename, str):
            f = open(filename, 'rb')
        else:
            f = filename

        for line in f:
            line = line.decode("utf-8")
            if '[parameters]' in line.lower():
                block = 'Parameters'
            elif '[comments]' in line.lower():
                block = 'comments'
            elif '[data]' in line.lower():
                break # data is read np.loadtxt
            elif not '#' in line:
                break # Finish reading.
            # read Parameters block
            elif block == 'Parameters':
                # Make lower case
                key = line[line.find('#')+1:line.find("=")].strip()
                # remove '(quotation) and , (space)
                val = line[line.find('=')+1:].replace(" ","").replace("'", "").strip()
                # string
                if key.lower() == 'NAME'.lower():
                    set_param('diag', val)
                # list of string
                elif key.lower() == 'DimName'.lower():
                    set_param('DimName', val, lambda x: x.split(','))
                elif key.lower() == 'DimUnit'.lower():
                    set_param('DimUnit', val, lambda x: x.split(','))
                elif key.lower() == 'ValName'.lower():
                    set_param('ValName', val, lambda x: x.split(','))
                elif key.lower() == 'ValUnit'.lower():
                    set_param('ValUnit', val, lambda x: x.split(','))
                # string
                elif key.lower() == 'Date'.lower():
                    set_param('Date', val)
                # integers
                elif key.lower() == 'DimNo'.lower():
                    set_param('DimNo', val, int)
                elif key.lower() == 'ValNo'.lower():
                    set_param('ValNo', val, int)
                elif key.lower() == 'ShotNo'.lower():
                    set_param('ShotNo', val, int)
                elif key.lower() == 'SubShotNO'.lower():
                    set_param('SubShotNO', val, int)
                # list of integers
                elif key.lower() == 'DimSize'.lower():
                    set_param('DimSize', val, lambda x:
                                            [int(s) for s in x.split(',')])
                else: # the rest of parameters                # string
                    if key is not None and len(key)>0:
                        parameters[key] = line[line.find('=')+1:].strip()

            elif block == 'comments':
                if '=' in line:
                    # Make lower case
                    key = line[line.find('#')+1:line.find("=")].strip()
                    # remove '(quotation) and , (space)
                    val = line[line.find('=')+1:].replace(" ","").replace("'", "").strip()
                    if key is not None and len(key)>0:
                        comments[key] = line[line.find('=')+1:].strip()
                else:
                    key = 'comment'
                    if key not in comments:
                        comments[key] = '' 
                    comments[key] += line[line.find('#')+1:].replace(" ","").replace("'", "").strip()

        # Make sure some necessary parameters are certainly stored
        need_keys = ['diag', 'DimName', 'DimUnit', 'ValName', 'ValUnit', 'Date',
                     'DimNo', 'ValNo', 'ShotNo', 'DimSize']
        for need_key in need_keys:
            if need_key not in parameters.keys():
                raise ValueError('There is no '+ need_key + ' property in ' +
                                 filename)
        """
        Next, we load [Data] part of file.
        """
        # temporary data
        try:
            tmpdata = np.loadtxt(filename, comments='#', delimiter=',')
        except ValueError as e:
            cols = range(parameters['DimNo'] + parameters['ValNo'])
            tmpdata = np.loadtxt(filename, comments='#', delimiter=',',
                                 usecols=cols)
    except Exception as e:
        print(e)
    finally:
        if isinstance(filename, str):
            f.close()

    # Even if parameters['DimNo'] contradicts with the actual data size,
    # we estimate it.
    if parameters['DimNo'] == 1:
        if parameters['DimSize'][0] != tmpdata.shape[0]:
            parameters['DimSize'] = [tmpdata.shape[0], ]

    # The original array is stored in strange order (neither F nor C)
    # We need to swap the axis temporary, and restore them later.
    coord_index = list(range(1, parameters['DimNo'])) + [0]
    restore_index = [-1] + list(range(parameters['DimNo'] - 1))
    dimsizes = [parameters['DimSize'][i] for i in coord_index]
    dimnames = [parameters['DimName'][i] for i in coord_index]
    dimunits = [parameters['DimUnit'][i] for i in coord_index]

    # storing and reshape dims (dict)
    coords = {}
    # in order to keep coordinate order, we first define keys
    for dname in parameters['DimName']:
        coords[dname] = None

    for i, dname in enumerate(parameters['DimName']):
        axis = restore_index[i]
        d = tmpdata[:,i].reshape(dimsizes, order='F')
        inds = (slice(None), ) + (0, ) * (parameters['DimNo'] - 1)
        coords[dname] = \
            ((dname),
             np.swapaxes(d, 0, axis)[inds],
             {'units': parameters['DimUnit'][i]})

    # append scalar coordinate
    coords['ShotNo'] = parameters['ShotNo']

    # xr.DataSet that will be created by this method.
    result = {}
    for i, vname in enumerate(parameters['ValName']):
        vname = _replace_illegal_characters(vname)
        result[vname] = xr.DataArray(
                data=tmpdata[:,i+len(parameters['DimName'])].reshape(
                    dimsizes, order='F'),
                dims=dimnames,
                coords=coords,
                name=vname,
                attrs={'units': parameters['ValUnit'][i]})
        # here, we transpose the array back to the original order
        result[vname] = result[vname].transpose(*parameters['DimName'])

    attrs = {}
    for key, item in parameters.items():
        # remove unnecessary parameters (to avoid duplicity)
        if key not in ['DimName', 'DimNo', 'ValName', 'ValNo', 'DimSize',
                       'DimUnit', 'ValUnit', 'ShotNo']:
            attrs[key] = item
        
    attrs.update(comments)

    ds = xr.Dataset(result, coords=coords, attrs=attrs)
    return ds


def dump(dataset, filename, fmt='%.6e', NAME=None, ShotNo=None):
    """
    Save xarray.Dataset to file.

    parameters:
    - dataset: xarray.Dataset object.
        To make the file compatibile to eg file, the following information is
        necessary, ['NAME', 'ShotNo']
        To add these attributes to xarray.Dataset, call
        >>> dataset.attrs['NAME'] = 'some_name'
    - filename: path to file
    - fmt: format of the values. Same to np.savetxt. See
        https://docs.scipy.org/doc/numpy/reference/generated/numpy.savetxt.html
        for the detail.
    """
    obj = dataset.copy(deep=True)
    # Make sure some necessary parameters are certainly stored
    if NAME is None:
        if 'diag' not in obj.attrs.keys():
            raise ValueError('There is no '+ NAME + ' property in ' +
                             filename + '. Please provide NAME argument')
        else:
            NAME = obj.attrs['diag']
    obj.attrs['diag'] = '\'' + NAME + '\''

    if ShotNo is None:
        if 'ShotNo' in obj.attrs.keys():
            ShotNo = obj.attrs['ShotNo']
        elif 'ShotNo' in obj.coords:
            ShotNo = int(obj['ShotNo'].values)
        else:
            raise ValueError('There is no '+ ShotNo + ' property in ' + \
                            filename + '. Please provide ShotNo argument')

    obj.attrs['ShotNo'] = ShotNo

    dims = [key for key in obj.coords if key in obj.dims]
    dimsize = [len(obj.coords[key]) for key in dims]

    def add_primes(s):
        """ Attach primes if s is str or list or str"""
        if isinstance(s, list):
            line = add_primes(s[0])
            for s1 in s[1:]:
                line += ', ' + add_primes(s1)
            return line
        elif isinstance(s, string_types):
            return '\'' + s + '\''
        else:
            return str(s)

    # add some attributes
    obj.attrs['DimName'] = add_primes(dims)
    obj.attrs['DimNo']   = len(obj.dims)
    obj.attrs['DimUnit'] = add_primes([obj.coords[d].attrs['units']
                                       if 'units' in obj.coords[d].attrs.keys()
                                       else '' for d in dims])
    obj.attrs['DimSize'] = dimsize
    obj.attrs['ValName'] = add_primes([k for k in obj.data_vars.keys()])
    obj.attrs['ValNo']   = len(obj.data_vars.keys())
    obj.attrs['ValUnit'] = add_primes([c.attrs['units'] if 'units' in
                                       c.attrs.keys() else ''
                                       for key,c in obj.data_vars.items()])
    obj.attrs['Date']    = datetime.now().strftime('\'%m/%d/%Y %H:%M\'')

    # prepare the header
    # main parameters
    header = "[Parameters]\n"
    attrs = obj.attrs.copy()
    for key in ['diag', 'ShotNo', 'Date', 'DimNo', 'DimName', 'DimSize',
                'DimUnit', 'ValNo', 'ValName', 'ValUnit']:
        item = attrs.pop(key)
        if key == 'diag':
            key = 'NAME'
        if isinstance(item, list):
            header += key + " = " + add_primes(item) +"\n"
        else:
            header += key + " = " + str(item) +"\n"
        
    # other parameters
    header += "\n[comments]\n"
    for key, item in obj.attrs.items():
        header += key + " = " + str(item) +"\n"
    # data start
    header += "\n[data]"

    #---  prepare 2d data to write into file ---
    data = []
    # prepare coordinates.
    # Note that the order of eg-format is somehow strange, neither F- nor C-
    # order.
    coord_index = list(range(1, len(dims))) + [0]
    restore_index = [len(dims)] + list(range(len(dims) - 1))
    coord_data = []
    for i, key in enumerate(dims):
        # expand dims to match the data_vars shape
        coord = obj.coords[key]
        ind = (slice(None),) + (np.newaxis,) * (len(dims)-restore_index[i]-1)
        coord_data.append(coord.values[ind])

    if len(dims) == 1:
        data.append(coord_data[0])
    else:
        data = [arr.flatten(order='F') for arr in
                np.broadcast_arrays(*coord_data)]

    # append data_vars
    reordered_dims = [dims[i] for i in coord_index]
    for key, item in obj.data_vars.items():
        data.append(
            item.transpose(*reordered_dims).values.flatten(order='F'))

    # write to file
    np.savetxt(filename, np.stack(data, axis=0).transpose(), header=header,
               delimiter=', ', fmt=fmt)
