import socket

import visa


class MercuryIps():

    PORT_NO = 7020
    STR_FORMAT = '{.3f}'

    # Magnet class

    class Magnet():

        def __init__(self, axis, mode='ip', resource_name=None, ip_address=None, timeout=10.0,
                     bytes_to_read=2048):
            """
            Constructor for a magnet along a certain axis.

            :param axis: The axis for the magnet, given by ['GRPX'|'GRPY'|'GRPZ']
            :param mode: Connection, given by ['ip'|'visa']
            :param resource_name: VISA resource name of the MercuryIPS
            :param ip_address: IP address of the MercuryIPS
            :param timeout: Time to wait for a response from the MercuryIPS before throwing an error.
            :param bytes_to_read: Amount of information to read from a response
            """
            self.axis = axis

            self.mode = mode
            self.resource_name = resource_name
            self.resource_manager = visa.ResourceManager()
            self.ip_address = ip_address
            self.timeout = timeout
            self.bytes_to_read = bytes_to_read

        ###################
        # Query functions #
        ####################

        def query_ip(self, command):
            """Sends a query to the MercuryIPS via ethernet.
            
            :param command: The command, which should be in the NOUN + VERB format
            :return: The MercuryIPS response
            """
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.ip_address, MercuryIps.PORT_NO))
                s.settimeout(self.timeout)
                s.sendall(command.encode())
                response = s.recv(self.bytes_to_read).decode()

            return response.decode()

        def query_visa(self, command):
            """Sends a query to the MercuryIPS via VISA.
            
            :param command: The command, which should be in the NOUN + VERB format
            :return: The MercuryIPS response
            """
            instr = self.resource_manager.open_resource(self.resource_name)
            response = instr.query(command)
            instr.close()

            return response

        @staticmethod
        def extract_value(response, noun, unit):
            """Finds the value that is contained within the response to a previously sent query.
            
            :param response: The response from a query.
            :param noun: The part of the query that refers to the NOUN (refer to MercuryIPS documentation)
            :return: A floating-point value of the response, but without units.
            """
            expected_response = 'STAT:' + noun + ':'
            value = float(response.replace(expected_response, '').strip('\n').replace(unit, ''))
            return value

        QUERY_AND_RECEIVE = {'ip': query_ip, 'visa': query_visa}

        @property
        def field_setpoint(self):
            noun = 'DEV:' + self.axis + ':PSU:SIG:FSET'
            command = 'READ:' + noun + '\n'
            response = MercuryIps.Magnet.QUERY_AND_RECEIVE[self.mode](self, command)
            return self.extract_value(response, noun, 'T')

        @field_setpoint.setter
        def field_setpoint(self, value):
            setpoint = str(value)
            self._field_setpoint = setpoint
            command = 'SET:DEV:' + self.axis + ':PSU:SIG:FSET:' + setpoint + '\n'
            response = MercuryIps.Magnet.QUERY_AND_RECEIVE[self.mode](self, command)

        @property
        def field_ramp_rate(self):
            noun = 'DEV:' + self.axis + ':PSU:SIG:RFST'
            command = 'READ:' + noun + '\n'
            response = MercuryIps.Magnet.QUERY_AND_RECEIVE[self.mode](self, command)
            return self.extract_value(response, noun, 'T/m')

        @field_ramp_rate.setter
        def field_ramp_rate(self, value):
            ramp_rate = str(value)
            command = 'SET:DEV:' + self.axis + ':PSU:SIG:RFST:' + ramp_rate + '\n'
            response = MercuryIps.Magnet.QUERY_AND_RECEIVE[self.mode](self, command)

        @property
        def current_setpoint(self):
            noun = 'DEV:' + self.axis + ':PSU:SIG:CSET'
            command = 'READ:' + noun + '\n'
            response = MercuryIps.Magnet.QUERY_AND_RECEIVE[self.mode](self, command)
            return self.extract_value(response, noun, 'A')

        @current_setpoint.setter
        def current_setpoint(self, value):
            setpoint = str(value)
            command = 'SET:DEV:' + self.axis + ':PSU:SIG:CSET' + setpoint + '\n'
            response = MercuryIps.Magnet.QUERY_AND_RECEIVE[self.mode](self, command)

        @property
        def current_ramp_rate(self):
            noun = 'DEV:' + self.axis + ':PSU:SIG:RCST'
            command = 'READ:' + noun + '\n'
            response = MercuryIps.Magnet.QUERY_AND_RECEIVE[self.mode](self, command)
            return self.extract_value(response, noun, 'A/m')

        @current_ramp_rate.setter
        def current_ramp_rate(self, value):
            ramp_rate = str(value)
            command = 'SET:DEV:' + self.axis + ':PSU:SIG:RCST' + ramp_rate + '\n'
            response = MercuryIps.Magnet.QUERY_AND_RECEIVE[self.mode](self, command)

        @property
        def magnetic_field(self):
            noun = 'DEV:' + self.axis + ':PSU:SIG:FLD'
            command = 'READ:' + noun + '\n'
            response = MercuryIps.Magnet.QUERY_AND_RECEIVE[self.mode](self, command)
            return self.extract_value(response, noun, 'T')

        def ramp_to_setpoint(self):
            command = 'SET:DEV:' + self.axis + ':PSU:ACTN:RTOS\n'
            response = MercuryIps.Magnet.QUERY_AND_RECEIVE[self.mode](self, command)

        def ramp_to_zero(self):
            command = 'SET:DEV:' + self.axis + ':PSU:ACTN:RTOZ\n'
            response = MercuryIps.Magnet.QUERY_AND_RECEIVE[self.mode](self, command)

        def output_on(self):
            command = 'SET:DEV:' + self.axis + ':PSU:ACTN:HOLD\n'
            response = MercuryIps.Magnet.QUERY_AND_RECEIVE[self.mode](self, command)

        def output_off(self):
            command = 'SET:DEV:' + self.axis + ':PSU:ACTN:CLMP\n'
            response = MercuryIps.Magnet.QUERY_AND_RECEIVE[self.mode](self, command)

    def __init__(self, mode = 'ip',
                    resource_name = None,
                    ip_address = None, timeout=10.0, bytes_to_read=2048):
        """
        Parameters:
        :param mode: ['ip'|'visa']
        :param resource_name: VISA resource name of the Mercury iPS
        :param ip_address: IP address of the Mercury iPS
        :param timeout: Time in seconds to wait for command acknowledgment
        :param bytes_to_read: Number of bytes to read from query
        """
        supported_modes = ('ip', 'visa')

        if mode.lower().strip() in supported_modes:
            self.mode = mode
        else:
            raise RuntimeError('Mode is not currently supported.')

        self.x_magnet = MercuryIps.Magnet('GRPX', mode=mode, resource_name=resource_name,
                                          ip_address=ip_address, timeout=timeout, bytes_to_read=bytes_to_read)
        self.y_magnet = MercuryIps.Magnet('GRPY', mode=mode, resource_name=resource_name,
                                          ip_address=ip_address, timeout=timeout, bytes_to_read=bytes_to_read)
        self.z_magnet = MercuryIps.Magnet('GRPZ', mode=mode, resource_name=resource_name,
                                          ip_address=ip_address, timeout=timeout, bytes_to_read=bytes_to_read)

    def circle_sweep(self, field_radius, number_points):
        pass
