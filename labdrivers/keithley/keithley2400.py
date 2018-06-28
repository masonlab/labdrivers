"""
An alternate class definition for the Keithley 2400.

This is another module to use if you wish to use "attributes" to
run your program. It also does not use pandas to pull data and
(temporarily) does not use the TRACe functionality because the
utility of the Keithley 2400 (for the Mason Lab) is limited mainly
to gate voltages.
"""

import visa

class keithley2400():

    def __init__(self, gpib_addr=23):
        '''
        Constructor for Keithley 2400 Sourcemeter

        :param gpib_addr: GPIB address (configured on Keithley 2400)
        '''
        self._gpib_addr = str(gpib_addr)
        
        try:
            self._resource_manager = visa.ResourceManager()
        except OSError:
            logger.exception("\n\tCould not find the VISA library. Is the National Instruments VISA driver installed?\n\n")

        self._instrument = None


    def enable_remote(self):
        '''Opens a handle for the Keithley 2400 Sourcemeter.'''
        self._instrument = self._resource_manager.open_resource("GPIB::{}".format(self.gpib_addr))


    def disable_remote(self):
        '''Closes the handle for the Keithley 2400 Sourcemeter.'''
        self._instrument.close()


    @property
    def gpib_addr(self):
        '''Returns the GPIB address of the Keithley 2400 Sourcemeter.'''
        return self._gpib_addr


    # source functions


    @property
    def source_type(self):
        response = self._instrument.query("source:function:mode?").strip()
        SOURCE_TYPE = {'VOLT': 'voltage', 'CURR': 'current'}
        return SOURCE_TYPE['response']


    @source_type.setter
    def source_type(self, value):
        if value.upper() in ("VOLTAGE","CURRENT"):
            self._instrument.write("source:function:mode {}".format(value.upper()))
        else:
            raise RuntimeError('Not a valid source type.')


    @property
    def source_value(self):
        return self.source_value


    @source_value.setter
    def source_value(self, value):
        self.source_value = value
        self._visa_resource.write("source:function:mode " + self.source_type.upper())
        self._visa_resource.write("source:" + self.source_type.upper() + ":mode FIXED")
        self._visa_resource.write("source:" + self.source_type.upper() + ":RANGE " + str(value))
        self._visa_resource.write("source:" + self.source_type.upper() + ":LEVEL " + str(value))


    @property
    def measure_type(self):
        MEASURE_TYPE = {'VOLT:DC': 'voltage', 'CURR:DC': 'current', 'RES': 'resistance'}
        measure_type_response = self._instrument.query("sense:function?").strip().replace('\"','').split(',')[-1]
        return MEASURE_TYPE[response]


    @measure_type.setter
    def measure_type(self, value):
        MEASURE_TYPE = {'voltage':'\'VOLTAGE:DC\'', 'current':'\'CURRENT:DC\'', 'resistance':'RESISTANCE'}
        if value.lower() in MEASURE_TYPE:
            self._instrument.write("sense:function:ON {}".format(MEASURE_TYPE[value.lower()]))
        else:
            raise RuntimeError('Expected a value from [\'voltage\'|\'current\'|\'resistance\'')


    # Resistance sensing


    @property
    def resistance_ohms_mode(self):
        MODES = {'MAN': 'manual', 'AUTO': 'auto'}
        response = self._instrument.query('SENS:RES:mode?').strip()
        return MODES[response]


    @resistance_ohms_mode.setter
    def resistance_ohms_mode(self, value):
        MODES = {'manual': 'MAN', 'auto': 'AUTO'}
        if value.lower() in MODES.keys():
            self._instrument.write('SENS:RES:mode {}'.format(MODES[value.lower()]))
        else:
            raise RuntimeError('Expected a value from [\'manual\'|\'auto\']')


    @property
    def expected_ohms_reading(self):
        response = self._instrument.query('sense:resistance:range?').strip()
        return float(response)


    @expected_ohms_reading.setter
    def expected_ohms_reading(self, value):
        if isInstance(value, int) or isInstance(value, float):
            self._instrument.write('sense:resistance:range {}'.format(value))
        else:
            RuntimeError('Expected an int or float.')


    # Voltage sensing and compliance
    

    @property
    def expected_voltage_reading(self):
        response = self._instrument.query('sense:voltage:RANGE?').strip()
        return float(response)


    @expected_voltage_reading.setter
    def expected_voltage_reading(self, value):
        if isInstance(value, int) or isInstance(value, float):
            self._instrument.write('sense:voltage:range {}'.format(value))
        else:
            RuntimeError('Expected an int or float.')


    @property
    def voltage_compliance(self):
        response = self._instrument.query("SENS:VOLT:PROT:LEV?").strip()
        return float(response)


    @voltage_compliance.setter
    def voltage_compliance(self, value):
        self._instrument.write("SENS:VOLT:PROT {}".format(str(value)))


    def within_voltage_compliance(self):
        response = self._instrument.query('SENS:VOLT:PROT:TRIP?').strip()
        return (not bool(int(response)))


    # Current sensing and compilance


    @property
    def expected_current_reading(self):
        response = self._instrument.query('sense:current:range?').strip()
        return float(response)


    @expected_current_reading.setter
    def expected_current_reading(self):
        if isInstance(value, int) or isInstance(value, float):
            self._instrument.write('sense:current:range {}'.format(value))
        else:
            RuntimeError('Expected an int or float.')


    @property
    def current_compliance(self):
        response = self._instrument.query("SENS:CURR:PROT:LEV?").strip()
        return float(response)


    @current_compliance.setter
    def current_compliance(self, value):
        self._instrument.write("SENS:CURR:PROT {}".format(str(value)))


    def within_current_compliance(self):
        response = self._instrument.query('SENS:CURR:PROT:TRIP?').strip()
        return (not bool(int(response)))


    # Output configuration


    @property
    def output(self):
        OUTPUT = {'0':'off', '1':'on'}
        response = self._instrument.query("OUTP?").strip()
        return OUTPUT[response]


    @output.setter
    def output(self, value):
        if output:
            self.output = True
            self._visa_resource.write("OUTP ON")
        else:
            self.output = False
            self._visa_resource.write("OUTP OFF")


    @property
    def output_off_mode(self):
        MODES = {'HIMP': 'high impedance', 'NORM': 'normal', 'ZERO': 'zero', 'GUAR': 'guard'}
        response = self._instrument.query('OUTP:SMOD?').strip()
        return MODES[response]


    @output_off_mode.setter
    def output_off_mode(self, value):
        MODES = {'high impedance': 'HIMP', 'himp': 'HIMP', 'normal': 'NORM', 'norm': 'NORM',
                 'zero': 'ZERO', '0': 'ZERO', 'guard': 'GUARD'}
        self._instrument.write('OUTP:SMOD {}'.format(MODES[value.lower()])


    # Trace functions

    
    def retrieve_trace(self):
        trace = self._instrument.query('trace:data?').strip().split(',')
        trace = [float(x) for x in trace]


    def clear_trace(self):
        self._instrument.query('trace:clear')
