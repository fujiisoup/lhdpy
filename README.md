# lhdpy

A small library to download LHD diagnostic data from LHD data archive 
https://www-lhd.nifs.ac.jp/pub/Repository_en.html

# install
`pip install git+https://www.github.com/fujiisoup/lhdpy`

# Requirements

`lhdpy` requires [`xarray`](https://docs.xarray.dev/en/stable/) 

To install `xarray`, ldo  
```bash
pip install xarray
```

# Example
```python
>>> import lhdpy
>>> lhdpy.download('ha2', 123456)
<xarray.Dataset>
Dimensions:        (Time: 1310)
Coordinates:
  * Time           (Time) float64 0.03 0.06 0.09 0.12 ... 39.21 39.24 39.27 39.3
    ShotNo         int64 123456
Data variables: (12/21)
    1-O(H)         (Time) float64 0.0 0.0 -0.0004 0.0 ... 0.0 -0.0013 -0.0004
    2-O(H)         (Time) float64 -0.0005 -0.0005 -0.0005 ... -0.0005 0.0008
    3-O(H)         (Time) float64 0.0005 0.0005 -0.0004 ... 0.0 0.0 0.0005
    4-O(H)         (Time) float64 0.0004 0.0004 0.0 0.0 0.0 ... 0.0 0.0 0.0 0.0
    5-O(H)         (Time) float64 0.0017 0.0008 0.0004 ... -0.0005 -0.0 0.0004
    6-O(H)         (Time) float64 0.0 0.0004 0.0 0.0 ... -0.0004 -0.0004 0.0 0.0
    ...             ...
    6-O(He)        (Time) float64 0.0005 0.0009 0.0005 ... 0.0005 0.0014 0.0005
    7-O(He)        (Time) float64 -0.0001 0.0003 0.0012 ... 0.0012 -0.0001
    8-O(He)        (Time) float64 -0.001 -0.001 0.0008 ... -0.001 -0.001 -0.0001
    9-O(He)        (Time) float64 -0.001 0.0003 -0.0006 ... -0.0006 -0.0001
    10-O(He)       (Time) float64 0.0003 -0.002 0.0003 ... -0.0002 -0.0011
    H_over_(H+He)  (Time) float64 0.0 0.0 0.0 0.0 0.0 ... 0.0 0.0 0.0 0.0 0.0
Attributes:
    diag:       ha2
    SubShotNO:  1
    Date:       12/05/201316:43
    comment:    H:656.3nm,He:587.6nm
```

# Note
Some data files do not follow the [eg file format](https://exp.lhd.nifs.ac.jp/opendata/LHD/file_format.html).
Such files cannot be read with `lhdpy` unless we add a customized reading function.
If you find any formats, please contact us.