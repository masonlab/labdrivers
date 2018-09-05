import socket


class Triton200:

    RUO2_CHANNEL = '5'
    CERNOX_CHANNEL = '6'

    VALID_CHANNELS = (CERNOX_CHANNEL, RUO2_CHANNEL)

    HEATER_RANGE = ['0.316', '1', '3.16', '10', '31.6', '100']

    def __init__(self, ip_address, port_number=33576, timeout=10000, bytes_to_read=2048):
        """
        Constructor for the Triton200 class.

        :param ip_address: The IP address of the Triton 200.
        :param port_number: The associated port number of the Triton 200.
        (default: 33576, as per the Triton 200 manual)
        :param timeout: How long to wait for a response. (default: 10000)
        :param bytes_to_read: How many bytes to accept from the response.
        (defualt: 2048)
        """
        self._address = (str(ip_address), int(port_number))
        self._timeout = timeout
        self._bytes_to_read = bytes_to_read
        self._temperature_channel = Triton200.RUO2_CHANNEL
        self._temperature_setpoint = 0.0
        self._heater_range = 0.0

        self._heater_channel = '1'
        self._turbo_channel = '1'

    @property
    def temperature_channel(self):
        """
        :return: The temperature channel, either the cernox (5) or the RuO2 (6)
        """
        return self._temperature_channel

    @temperature_channel.setter
    def temperature_channel(self, value):
        self._temperature_channel = str(value)

    @property
    def temperature_setpoint(self):
        return self._temperature_setpoint

    @temperature_setpoint.setter
    def temperature_setpoint(self, value):
        if not isinstance(value, float):
            raise RuntimeError("Make sure the temperature set point is a number.")
        elif 0 <= value < 10:
            self._temperature_setpoint = value
        else:
            print("Keep an eye on the turbo pump if you ramp!!!")
            self._temperature_setpoint = value

    @property
    def temperature(self):
        """
        :return: The temperature reading from the current temperature channel.
        """
        noun = 'DEV:T' + str(self.temperature_channel) + ':TEMP:SIG:TEMP'
        command = 'READ:' + noun + '\r\n'
        response = self.query_and_receive(command)

        return self.extract_value(response, noun, 'K')

    def update_heater(self):
        """
        Associates the heater with the current temperature channel and changes the heater current to
        preset values given the temperature set point.
        """
        command = 'SET:DEV:T' + str(self.temperature_channel) + ':TEMP:LOOP:HTR:H' + str(self._heater_channel) + '\r\n'
        response = self.query_and_receive(command)

        if not response:
            raise RuntimeError("Changing of heater focus unsuccessful.")

        heater_index = ((self.temperature_setpoint > 0.030)
                        + (self.temperature_setpoint > 0.050)
                        + (self.temperature_setpoint > 0.300)
                        + (self.temperature_setpoint > 1.000)
                        + (self.temperature_setpoint > 1.500))
        heater_current = Triton200.HEATER_RANGE[heater_index]

        command = 'SET:DEV:T' + str(self.temperature_channel) + ':TEMP:LOOP:RANGE:' + heater_current + '\r\n'
        response = self.query_and_receive(command)

        if not response:
            raise RuntimeError("Changing of heater range unsuccessful.")

    def controlled_ramp_on(self):
        """Starts a temperature sweep for the current temperature channel."""
        command = 'SET:DEV:T' + str(self.temperature_channel) + 'TEMP:LOOP:RAMP:ENAB:ON\r\n'
        response = self.query_and_receive(command)

        if not response:
            raise RuntimeError("Enabling of temperature ramp unsuccessful.")

    def controlled_ramp_off(self):
        """Stops a temperature sweep for the current temperature channel."""
        command = 'SET:DEV:T' + str(self.temperature_channel) + 'TEMP:LOOP:RAMP:ENAB:OFF\r\n'
        response = self.query_and_receive(command)

        if not response:
            raise RuntimeError("Disabling of temperature ramp unsuccessful.")

    def turbo_on(self):
        """Turns on a turbo pump.

        WARNING: Do not use this unless you know what you are doing."""
        command = 'SET:DEV:TURB' + self._turbo_channel + ':PUMP:SIG:STATE:ON\r\n'
        response = self.query_and_receive(command)

        if not response:
            raise RuntimeError("Enabling of turbo pump unsuccessful.")

    def turbo_off(self):
        """Turns off a turbo pump.

        WARNING: Do not use this unless you know what you are doing."""
        command = 'SET:DEV:TURB' + self._turbo_channel + ':PUMP:SIG:STATE:OFF\r\n'
        response = self.query_and_receive(command)

        if not response:
            raise RuntimeError("Disabling of turbo pump unsuccessful.")

    def query_and_receive(self, command):
        """
        Queries the Oxford Triton 200 with the given command.

        :param command: Specifies a read/write of a property.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(self._address)
            s.settimeout(self._timeout)
            s.sendall(command.encode())
            response = s.recv(self._bytes_to_read).decode()

        return response

    @staticmethod
    def extract_value(response, noun, unit):
        expected_response = 'STAT:' + noun + ':'
        value = float(response.replace(expected_response, '').strip('\n').replace(unit, ''))
        return value
