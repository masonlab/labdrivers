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
    resource_manager = visa.ResourceManager()
except OSError:
    logger.exception("\n\tCould not find the VISA library. Is the National Instruments VISA driver installed?\n\n")
    
class LS332():

    def __init__(self, GPIBaddr = 12):
        """Connect to Lake Shore Cryotronics 332.
        
        Args:
            GPIBaddr: GPIB address of LS332.
        """
        self._visa_resource = resource_manager.open_resource("GPIB::%d" % GPIBaddr)
        self.