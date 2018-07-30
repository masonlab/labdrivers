import socket

import visa

class mercury_ips():

    PORT_NO = 7020
    AXIS_GROUP = {  'x': 'GRPX',
                    'y': 'GRPY',
                    'z': 'GRPZ' }
    SUPPORTED_MODES = ('ip', 'visa')
    QUERY_AND_RECEIVE = {   'ip': query_ip,
                'visa': query_visa  }
    STR_FORMAT = '{.3f}'

    def __init__(self, mode = 'ip',
                    resource_name = None,
                    ip_address = None, timeout=10.0, bytes_to_read=2048):
        """
        Constructor for the MercuryIPS class.
        """
        try:
            if mode in MercuryIPS.SUPPORTED_MODES:
                self.mode = mode
        except:
            raise RuntimeError('Mode is not currently supported.')
        
        self.resource_name = resource_name
        self.resource_manager = visa.ResourceManager()

        self.ip_address = ip_address
        self.timeout = timeout
        self.bytes_to_read = bytes_to_read

        self._axis = 'GRPZ'


    @property
    def axis(self):
        return self._axis


    @axis.setter
    def axis(self, value):
        self._axis = MercuryIPS.AXIS_GROUP[str(value).lower()]

    
    @property
    def field_setpoint(self):
        noun = 'DEV:' + self.axis + ':PSU:SIG:FSET'
        command = 'READ:' + noun + '\n'
        response = MercuryIPS.QUERY_AND_RECEIVE[self.mode](command)
        return self.extract_value(response, noun)


    @field_setpoint.setter
    def field_setpoint(self, value):
        setpoint = MercuryIPS.STR_FORMAT.format(value)
        self._field_setpoint = setpoint
        command = 'SET:DEV:' + self.axis + ':PSU:SIG:FSET:' + setpoint + '\n'
        response = MercuryIPS.QUERY_AND_RECEIVE[self.mode](command)


    @property
    def field_ramp_rate(self):
        noun = 'DEV:' + self.axis + ':PSU:SIG:RFST'
        command = 'READ:' + noun + '\n'
        response = MercuryIPS.QUERY_AND_RECEIVE[self.mode](command)
        return self.extract_value(response, noun)


    @field_ramp_rate.setter
    def field_ramp_rate(self, value):
        ramp_rate = MercuryIPS.STR_FORMAT.format(value)
        command = 'SET:DEV:' + self.axis + ':PSU:SIG:RFST:' + ramp_rate + '\n'
        response = MercuryIPS.QUERY_AND_RECEIVE[self.mode](command)


    @property
    def current_setpoint(self):
        noun = 'DEV:' + self.axis + ':PSU:SIG:CSET'
        command = 'READ:' + noun + '\n'
        response = MercuryIPS.QUERY_AND_RECEIVE[self.mode](command)
        return self.extract_value(response, noun)


    @current_setpoint.setter
    def current_setpoint(self, value):
        setpoint = MercuryIPS.STR_FORMAT.format(value)
        command = 'SET:DEV:' + self.axis + ':PSU:SIG:CSET' + setpoint + '\n'
        response = MercuryIPS.QUERY_AND_RECEIVE[self.mode](command)


    @property
    def current_ramp_rate(self):
        noun = 'DEV:' + self.axis + ':PSU:SIG:RCST'
        command = 'READ:' + noun + '\n'
        response = MercuryIPS.QUERY_AND_RECEIVE[self.mode](command)
        return self.extract_value(response, noun)


    @current_ramp_rate.setter
    def current_ramp_rate(self, value):
        ramp_rate = MercuryIPS.STR_FORMAT.format(value)
        command = 'SET:DEV:' + self.axis + ':PSU:SIG:RCST' + ramp_rate + '\n'
        response = MercuryIPS.QUERY_AND_RECEIVE[self.mode](command)


    @property
    def magnetic_field(self):
        noun = 'DEV:' + self.axis + ':PSU:SIG:FLD'
        command = 'READ:' + noun + '\n'
        response = MercuryIPS.QUERY_AND_RECEIVE[self.mode](command)
        return self.extract_value(response, noun)


    def ramp_to_setpoint(self):
        command = 'SET:DEV:' + self.axis + ':PSU:ACTN:RTOS\n'
        response = MercuryIPS.QUERY_AND_RECEIVE[self.mode](command)


    def ramp_to_zero(self):
        command = 'SET:DEV:' + self.axis + ':PSU:ACTN:RTOZ\n'
        response = MercuryIPS.QUERY_AND_RECEIVE[self.mode](command)


    def output_on(self):
        command = 'SET:DEV:' + self.axis + ':PSU:ACTN:HOLD\n'
        response = MercuryIPS.QUERY_AND_RECEIVE[self.mode](command)


    def output_off(self):
        command = 'SET:DEV:' + self.axis + ':PSU:ACTN:CLMP\n'
        response = MercuryIPS.QUERY_AND_RECEIVE[self.mode](command)


    #  #  #  #  #  #  #  #
    #  Query functions   #
    #  #  #  #  #  #  #  #


    def query_ip(self, command):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.ip_address, MercuryIPS.PORT_NO))
            s.settimeout(self.timeout)
            s.sendall(command)
            response = s.recv(self.bytes_to_read)
        
        return response.decode()


    def query_visa(self, command):
        instr = self.resource_manager.open_resource(self.resource_name)
        response = instr.query_visa(command)
        instr.close()

        return response


    def extract_value(self, response, noun):
        expected_response = 'STAT:' + noun + ':'
        value = float(response.replace(expected_response, '').strip('\n'))
        return value