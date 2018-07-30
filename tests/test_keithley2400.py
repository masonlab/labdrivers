import pytest

from labdrivers.keithley.keithley2400 import keithley2400

KEITHLEY_GPIB_ADDR = 23


def test_source_type():
    sourcemeter = keithley2400(KEITHLEY_GPIB_ADDR)
    sourcemeter.enable_remote()

    sourcemeter.source_type = 'voltage'
    assert sourcemeter.source_type == 'voltage'
    sourcemeter.source_type = 'current'
    assert sourcemeter.source_type == 'current'

    with pytest.raises(RuntimeError):
        sourcemeter.source_type = 'ham'


