"""Module containing a class to interface with an Oxford Instruments ITC 503.

This module requires a National Instruments VISA driver, which can be found at
https://www.ni.com/visa/

Attributes:
    resource_manager: the pyvisa resource manager which provides the visa
                      objects used for communicating over the GPIB interface

    logger: a python logger object


Classes:
    itc503: a class for interfacing with a ITC 503 temperature controller

"""
import datetime as dt
import time
import logging

import visa
from pyvisa.errors import VisaIOError

# create a logger object for this module
logger = logging.getLogger(__name__)
# added so that log messages show up in Jupyter notebooks
logger.addHandler(logging.StreamHandler())

try:
    # the pyvisa manager we'll use to connect to the GPIB resources
    resource_manager = visa.ResourceManager()
except OSError:
    logger.exception("\n\tCould not find the VISA library. Is the National Instruments VISA driver installed?\n\n")


class itc503():
    
    def __init__(self, GPIBaddr=24):
        """Connect to an ITC 503 S at the specified GPIB address

        Args:
            GPIBaddr(int): GPIB address of the ITC 503 
        """
        self._visa_resource = resource_manager.open_resource("GPIB::%d" % GPIBaddr)
        self._visa_resource.read_termination = '\r'


    def setControl(self, state=3):
        """Set the LOCAL / REMOTE control state of the ITC 503

        0 - Local & Locked (default state)
        1 - Remote & Locked
        2 - Local & Unlocked
        3 - Remote & Locked

        Args:
            state(int): the state in which to place the ITC 503
        """
        assert type(state) == int, 'argument must be integer'
        assert state in [0,1,2,3], 'argument must be one of [0,1,2,3]'

        self._visa_resource.write("$C{}".format(state))


    def readTemperature(self, sensor=1):
        """Read the current temperature
        
        Args:
            sensor(int): which sensor channel to read [1,2, or 3]

        Returns:
            temperature(float): current temperature
        """
        assert type(sensor) == int, 'argument must be integer'
        assert sensor in [1,2,3], 'argument must be one of [1,2,3]'
        
        self._visa_resource.write('R {}'.format(sensor))
        self._visa_resource.wait_for_srq()
        value_str = self._visa_resource.read()

        return float(value_str.strip('R+'))
