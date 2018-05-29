import socket

class triton200():

    # TODO:
    # Find the proper channels for these
    CERNOX_CHANNEL = '4'
    RUO2_CHANNEL = '5'

    VALID_CHANNELS = (CERNOX_CHANNEL, RUO2_CHANNEL)

    def __init__(self, ip_address, port_number = 33756, timeout = 10000, bytes_to_read = 2048):
        """
        Constructor for the Triton200 class.

        :param parameters: A dictionary containing the IP address, port
        number, timeout duration, and the number of bytes to read.
        """
        self._address = (str(ip_address), str(port_number))
        self._timeout = timeout
        self._bytes_to_read = bytes_to_read
        # Default channel is 5 because it's the 20 mK plate
        self._temperature_channel = triton200.RUO2_CHANNEL
        self._heater_channel = '1'


    @property
    def channel(self):
        return self._temperature_channel
    

    @channel.setter
    def channel(self, value):
        self._temperature_channel = str(value)


    @property
    def temperature_setpoint(self):
        command = ('READ:DEV:T' + str(self.channel) + 'HTR:SIG:POWR\r\n').encode()
        response = self.query_and_receive(command)


    @temperature_setpoint.setter
    def temperature_setpoint(self, value):
        pass


    @property
    def temperature(self):
        command = ('READ:DEV:T' + str(self.channel) + ':TEMP:SIG:TEMP\r\n').encode()
        response = self.query_and_receive(command)

        return # TODO: extract response


    def query_and_receive(self, command):
        """
        Queries the Oxford Triton 200 with the given command.

        :param command: Specifies a read/write of a property.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(self.address)
            s.settimeout(self.timeout)
            s.sendall(command)
            response = s.recv(self.bytes_to_read).decode()

        return response


    def extract_value(self, response, noun):
        expected_response = 'STAT:' + noun + ':'
        value = float(response.replace(expected_response, '').strip('\n'))
        return value