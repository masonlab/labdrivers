"""Python driver to connect the Triton 200 dilution fridge to the controller.

Typically this should be used for the 0 to 2K range. Anything above 2K will
cause the turbo pump to be unhappy, and so should be avoided.
"""

import socket


class Triton200():

    default_channel = 5

    def __init__(self, parameters):
        """Constructor for Triton200.

        Keyword arguments:

        parameters:
            This is a dictionary of four parameters:
            ip_address (str), port (int), timeout (int),
            bytes_to_read (int).
        """
        self.address = (parameters['ip_address'], parameters['port'])
        self.timeout = parameters['timeout']
        self.bytes_to_read = parameters['bytes_to_read']

    def get_temperature(self, channel=default_channel):
        """Reads the temperature of the given channel.

        Keyword arguments:

        channel:
            The channel corresponding to the location where the
            user wants to read the temperature. Defaults to 5, the
            RuO2 plate.
        """
        parameter = self._get_temperature_parameter(channel)
        command = ('READ:'
                    + parameter
                    + '\r\n').encode()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(self.address)
            s.settimeout(self.timeout)
            s.sendall(command)
            response = s.recv(self.bytes_to_read).decode()

        response = response.strip('\n')
        response = response.replace('STAT:' + parameter, '')
        response = response.replace('K', '')

        return float(response)

    def set_temperature(self, new_temperature=0, channel=default_channel):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(self.address)
            s.settimeout(self.timeout)
        pass

    def get_heater_range(self, channel=default_channel):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(self.address)
            s.settimeout(self.timeout)
        pass

    def set_heater_range(self, new_heater_range, channel=default_channel):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(self.address)
            s.settimeout(self.timeout)
        pass

    def _get_temperature_parameter(self, channel):
        """Obtains the temperature parameter for calls and responses.

        Keyword arguments:

            channel:
                The temperature controller channel as specified on
                the Triton GUI.
        """
        return 'DEV:T' + str(channel) + ':TEMP:SIG:TEMP'

    def _get_heater_range_parameter(self, channel):
        """Obtains the heater range parameter for calls and responses.

        Keyword arguments:

            channel:
                The heater channel as specified on the Triton GUI.
        """
        return 'DEV:H' + str(channel) + ':HTR:SIG:POWR'