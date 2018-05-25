import socket
import visa

class MercuryIPS():

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
            if mode in SUPPORTED_MODES:
                self.mode = mode
        except:
            raise RuntimeError('Mode is not currently supported.')
        
        self.resource_name = resource_name
        self.resource_manager = visa.ResourceManager()

        self.ip_address = ip_address
        self.timeout = timeout
        self.bytes_to_read = bytes_to_read

        self.axis = 'GRPZ'
        self.magnet_unclamped = False
        self.field_setpoint = 0.0
        self.field_ramp_rate = 0.0


    @property
    def axis(self):
        return self.axis


    @axis.setter
    def axis(self, value):
        self.axis = MercuryIPS.AXIS_GROUP[value.lower()]


    @property
    def magnet_unclamped(self):
        return self.magnet_unclamped


    @magnet_unclamped.setter
    def magnet_unclamped(self, value):
        self.magnet_unclamped = value
        if self.magnet_unclamped:
            clamp_status = 'HOLD'
        else:
            clamp_status = 'CLMP'
        
        command = 'SET:DEV:' + self.axis + ':PSU:ACTN:' + clamp_status + '\n'
        response = MercuryIPS.QUERY_AND_RECEIVE[self.mode](command)


    @property
    def field_setpoint(self):
        return self.field_setpoint

    
    @field_setpoint.setter
    def field_setpoint(self, value):
        setpoint = STR_FORMAT.format(value)
        command = 'READ:DEV:' + self.axis + ':PSU:SIG:FSET:' + setpoint + '\n'
        response = MercuryIPS.QUERY_AND_RECEIVE[self.mode](command)
        self.field_setpoint = setpoint


    @property
    def field_ramp_rate(self):
        return self.field_ramp_rate


    @field_ramp_rate.setter
    def field_ramp_rate(self, value):
        setpoint = STR_FORMAT.format(value)
        command = 'READ:DEV:' + self.axis + ':PSU:SIG:FSET:' + setpoint + '\n'
        response = MercuryIPS.QUERY_AND_RECEIVE[self.mode](command)
        self.field_ramp_rate = setpoint


    def ramp_to_setpoint(self):
        command = 'SET:DEV:' + self.axis + ':PSU:ACTN:RTOS\n'
        response = MercuryIPS.QUERY_AND_RECEIVE[self.mode](command)


    def ramp_to_zero(self):
        command = 'SET:DEV:' + self.axis[axis.lower()] + ':PSU:ACTN:RTOZ\n'
        response = MercuryIPS.QUERY_AND_RECEIVE[self.mode](command)


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