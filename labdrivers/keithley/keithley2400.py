from statistics import mean, stdev

import visa


class Keithley2400:

    def __init__(self, gpib_addr=23):
        """
        Constructor for Keithley 2400 Sourcemeter

        :param gpib_addr: GPIB address (configured on Keithley 2400)
        """
        self._gpib_addr = str(gpib_addr)
        self._resource_manager = visa.ResourceManager()
        self._instrument = self._resource_manager.open_resource("GPIB::{}".format(self.gpib_addr))

    @property
    def gpib_addr(self):
        """Returns the GPIB address of the Keithley 2400 Sourcemeter."""
        return self._gpib_addr

    # source functions

    @property
    def source_type(self):
        """Gets or sets the source type of the Keithley 2400 SourceMeter.

        Expected strings for setting: 'voltage', 'current'"""
        response = self._instrument.query("source:function:mode?").strip()
        source_type = {'VOLT': 'voltage', 'CURR': 'current'}
        return source_type[response]

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
        """Gets or sets the mode of the source.

        Expected strings for setting: 'fixed', 'sweep', 'list'"""
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
        """Get or set the numeric value of the source chosen from Keithley2400.source_type."""
        # TODO: test
        return self._instrument.query('source:' + self.source_type.lower() + ':level?')

    @source_value.setter
    def source_value(self, value):
        self._instrument.write("source:function:mode " + self.source_type.lower())
        self._instrument.write("source:" + self.source_type.lower() + ":range " + str(value))
        self._instrument.write("source:" + self.source_type.lower() + ":level " + str(value))

    @property
    def measure_type(self):
        """The type of measurement the Keithley 2400 SourceMeter will make.

        Expected strings for setting: 'voltage', 'current', 'resistance'
        """
        measure_type = {'VOLT:DC': 'voltage', 'CURR:DC': 'current', 'RES': 'resistance'}
        measure_type_response = self._instrument.query("sense:function?").strip().replace('\"', '').split(',')[-1]
        return measure_type[measure_type_response]

    @measure_type.setter
    def measure_type(self, value):
        measure_type = {'voltage': '\'VOLTAGE:DC\'', 'current': '\'CURRENT:DC\'', 'resistance': 'RESISTANCE'}
        if value.lower() in measure_type:
            self._instrument.write("sense:function:ON {}".format(measure_type[value.lower()]))
        else:
            raise RuntimeError('Expected a value from [\'voltage\'|\'current\'|\'resistance\'')

    # Resistance sensing

    @property
    def resistance_ohms_mode(self):
        """Gets or sets the resistance mode.

        Expected strings for setting: 'manual', 'auto'"""
        modes = {'MAN': 'manual', 'AUTO': 'auto'}
        response = self._instrument.query('sense:resistance:mode?').strip()
        return modes[response]

    @resistance_ohms_mode.setter
    def resistance_ohms_mode(self, value):
        modes = {'manual': 'MAN', 'auto': 'AUTO'}
        if value.lower() in modes.keys():
            self._instrument.write('sense:resistance:mode {}'.format(modes[value.lower()]))
        else:
            raise RuntimeError('Expected a value from [\'manual\'|\'auto\']')

    @property
    def expected_ohms_reading(self):
        """Gets or sets the expected range of a resistance reading from the device under test."""
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
        """Gets the status of or sets four-wire sensing.

        Expected booleans for setting: True, False."""
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
        """Gets or sets the expected voltage reading from the device under test."""
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
        """Gets or sets the voltage compliance.

        Expected range of floats: 200e-6 <= x <= 210"""
        response = self._instrument.query("SENS:VOLT:PROT:LEV?").strip()
        return float(response)

    @voltage_compliance.setter
    def voltage_compliance(self, value):
        if 200e-6 <= value <= 210:
            self._instrument.write("SENS:VOLT:PROT {}".format(str(value)))
        else:
            raise RuntimeError('Voltage compliance cannot be set. Value must be between 200 \u03BC' + 'V and 210 V.')

    def within_voltage_compliance(self):
        """Queries if the measured voltage is within the set compliance.

        :returns: boolean"""
        response = self._instrument.query('SENS:VOLT:PROT:TRIP?').strip()
        return not bool(int(response))

    # Current sensing and compilance

    @property
    def expected_current_reading(self):
        """Gets or sets the expected current reading from the device under test."""
        response = self._instrument.query('sense:current:range?').strip()
        return float(response)

    @expected_current_reading.setter
    def expected_current_reading(self, value):
        if isinstance(value, int) or isinstance(value, float):
            self._instrument.write('sense:current:range {}'.format(value))
        else:
            RuntimeError('Expected an int or float.')

    @property
    def current_compliance(self):
        """Sets or gets the current compliance level in Amperes."""
        response = self._instrument.query("SENS:CURR:PROT:LEV?").strip()
        return float(response)

    @current_compliance.setter
    def current_compliance(self, value):
        if 1e-9 <= value <= 1.05:
            self._instrument.write("SENS:CURR:PROT {}".format(str(value)))
        else:
            raise RuntimeError('Current compliance cannot be set. Value must be between 1 nA and 1.05 A.')

    def within_current_compliance(self):
        """Queries if the measured current is within the set compliance.

        :returns: boolean"""
        response = self._instrument.query('SENS:CURR:PROT:TRIP?').strip()
        return not bool(int(response))

    # Output configuration

    @property
    def output(self):
        """Gets or sets the source output of the Keithley 2400.

        Expected input: boolean

        :returns: boolean"""
        output = {'0': False, '1': True}
        response = self._instrument.query("OUTP?").strip()
        return output[response]

    @output.setter
    def output(self, value):
        if value:
            self._instrument.write("OUTP ON")
        else:
            self._instrument.write("OUTP OFF")

    @property
    def output_off_mode(self):
        """Gets or sets the output mode when the output is off.

        Expected input strings: 'himp', 'normal', 'zero', 'guard'

        :returns: description of the output's off mode"""
        modes = {'HIMP': 'high impedance', 'NORM': 'normal', 'ZERO': 'zero', 'GUAR': 'guard'}
        response = self._instrument.query('OUTP:SMOD?').strip()
        return modes[response]

    @output_off_mode.setter
    def output_off_mode(self, value):
        modes = {'high impedance': 'HIMP', 'himp': 'HIMP', 'normal': 'NORM', 'norm': 'NORM',
                 'zero': 'ZERO', '0': 'ZERO', 'guard': 'GUARD'}
        self._instrument.write('OUTP:SMOD {}'.format(modes[value.lower()]))

    # Data acquisition

    def read(self, *measurements):
        """
        
        Reads data from the Keithley 2400. Equivalent to the command :INIT; :FETCH?

        Multiple string arguments may be used. For example::
            
            keithley.read('voltage', 'current')
            keithley.read('time')

        The first line returns a list in the form [voltage, current] and the second line
        returns a list in the form [time].

        Note: The returned lists contains the values in the order that you requested.

        :param str *measurements: Any number of arguments that are from: 'voltage', 'current', 'resistance', 'time'
        :return list measure_list: A list of the arithmetic means in the order of the given arguments
        :return list measure_stdev_list: A list of the standard deviations (if more than 1 measurement) in the order
            of the given arguments
        """
        response = self._instrument.query('read?').strip().split(',')
        response = [float(x) for x in response]
        read_types = {'voltage': 0, 'current': 1, 'resistance': 2, 'time': 3}

        measure_list = []
        measure_stdev_list = []

        for measurement in measurements:
            samples = response[read_types[measurement]::5]
            measure_list.append(mean(samples))
            if len(samples) > 1:
                measure_stdev_list.append(stdev(samples))

        return measure_list, measure_stdev_list

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
        """Gets or sets the type of trigger to be used.

        Expected strings for setting: 'immediate', 'tlink', 'timer', 'manual', 'bus',
        'nst', 'pst', 'bst' (see source code for other possibilities)"""
        triggers = {'IMM': 'immediate',         'TLIN': 'trigger link',         'TIM': 'timer',
                    'MAN': 'manual',            'BUS': 'bus trigger',           'NST': 'low SOT pulse',
                    'PST': 'high SOT pulse',    'BST': 'high or low SOT pulse'}
        return triggers[self._instrument.query('trigger:source?')]

    @trigger.setter
    def trigger(self, trigger):
        triggers = {
            'imm': 'IMM', 'immediate': 'IMM',
            'tlin': 'TLIN', 'tlink': 'TLIN', 'trigger link': 'TLIN',
            'tim': 'TIM', 'timer': 'TIM',
            'man': 'MAN', 'manual': 'MAN',
            'bus': 'BUS', 'bus trigger': 'BUS',
            'nst': 'NST', 'low SOT pulse': 'NST',
            'pst': 'PST', 'high SOT pulse': 'PST',
            'bst': 'BST', 'high or low SOT pulse': 'BST'
        }
        if trigger.lower() in triggers.keys():
            self._instrument.query('trigger:source {}'.format(trigger))
        else:
            raise RuntimeError('Unexpected trigger input. See documentation for details.')

    @property
    def trigger_count(self):
        """Gets or sets the number of triggers

        Expected integer value range: 1 <= n <= 2500"""
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
        """Gets the number of readings that are stored in the buffer."""
        return int(self._instrument.query('trace:points:actual?').strip())

    @property
    def trace_points(self):
        """Gets or sets the size of the buffer
        
        Expected integer value range: 1 <= n <= 2500"""
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
        """Sets the source of the trace feed.

        Expected strings: 'sense', 'calculate1', 'calculate2'"""
        if value in ('sense', 'calculate1', 'calculate2'):
            self._instrument.write('trace:feed {}'.format(value))
        else:
            raise RuntimeError('Unexpected trace source type. See documentation for details.')

    def read_trace(self):
        """Read contents of buffer."""
        trace = self._instrument.query('trace:data?').strip().split(',')
        trace_list = [float(x) for x in trace]
        return trace_list

    def clear_trace(self):
        """Clear the buffer."""
        self._instrument.query('trace:clear')

    def buffer_memory_status(self):
        """Check buffer memory status."""
        response = self._instrument.query('trace:free?')
        return response

    def fill_buffer(self):
        """Fill buffer and stop."""
        self._instrument.write('trace:feed:control next')

    def disable_buffer(self):
        """Disables the buffer."""
        self._instrument.write('trace:feed:control never')

    # Sweeping

    # TODO: implement these!!!

    @property
    def sweep_start(self):
        """To be implemented."""
        pass

    @sweep_start.setter
    def sweep_start(self, start):
        pass

    @property
    def sweep_end(self):
        """To be implemented."""
        pass

    @sweep_end.setter
    def sweep_end(self, end):
        pass

    @property
    def sweep_center(self):
        """To be implemented."""
        pass

    @sweep_center.setter
    def sweep_center(self, center):
        pass

    @property
    def sweep_span(self):
        """To be implemented."""
        pass

    @sweep_span.setter
    def sweep_span(self, span):
        pass

    @property
    def sweep_ranging(self):
        """To be implemented."""
        pass

    @sweep_ranging.setter
    def sweep_ranging(self, _range):
        pass

    @property
    def sweep_scale(self):
        """To be implemented."""
        pass

    @sweep_scale.setter
    def sweep_scale(self, scale):
        pass

    @property
    def sweep_points(self):
        """To be implemented."""
        pass

    @sweep_points.setter
    def sweep_points(self, num_points):
        pass

    @property
    def sweep_direction(self):
        """To be implemented."""
        pass

    @sweep_direction.setter
    def sweep_direction(self, direction):
        pass

    # Ramping commands

    def ramp_to_zero(self):
        pass

    def ramp_to_setpoint(self, setpoint: float, step: float, wait: float):
        pass

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
        return {'manufacturer': response[0],
                'model': response[1],
                'serial number': response[2],
                'firmware revision level': response[3]
                }

    def send_bus_trigger(self):
        """Sends a bus trigger to SourceMeter."""
        self._instrument.write('*trg')
