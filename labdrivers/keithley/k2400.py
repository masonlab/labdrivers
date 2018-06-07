"""
An alternate class definition for the Keithley 2400.

This is another module to use if you wish to use "attributes" to
run your program. It also does not use pandas to pull data and
(temporarily) does not use the TRACe functionality because the
utility of the Keithley 2400 (for the Mason Lab) is limited mainly
to gate voltages.
"""

import visa

try:
    # the pyvisa manager we'll use to connect to the GPIB resources
    resource_manager = visa.ResourceManager()
except OSError:
    logger.exception("\n\tCould not find the VISA library. Is the National Instruments VISA driver installed?\n\n")

class k2400():

    SOURCES = ('voltage','current')
    MEASUREMENTS = ('voltage','current','resistance')

    def __init__(self, GPIBaddr=23):

        self._visa_resource = resource_manager.open_resource('GPIB::{}'.format(GPIBaddr))
        self._visa_resource_write('*RST')


    @property
    def source_type(self):
        return self.source_type


    @source_type.setter
    def source_type(self, value):
        source_type = value.lower()
        if source in SOURCES:
            self.source_type = source_type
        else:
            raise RuntimeError('Not a valid source.')


    @property
    def source_value(self):
        return self.source_value


    @source_value.setter
    def source_value(self, value):
        self.source_value = value
        self._visa_resource.write("SOURCE:FUNCTION:MODE " + self.source_type.upper())
        self._visa_resource.write("SOURCE:" + self.source_type.upper() + ":MODE FIXED")
        self._visa_resource.write("SOURCE:" + self.source_type.upper() + ":RANGE " + str(value))
        self._visa_resource.write("SOURCE:" + self.source_type.upper() + ":LEVEL " + str(value))


    @property
    def measure_type(self):
        return self.measure_type


    @measure_type.setter
    def measure_type(self, value):
        measure_type = value.lower()
        if measure_type in MEASUREMENTS:
            self.measure_type = measure_type
        else:
            raise RuntimeError('Not a valid measurement type.')


    @property
    def voltage_compliance(self):
        return self.voltage_compliance

    
    @voltage_compliance.setter
    def voltage_compliance(self, limit):
        self.voltage_compliance = limit
        self._visa_resource.write("SENS:VOLT:PROT " + str(limit))


    @property
    def current_compliance(self):
        return self.current_compliance

    
    @current_compliance.setter
    def current_compliance(self, limit):
        self.current_compliance = limit
        self._visa_resource.write("SENS:CURR:PROT " + str(limit))


    @property
    def output(self):
        return self.output


    @output.setter
    def output(self, value):
        if output:
            self.output = True
            self._visa_resource.write("OUTPUT ON")
        else:
            self.output = False
            self._visa_resource.write("OUTPUT OFF")