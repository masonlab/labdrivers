import pytest

from labdrivers.oxford import triton200

def test_temperature_channel():
    fridge = triton200("""ip_address""")
    assert fridge.temperature_channel != 5
    assert fridge.temperature_channel == '5'
    fridge.temperature_channel = 6
    assert fridge.temperature_channel != 6
    assert fridge.temperature_channel == '6'


def test_temperature_setpoint():
    fridge