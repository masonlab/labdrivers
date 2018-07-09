import pytest

from labdrivers.srs.sr830 import sr830

LOCKIN_GPIB_ADDR = 8


def test_sync_filter():
    lock_in = sr830(LOCKIN_GPIB_ADDR)

    lock_in.sync_filter = True
    assert int(lock_in.sync_filter) == 1
    lock_in.sync_filter = False
    assert int(lock_in.sync_filter) == 0

    with pytest.raises(RuntimeError):
        lock_in.sync_filter = 'ham'


def test_low_pass_filter_slope():
    lock_in = sr830(LOCKIN_GPIB_ADDR)

    lock_in.low_pass_filter_slope = 6
    assert int(lock_in.low_pass_filter_slope) == 0
    lock_in.low_pass_filter_slope = 12
    assert int(lock_in.low_pass_filter_slope) == 1
    lock_in.low_pass_filter_slope = 18
    assert int(lock_in.low_pass_filter_slope) == 2
    lock_in.low_pass_filter_slope = 24
    assert int(lock_in.low_pass_filter_slope) == 3

    with pytest.raises(RuntimeError):
        lock_in.low_pass_filter_slope = 100


def test_reserve():
    lock_in = sr830(LOCKIN_GPIB_ADDR)

    lock_in.reserve = 'hi'
    assert int(lock_in.reserve) == 0
    lock_in.reserve = 'high'
    assert int(lock_in.reserve) == 0
    lock_in.reserve = 'high reserve'
    assert int(lock_in.reserve) == 0
    lock_in.reserve = 0
    assert int(lock_in.reserve) == 0

    lock_in.reserve = 'normal'
    assert int(lock_in.reserve) == 1
    lock_in.reserve = 1
    assert int(lock_in.reserve) == 1

    lock_in.reserve = 'lo'
    assert int(lock_in.reserve) == 2
    lock_in.reserve = 'low'
    assert int(lock_in.reserve) == 2
    lock_in.reserve = 'low noise'
    assert int(lock_in.reserve) == 2
    lock_in.reserve = 2
    assert int(lock_in.reserve) == 2

    with pytest.raises(RuntimeError):
        lock_in.reserve = 'eggs'


def test_frequency():
    lock_in = sr830(LOCKIN_GPIB_ADDR)

    lock_in.frequency = 23.33
    assert lock_in.frequency == 23.33

    with pytest.raises(RuntimeError):
        lock_in.frequency = -23.33


def test_input():
    lock_in = sr830(LOCKIN_GPIB_ADDR)

    lock_in.input = '0'
    assert lock_in.input == '0'
    lock_in.input = 0
    assert lock_in.input == '0'
    lock_in.input = 'a'
    assert lock_in.input == '0'
    lock_in.input = 'A'
    assert lock_in.input == '0'

    lock_in.input = '1'
    assert lock_in.input == '1'
    lock_in.input = 1
    assert lock_in.input == '1'
    lock_in.input = 'a-b'
    assert lock_in.input == '1'
    lock_in.input = 'A-b'
    assert lock_in.input == '1'
    lock_in.input = 'differential'
    assert lock_in.input == '1'

    lock_in.input = '2'
    assert lock_in.input == '2'
    lock_in.input = 2
    assert lock_in.input == '2'
    lock_in.input = 'i1'
    assert lock_in.input == '2'
    lock_in.input = 'i1m'
    assert lock_in.input == '2'
    lock_in.input = 'I1MOHM'
    assert lock_in.input == '2'

    lock_in.input = '3'
    assert lock_in.input == '3'
    lock_in.input = 3
    assert lock_in.input == '3'
    lock_in.input = 'i100'
    assert lock_in.input == '3'
    lock_in.input = 'i100m'
    assert lock_in.input == '3'
    lock_in.input = 'i100mohm'
    assert lock_in.input == '3'


def test_phase():
    lock_in = sr830(LOCKIN_GPIB_ADDR)

    with pytest.raises(RuntimeError):
        lock_in.phase = -720.0
    
    lock_in.phase = 128.0
    assert lock_in.phase == 128.0


def test_amplitude():
    lock_in = sr830(LOCKIN_GPIB_ADDR)

    with pytest.raises(RuntimeError):
        lock_in.amplitude = 5.002

    with pytest.raises(RuntimeError):
        lock_in.amplitude = 0.0

    lock_in.amplitude = 0.100
    assert lock_in.amplitude == 0.100