import socket

class Triton200():

    def __init__(self, parameters):
        """
        Constructor for the Triton200 class.

        :param parameters: A dictionary containing the IP address, port
        number, timeout duration, and the number of bytes to read.
        """

        self.address = (parameters['ip_address'], parameters['port_number'])
        self.timeout = parameters['timeout']
        self.bytes_to_read = parameters['bytes_to_read']
        # Default channel is 5 because it's the 20 mK plate
        self.channel = 5

    @property
    def channel(self):
        return self.channel
    
    @channel.setter
    def channel(self, value):
        self.channel = value

    @property
    def temperature(self):
        command = ('READ:DEV:T' + str(self.channel) + ':TEMP:SIG:TEMP\r\n').encode()
        response = self.query_and_receive(command)

        return # TODO: extract response
    
    @property
    def temperature_setpoint(self):
        command = ('READ:DEV:H' + str(self.channel) + 'HTR:SIG:POWR\r\n').encode()
        response = self.query_and_receive(command)

    @temperature_setpoint.setter
    def temperature_setpoint(self, value):


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