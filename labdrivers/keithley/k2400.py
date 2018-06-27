"""
An alternate class definition for the Keithley 2400.

This is another module to use if you wish to use "attributes" to
run your program. It also does not use pandas to pull data and
(temporarily) does not use the TRACe functionality because the
utility of the Keithley 2400 (for the Mason Lab) is limited mainly
to gate voltages.
"""

import visa

class k2400():

    def __init__(self, gpib_addr=23):

        self._gpib_addr = str(gpib_addr)
        
        try:
            self._resource_manager = visa.ResourceManager()
        except OSError:
            logger.exception("\n\tCould not find the VISA library. Is the National Instruments VISA driver installed?\n\n")

        self._instrument = None


    def enable_remote(self):
        self._instrument = self._resource_manager.open_resource("GPIB::{}".format(self.gpib_addr))


    def disable_remote(self):
        self._instrument.close()


    @property
    def gpib_addr(self):
        return self._gpib_addr


    @property
    def source_type(self):
        response = self._instrument.query("SOURCE:FUNCTION:MODE?").strip()
        SOURCE_TYPE = {'VOLT': 'voltage', 'CURR': 'current'}
        return SOURCE_TYPE['response']


    @source_type.setter
    def source_type(self, value):
        if value.upper in ("VOLTAGE","CURRENT"):
            self._instrument.write("SOURCE:FUNCTION:MODE {}".format(value.upper()))
        else:
            raise RuntimeError('Not a valid source type.')


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
        MEASURE_TYPE = {'VOLT:DC': 'voltage', 'CURR:DC': 'current', 'RES': 'resistance'}
        measure_type_response = self._instrument.query("SENSE:FUNCTION?").strip().replace('\"','').split(',')[-1]
        return MEASURE_TYPE[response]


    @measure_type.setter
    def measure_type(self, value):
        MEASURE_TYPE = {'voltage':'\'VOLTAGE:DC\'', 'current':'\'CURRENT:DC\'', 'resistance':'RESISTANCE'}
        if value.lower() in MEASURE_TYPE:
            self._instrument.write("SENSE:FUNCTION:ON {}".format(MEASURE_TYPE[value.lower()]))
        else:
            raise RuntimeError('Not a valid measurement type.')
    

    @property
    def voltage_compliance(self):
        response = self._instrument.query("SENS:VOLT:PROT:LEV?").strip()
        return float(response)


    @voltage_compliance.setter
    def voltage_compliance(self, value):
        self._instrument.write("SENS:VOLT:PROT {}".format(str(value)))


    @property
    def current_compliance(self):
        response = self._instrument.query("SENS:CURR:PROT:LEV?").strip()
        return float(response)

    @current_compliance.setter
    def current_compliance(self, value):
        self._instrument.write("SENS:CURR:PROT {}".format(str(value)))


    @property
    def output(self):
        OUTPUT = {'0':'off', '1':'on'}
        response = self._instrument.query("OUTPUT?").strip()
        return OUTPUT[response]


    @output.setter
    def output(self, value):
        if output:
            self.output = True
            self._visa_resource.write("OUTPUT ON")
        else:
            self.output = False
            self._visa_resource.write("OUTPUT OFF")
