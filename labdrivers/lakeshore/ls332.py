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
import visa

    
class Ls332:

    CHANNELS = ('A', 'B')

    def __init__(self, gpib_addr = 12):
        self.resource_manager = visa.ResourceManager()
        self._visa_resource = self.resource_manager.open_resource("GPIB::%d" % gpib_addr)
        self.channel = None

    @property
    def channel(self):
        """Gets or sets the current channel of the LS332.

        Setting expects the strings: 'A', 'B'

        :returns: The channel 'A' or 'B'"""
        return self.channel

    @channel.setter
    def channel(self, channel):
        input_value = channel.upper()

        if input_value in Ls332.CHANNELS:
            self.channel = input_value
        else:
            raise RuntimeError('Invalid channel')

    def reset(self):
        """Resets device to power-up settings."""
        self._visa_resource.write("*RST")

    @property
    def temperature(self):
        """Reads the temperature of the currently-set channel."""
        return self._visa_resource.query_ascii_values("KRDG? {}".format(self.channel))

    @property
    def temperature_setpoint(self):
        """Reads the temperature set point of the currently-set channel."""
        return self._visa_resource.query_ascii_values("SETP? {}".format(self.channel))
