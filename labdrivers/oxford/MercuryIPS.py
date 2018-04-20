import socket
import visa

class MercuryIPS_visa():

    def __init__(self, resource_name):
        self.resource_name = resource_name
        self.resource_manager = visa.ResourceManager()
        self.axis = {   'x': 'GRPX',
                        'y': 'GRPY',
                        'z': 'GRPZ'  }

    def set_field_ramp_rate(self, axis, field_ramp_rate):
        instr = self.resource_manager.open_resource(self.resource_name)
        command = 'SET:DEV:' + self.axis[axis.lower()] + ':PSU:' \
                    + 'SIG:RFST' + str(field_ramp_rate) + '\n'
        response = instr.query(command)
        return response

    def get_field_ramp_rate(self, axis, field_ramp_rate):
        instr = self.resource_manager.open_resource(self.resource_name)
        command = 'READ:DEV:' + self.axis[axis.lower()] + ':PSU:' \
                    + 'SIG:RFST' + str(field_ramp_rate) + '\n'
        response = instr.query(command)
        return response

    def set_field_setpoint(self, axis, field_setpoint):
        instr = self.resource_manager.open_resource(self.resource_name)
        command = 'SET:DEV:' + self.axis[axis.lower()] + ':PSU:' \
                    + 'SIG:FSET' + str(field_setpoint) + '\n'
        response = instr.query(command)
        return response

    def get_field_setpoint(self, axis, field_setpoint):
        instr = self.resource_manager.open_resource(self.resource_name)
        command = 'READ:DEV:' + self.axis[axis.lower()] + ':PSU:' \
                    + 'SIG:FSET' + str(field_setpoint) + '\n'
        response = instr.query(command)
        return response

    def unclamp_magnet(self, axis):
        instr = self.resource_manager.open_resource(self.resource_name)
        command = 'SET:DEV:' + self.axis[axis.lower()] + ':PSU:' \
                    + 'ACTN:HOLD\n'
        response = instr.query(command)
        return response

    def clamp_magnet(self, axis):
        instr = self.resource_manager.open_resource(self.resource_name)
        command = 'SET:DEV:' + self.axis[axis.lower()] + ':PSU:' \
                    + 'ACTN:CLMP\n'
        response = instr.query(command)
        return response

    def ramp_to_setpoint(self, axis):
        instr = self.resource_manager.open_resource(self.resource_name)
        command = 'SET:DEV:' + self.axis[axis.lower()] + ':PSU:' \
                    + 'ACTN:RTOS\n'
        response = instr.query(command)
        return response

    def ramp_to_zero(self, axis):
        instr = self.resource_manager.open_resource(self.resource_name)
        command = 'SET:DEV:' + self.axis[axis.lower()] + ':PSU:' \
                    + 'ACTN:RTOZ\n'
        response = instr.query(command)
        return response

class MercuryIPS():

    PORT_NO = 7020

    def __init__(self, ip_address, timeout=10.0, bytes_to_read=2048):
        """Class constructor for the Mercury IPS.

        Args:
            ip_address (str): IP address of the Mercury IPS
            timeout (float): Seconds to wait for a response before
            raising an error.
            bytes_to_read (int): Maximum number of bytes to read from
            the response of the Mercury IPS.
        """
        self.ip_address = ip_address
        self.timeout = timeout
        self.bytes_to_read = bytes_to_read
        self.axis = {   'x': 'GRPX',
                        'y': 'GRPY',
                        'z': 'GRPZ'  }

    def get_field_target(self, axis):
        """Returns the field setpoint.

        Args:
            axis (str): The x, y, or z axis of the vector magnet.
            Input may be upper or lowercase and will be converted
            in any case.
        """
        noun = self._get_power_supply_group(axis.lower()) \
                + ':SIG:FSET\n'
        command = 'READ:' + noun
        response = self._query_and_receive(command)

    def set_field_target(self, axis):
        """Sets the field setpoint.

        Args:
            axis (str): The x, y, or z axis of the vector magnet.
            Input may be upper or lowercase and will be converted
            in any case.
        """
        noun = self._get_power_supply_group(axis.lower()) \
                + ':SIG:FSET\n'
        command = 'SET:' + noun
        response = self._query_and_receive(command)
        return self._extract_quantity(noun, response)

    def get_current_target(self, axis):
        pass
        
    def set_current_target(self, axis):
        pass

    def get_field_ramp_target(self, axis):
        pass

    def set_field_ramp_target(self, axis):
        pass

    def get_current_ramp_target(self, axis):
        pass

    def set_current_ramp_target(self, axis):
        pass

    def get_field(self, axis):
        pass

    def get_persistent_field(self, axis):
        pass

    def get_field_ramp(self, axis):
        pass

    def get_current_ramp(self, axis):
        pass

    ######################
    #  Helper functions  #
    ######################

    def _get_power_supply_group(self, axis):
        """Returns part of the noun.

        Args:
            axis (str): A string assumed to be in lowercase which
            indicates axis x, y, or z.
        """
        return 'DEV:' + self.axis[axis] + ':PSU:'

    def _query_and_receive(self, command):
        """Sends a query and returns the response.

        Args:
            command (str): A query for one of the power supply groups
            asking to get or set a current, field, ramp rate, or set
            point.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.ip_address, MercuryIPS.PORT_NO))
            s.settimeout(self.timeout)
            s.sendall(command)
            response = s.recv(self.bytes_to_read)
        
        return response.decode()

    def _extract_quantity(self, noun, response):
        """Extracts the queried quantity in the specified units.

        Current: A
        Field: T
        Current ramp rate: A/min
        Field ramp rate: T/min

        Args:
            response (str): The response from the Mercury IPS if it
            was sent a valid query.

        TODO:
            Look at the types of responses from all the nouns and
            determine how you will extract the numerical quantity
            if necessary.
        """
        to_replace = 'STAT:' + noun
        response = response.replace(to_replace, '')
        response = response.replace(':VALID\n', '')
        return response