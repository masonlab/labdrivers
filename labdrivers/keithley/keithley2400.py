"""
Author: pbnjeff89 (Jeff Damasco)
Version: 2.0

- More control over individual components
- No more glitches/annoyances with -420 errors due to unterminated queries
- No more use of pandas

Some of this class structure was inspired by large chunks of code from
Henry's old class. I chose to move in a slightly different direction
because the old class was very restrictive in its use and also gave
errors whenever the Sourcemeter was used for gating.

Here, this version adds in the trace/buffer commands individually but will
also give a limited implementation of sweeps so that the user does not
have to remember all of the code in the API.
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

    def __enter__(self):
        '''Opens handle for Keithley 2400 Sourcemeter.'''
        self._instrument = self._resource_manager.open_resource("GPIB::{}".format(self.gpib_addr))

    def __exit__(self):
        '''Closes handle for Keithley 2400 Sourcemeter.'''
        self._instrument.close()

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
        return SOURCE_TYPE[response]

    @source_type.setter
    def source_type(self, value):
        if value.lower() == 'voltage' or value.lower() == 'v':
            source = 'voltage'
            self._instrument.write("source:function:mode {}".format(source.lower()))
        elif value.lower() == 'current' or value.lower() == 'i':
            source = 'current'
            self._instrument.write('source:function:mode {}'.format(source.lower()))
        else:
            raise RuntimeError('Not a valid source type.')

    @property
    def source_mode(self):
        """Mode of the source: [fixed | sweep | list]"""
        # TODO: test
        return self._instrument.query('source:' + self.source_type.lower() + ':mode?')

    @source_mode.setter
    def source_mode(self, mode):
        if mode.lower() in ('fixed', 'sweep', 'list'):
            self._instrument.write('source:' + self.source_type.lower() + ':mode {}'.format(mode))
        else:
            raise RuntimeError('Mode is not one of [fixed | sweep | list]')

    @property
    def source_value(self):
        """Numeric value of the source chosen from keithley.source_type."""
        # TODO: test
        return self._instrument.query('source:' + self.source_type.lower() + ':level?')

    @source_value.setter
    def source_value(self, value):
        self._instrument.write("source:function:mode " + self.source_type.lower())
        self._instrument.write("source:" + self.source_type.lower() + ":range " + str(value))
        self._instrument.write("source:" + self.source_type.lower() + ":level " + str(value))

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
        response = self._instrument.query('sense:resistance:mode?').strip()
        return MODES[response]

    @resistance_ohms_mode.setter
    def resistance_ohms_mode(self, value):
        MODES = {'manual': 'MAN', 'auto': 'AUTO'}
        if value.lower() in MODES.keys():
            self._instrument.write('sense:resistance:mode {}'.format(MODES[value.lower()]))
        else:
            raise RuntimeError('Expected a value from [\'manual\'|\'auto\']')

    @property
    def expected_ohms_reading(self):
        response = self._instrument.query('sense:resistance:range?').strip()
        return float(response)

    @expected_ohms_reading.setter
    def expected_ohms_reading(self, value):
        if isinstance(value, int) or isinstance(value, float):
            self._instrument.write('sense:resistance:range {}'.format(value))
        else:
            raise RuntimeError('Expected an int or float.')

    @property
    def four_wire_sensing(self):
        response = self._instrument.query('system:rsense?').strip()
        return bool(int(response))

    @four_wire_sensing.setter
    def four_wire_sensing(self, value):
        if isinstance(value, bool):
            self._instrument.write('system:rsense {}'.format(int(value)))
        else:
            raise RuntimeError('Expected boolean value.')

    # Voltage sensing and compliance

    @property
    def expected_voltage_reading(self):
        response = self._instrument.query('sense:voltage:RANGE?').strip()
        return float(response)

    @expected_voltage_reading.setter
    def expected_voltage_reading(self, value):
        if isinstance(value, int) or isinstance(value, float):
            self._instrument.write('sense:voltage:range {}'.format(value))
        else:
            raise RuntimeError('Expected an int or float.')

    @property
    def voltage_compliance(self):
        response = self._instrument.query("SENS:VOLT:PROT:LEV?").strip()
        return float(response)

    @voltage_compliance.setter
    def voltage_compliance(self, value):
        if 200e-6 <= value <= 210:
            self._instrument.write("SENS:VOLT:PROT {}".format(str(value)))
        else:
            raise RuntimeError('Voltage compliance cannot be set. Value must be between 200 \u03BC' + 'V and 210 V.')

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
        if isinstance(value, int) or isinstance(value, float):
            self._instrument.write('sense:current:range {}'.format(value))
        else:
            RuntimeError('Expected an int or float.')

    @property
    def current_compliance(self):
        response = self._instrument.query("SENS:CURR:PROT:LEV?").strip()
        return float(response)

    @current_compliance.setter
    def current_compliance(self, value):
        if 1e-9 <= value <= 1.05:
            self._instrument.write("SENS:CURR:PROT {}".format(str(value)))
        else:
            raise RuntimeError('Current compliance cannot be set. Value must be between 1 nA and 1.05 A.')

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
        if value:
            self._instrument.write("OUTP ON")
        else:
            self._instrument.write("OUTP OFF")

    @property
    def output_off_mode(self):
        MODES = {'HIMP': 'high impedance', 'NORM': 'normal', 'ZERO': 'zero', 'GUAR': 'guard'}
        response = self._instrument.query('OUTP:SMOD?').strip()
        return MODES[response]

    @output_off_mode.setter
    def output_off_mode(self, value):
        MODES = {'high impedance': 'HIMP', 'himp': 'HIMP', 'normal': 'NORM', 'norm': 'NORM',
                 'zero': 'ZERO', '0': 'ZERO', 'guard': 'GUARD'}
        self._instrument.write('OUTP:SMOD {}'.format(MODES[value.lower()]))

    # Data acquisition

    def read(self):
        response = self._instrument.query('read?').strip()
        return float(response)

    # Trigger functions

    @property
    def trace_delay(self):
        """The amount of time the SourceMeter waits after the trigger to perform Device Action."""
        return float(self._instrument.query('trigger:delay?').strip())

    @trace_delay.setter
    def trace_delay(self, delay):
        if isinstance(delay, float) or isinstance(delay, int):
            if 0.0 <= delay <= 999.9999:
                self._instrument.write('trigger:delay {}'.format(delay))
            else:
                raise RuntimeError('Expected delay to be between 0.0 and 999.9999 seconds.')
        else:
            raise RuntimeError('Expected delay to be an int or float.')

    @property
    def trigger(self):
        TRIGGERS =  {   'IMM': 'immediate',         'TLIN': 'trigger link',         'TIM': 'timer',
                        'MAN': 'manual',            'BUS': 'bus trigger',           'NST': 'low SOT pulse',
                        'PST': 'high SOT pulse',    'BST': 'high or low SOT pulse'
                    }
        return TRIGGERS[self._instrument.query('trigger:source?')]

    @trigger.setter
    def trigger(self, trigger):
        TRIGGERS = {
            'imm': 'IMM', 'immediate': 'IMM',
            'tlin': 'TLIN', 'tlink': 'TLIN', 'trigger link': 'TLIN',
            'tim': 'TIM', 'timer': 'TIM',
            'man': 'MAN', 'manual': 'MAN',
            'bus': 'BUS', 'bus trigger': 'BUS',
            'nst': 'NST', 'low SOT pulse': 'NST',
            'pst': 'PST', 'high SOT pulse': 'PST',
            'bst': 'BST', 'high or low SOT pulse': 'BST'
        }
        if trigger.lower() in TRIGGERS.keys():
            self._instrument.query('trigger:source {}'.format(trigger))
        else:
            raise RuntimeError('Unexpected trigger input. See documentation for details.')

    @property
    def trigger_count(self):
        """Number of triggers.

        Expected value: Between 1 and 2500."""
        return float(self._instrument.query('trigger:count?').strip())

    @trigger_count.setter
    def trigger_count(self, num_triggers):
        if isinstance(num_triggers, int):
            if 1 <= num_triggers <= 2500:
                self._instrument.write('trigger:count {}'.format(num_triggers))
            else:
                raise RuntimeError('Trigger count expected to be between 1 and 2500.')
        else:
            raise RuntimeError('Trigger count expected to be type int.')

    def initiate_cycle(self):
        """Initiates source or measure cycle, taking the SourceMeter out of an idle state."""
        self._instrument.write('initiate')

    def abort_cycle(self):
        """Aborts the source or measure cycle, bringing the SourceMeter back into an idle state."""
        self._instrument.write('abort')

    # Data storage / Buffer functions

    # Note: :trace:data? and :read? are two separate buffers of
    # maximum size 2500 readings.
    
    @property
    def num_readings_in_buffer(self):
        """The number of readings stored in buffer."""
        return int(self._instrument.query('trace:points:actual?').strip())

    @property
    def trace_points(self):
        """Buffer size.
        
        Expected value: 1 <= n <= 2500."""
        return int(self._instrument.query('trace:points?').strip())

    @trace_points.setter
    def trace_points(self, num_points):
        if isinstance(num_points, int):
            if 1 <= num_points <= 2500:
                self._instrument.write('trace:points {}'.format(num_points))
            else:
                raise RuntimeError('Keithley 2400 SourceMeter may only have 1 to 2500 buffer points.')
        else:
            raise RuntimeError('Expected type of num_points: int.')

    def trace_feed_source(self, value):
        """Source of readings.

        Expected values: sense, calculate1, calculate2."""
        if value in ('sense', 'calculate1', 'calculate2'):
            self._instrument.write('trace:feed {}'.format(value))
        else:
            raise RuntimeError('Unexpected trace source type. See documentation for details.')

    def read_trace(self):
        """Read contents of buffer."""
        trace = self._instrument.query('trace:data?').strip().split(',')
        trace = [float(x) for x in trace]

    def clear_trace(self):
        """Clear buffer."""
        self._instrument.query('trace:clear')

    def buffer_memory_status(self):
        """Check buffer memory status."""
        response = self._instrument.query('trace:free?')

    def fill_buffer(self):
        """Fill buffer and stop."""
        self._instrument.write('trace:feed:control next')

    def disable_buffer(self):
        """Disable buffer."""
        self._instrument.write('trace:feed:control never')

    # Sweeeping

    # TODO: implement these!!!

    @property
    def sweep_start(self):
        pass

    @sweep_start.setter
    def sweep_start(self, start):
        pass

    @property
    def sweep_end(self):
        pass

    @sweep_end.setter
    def sweep_end(self, end):
        pass

    @property
    def sweep_center(self):
        pass

    @sweep_center.setter
    def sweep_center(self, center):
        pass

    @property
    def sweep_span(self):
        pass

    @sweep_span.setter
    def sweep_span(self, span):
        pass

    @property
    def sweep_ranging(self):
        pass

    @sweep_ranging.setter
    def sweep_ranging(self, _range):
        pass

    @property
    def sweep_scale(self):
        pass

    @sweep_scale.setter
    def sweep_scale(self, scale):
        pass

    @property
    def sweep_points(self):
        pass

    @sweep_points.setter
    def sweep_points(self, num_points):
        pass

    @property
    def sweep_direction(self):
        pass

    @sweep_direction.setter
    def sweep_direction(self, direction):
        pass

    # Pre-made commands

    # TODO: make stuff

    # Common commands

    def clear_status(self):
        """Clears all event registers and Error Queue."""
        self._instrument.write('*cls')

    def reset_to_defaults(self):
        """Resets to defaults of Sourcemeter."""
        self._instrument.write('*rst')

    def identify(self):
        """Returns manufacturer, model number, serial number, and firmware revision levels."""
        response = self._instrument.write('*idn?')
        return  {   'manufacturer': response[0],
                    'model': response[1],
                    'serial number': response[2],
                    'firmware revision level': response[3]
                }

    def send_bus_trigger(self):
        """Sends bus trigger to SourceMeter."""
        self._instrument.write('*trg')


    
