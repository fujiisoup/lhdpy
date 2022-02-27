from .. import core, eg
import pytest

@pytest.mark.parametrize(('diag', 'shot'), [
    ('DivIis_tor', 123333),
    ('ha2', 123456),
])
def test_download(diag, shot):
    data = core.download(diag, shot)
    print(data)
    # check if data can be converted to netcdf
    data.to_netcdf('test.nc')
    # check if data can be converted to the eg file
    eg.dump(data, 'test.dat')