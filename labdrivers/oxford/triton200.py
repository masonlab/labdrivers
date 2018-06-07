import socket

class triton200():

    RUO2_CHANNEL = '5'
    CERNOX_CHANNEL = '6'

    VALID_CHANNELS = (CERNOX_CHANNEL, RUO2_CHANNEL)

    HEATER_RANGE = ['0.316', '1', '3.16', '10', '31.6', '100']

    def __init__(self, ip_address, port_number = 33756, timeout = 10000, bytes_to_read = 2048):
        """
        Constructor for the Triton200 class.

        :param ip_address: The IP address of the Triton 200.

        :param port_number: The associated port number of the Triton 200.
        (default: 33756, as per the Triton 200 manual)

        :param timeout: How long to wait for a response. (default: 10000)

        :param bytes_to_read: How many bytes to accept from the response.
        (defualt: 2048)
        """
        self._address = (str(ip_address), str(port_number))
        self._timeout = timeout
        self._bytes_to_read = bytes_to_read
        self._temperature_channel = triton200.RUO2_CHANNEL
        self._temperature_setpoint = 0.0
        self._heater_range = 0.0

        self._heater_channel = '1'
        self._turbo_channel = '1'


    @property
    def temperature_channel(self):
        return self._temperature_channel
    

    @channel.setter
    def temperature_channel(self, value):
        self._temperature_channel = str(value)


    @property
    def temperature_setpoint(self):
       return self._temperature_setpoint


    @temperature_setpoint.setter
    def temperature_setpoint(self, value):
        self._temperature_setpoint = value


    @property
    def temperature(self):
        noun = 'DEV:T' + str(self._temperature_channel) + ':TEMP:SIG:TEMP'
        command = 'READ:' + noun + '\r\n'
        response = self.query_and_receive(command)

        return self.extract_value(response, noun)


    def change_heater_focus(self):
        command = 'SET:DEV:T' + str(self._temperature_channel) + ':TEMP:LOOP:HTR:H' + str(self._heater_channel) + '\r\n'
        response = self.query_and_receive(command)


    def change_heater_range(self):
        heater_index = (  (self.temperature_setpoint > 0.030)
                        + (self.temperature_setpoint > 0.050)
                        + (self.temperature_setpoint > 0.300)
                        + (self.temperature_setpoint > 1.000)
                        + (self.temperature_setpoint > 1.500) )
        heater_current = triton200.HEATER_RANGE[heater_index]

        command = 'SET:DEV:T' + str(self._temperature_channel) + ':TEMP:LOOP:RANGE:' + heater_current + '\r\n'
        response = self.query_and_receive(command)


    def controlled_ramp_on(self):
        command = 'SET:DEV:T' + str(self._temperature_channel) + 'TEMP:LOOP:RAMP:ENAB:ON\r\n'
        response = self.query_and_receive(command)


    def controlled_ramp_off(self):
        command = 'SET:DEV:T' + str(self._temperature_channel) + 'TEMP:LOOP:RAMP:ENAB:OFF\r\n'
        response = self.query_and_receive(command)


    def turbo_on(self):
        command = 'SET:DEV:TURB' + self._turbo_channel + ':PUMP:SIG:STATE:ON\r\n'
        response = self.query_and_receive(command)


    def turbo_off(self):
        command = 'SET:DEV:TURB' + self._turbo_channel + ':PUMP:SIG:STATE:OFF\r\n'
        response = self.query_and_receive(command)


    def query_and_receive(self, command):
        """
        Queries the Oxford Triton 200 with the given command.

        :param command: Specifies a read/write of a property.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(self._address)
            s.settimeout(self._timeout)
            s.sendall(command)
            response = s.recv(self._bytes_to_read).decode()

        return response


    def extract_value(self, response, noun):
        expected_response = 'STAT:' + noun + ':'
        value = float(response.replace(expected_response, '').strip('\n'))
        return value