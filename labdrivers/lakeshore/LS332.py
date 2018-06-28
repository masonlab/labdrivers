"""Module for controlling the Lake Shore Cryotronics 332.

This module requires a National Instruments VISA driver, which can be found at
https://www.ni.com/visa/.

Attributes:
    resource_manager: the pyvisa resource manager which provides the visa
                      objects used for communicating over the GPIB interface

    logger: a python logger object
    
Classes:
    LS332: A class for interfacing to the LS332 temperature controller.
"""
import logging

import visa
from pyvisa.errors import VisaIOError

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


try:
    # the pyvisa manager we'll use to connect to the GPIB resources
    resource_manager = visa.ResourceManager()
except OSError:
    logger.exception("\n\tCould not find the VISA library. Is the National Instruments VISA driver installed?\n\n")

    
class ls332():

    CHANNELS = ('A','B')

    def __init__(self, GPIBaddr = 12):
        """Connect to Lake Shore Cryotronics 332.
        
        Args:
            GPIBaddr: GPIB address of LS332.
        """
        self._visa_resource = resource_manager.open_resource("GPIB::%d" % GPIBaddr)
        self.channel = None


    @property
    def channel(self):
        return self.channel


    @channel.setter
    def channel(self, value):
        input_value = value.upper()

        try:
            if input_value in CHANNELS:
                self.channel = input_value
        except:
            raise RuntimeError('Invalid channel')

    
    def reset(self):
        """Resets device to power-up settings."""
        self._visa_resource.write("*RST")

    
    @property
    def temperature(self):
        return self._visa_resource.query_ascii_values("KRDG? {}".format(self.channel))


    @property
    def temperature_setpoint(self):
        return self._visa_resource.query_ascii_values("SETP? {}".format(self.channel))
