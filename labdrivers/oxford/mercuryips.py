import socket

import visa


class MercuryIps:

    # Magnet class

    class Magnet:
        """
        Constructor for a magnet along a certain axis.

        :param axis: The axis for the magnet, given by ['GRPX'|'GRPY'|'GRPZ']
        :type axis: string
        :param mode: Connection, given by ['ip'|'visa']
        :type mode: string
        :param resource_name: VISA resource name of the MercuryIPS
        :type resource_name: string
        :param ip_address: IP address of the MercuryIPS
        :type ip_address: string
        :param port: Port number of the Mercury iPS
        :type port: integer
        :param timeout: Time to wait for a response from the MercuryIPS before throwing an error.
        :type timeout: float
        :param bytes_to_read: Amount of information to read from a response
        :type bytes_to_read: integer
        """

        def __init__(self, axis, mode='ip', resource_name=None, ip_address=None, port=7020, timeout=10.0,
                     bytes_to_read=2048):
            self.axis = axis
            self.mode = mode
            self.resource_name = resource_name
            self.resource_manager = visa.ResourceManager()
            self.ip_address = ip_address
            self.port = port
            self.timeout = timeout
            self.bytes_to_read = bytes_to_read

        ###################
        # Query functions #
        ####################

        def query_ip(self, command):
            """Sends a query to the MercuryIPS via ethernet.
            
            :param command: The command, which should be in the NOUN + VERB format
            :type command: string
            :returns str: The MercuryIPS response
            """
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.ip_address, self.port))
                s.settimeout(self.timeout)
                s.sendall(command.encode())
                response = s.recv(self.bytes_to_read).decode()

            return response.decode()

        def query_visa(self, command):
            """Sends a query to the MercuryIPS via VISA.
            
            :param command: The command, which should be in the NOUN + VERB format
            :type command: string
            :returns str: The MercuryIPS response
            """
            instr = self.resource_manager.open_resource(self.resource_name)
            response = instr.query(command)
            instr.close()

            return response

        @staticmethod
        def extract_value(response, noun, unit):
            """Finds the value that is contained within the response to a previously sent query.
            
            :param response: The response from a query.
            :type response: string
            :param noun: The part of the query that refers to the NOUN (refer to MercuryIPS documentation).
            :param unit: The measurement unit (e.g. K for Kelvin, T for Tesla).
            :returns float: The value of the response, but without units.
            """
            expected_response = 'STAT:' + noun + ':'
            value = float(response.replace(expected_response, '').strip('\n').replace(unit, ''))
            return value

        # Employing hash tables instead of if-else trees
        QUERY_AND_RECEIVE = {'ip': query_ip, 'visa': query_visa}

        @property
        def field_setpoint(self):
            """The magnetic field set point in Tesla"""
            noun = 'DEV:' + self.axis + ':PSU:SIG:FSET'
            command = 'READ:' + noun + '\n'
            response = MercuryIps.Magnet.QUERY_AND_RECEIVE[self.mode](self, command)
            return self.extract_value(response, noun, 'T')

        @field_setpoint.setter
        def field_setpoint(self, value):
            if ((self.axis == 'GRPZ' and (-6 <= value <= 6)) or
                    ((self.axis == 'GRPX' or self.axis == 'GRPY') and (-1 <= value <= 1))):
                setpoint = str(value)
                command = 'SET:DEV:' + self.axis + ':PSU:SIG:FSET:' + setpoint + '\n'
                response = MercuryIps.Magnet.QUERY_AND_RECEIVE[self.mode](self, command)

                if not response:
                    raise RuntimeWarning("No response from the MercuryIps after querying the field setpoint.")
            else:
                raise RuntimeError("The setpoint must be within the proper limits.")

        @property
        def field_ramp_rate(self):
            """The magnetic field ramp rate in Tesla per minute along the magnet axis."""
            noun = 'DEV:' + self.axis + ':PSU:SIG:RFST'
            command = 'READ:' + noun + '\n'
            response = MercuryIps.Magnet.QUERY_AND_RECEIVE[self.mode](self, command)
            return self.extract_value(response, noun, 'T/m')

        @field_ramp_rate.setter
        def field_ramp_rate(self, value):
            ramp_rate = str(value)
            command = 'SET:DEV:' + self.axis + ':PSU:SIG:RFST:' + ramp_rate + '\n'
            response = MercuryIps.Magnet.QUERY_AND_RECEIVE[self.mode](self, command)

            if not response:
                raise RuntimeWarning("No response after setting a field ramp rate.")

        @property
        def current_setpoint(self):
            """The set point of the current for a magnet in Amperes."""
            noun = 'DEV:' + self.axis + ':PSU:SIG:CSET'
            command = 'READ:' + noun + '\n'
            response = MercuryIps.Magnet.QUERY_AND_RECEIVE[self.mode](self, command)
            return self.extract_value(response, noun, 'A')

        @current_setpoint.setter
        def current_setpoint(self, value):
            setpoint = str(value)
            command = 'SET:DEV:' + self.axis + ':PSU:SIG:CSET' + setpoint + '\n'
            response = MercuryIps.Magnet.QUERY_AND_RECEIVE[self.mode](self, command)

            if not response:
                raise RuntimeWarning("No response after setting current set point.")

        @property
        def current_ramp_rate(self):
            """The ramp rate of the current for a magnet in Amperes per minute."""
            noun = 'DEV:' + self.axis + ':PSU:SIG:RCST'
            command = 'READ:' + noun + '\n'
            response = MercuryIps.Magnet.QUERY_AND_RECEIVE[self.mode](self, command)
            return self.extract_value(response, noun, 'A/m')

        @current_ramp_rate.setter
        def current_ramp_rate(self, value):
            ramp_rate = str(value)
            command = 'SET:DEV:' + self.axis + ':PSU:SIG:RCST' + ramp_rate + '\n'
            response = MercuryIps.Magnet.QUERY_AND_RECEIVE[self.mode](self, command)

            if not response:
                raise RuntimeWarning("No response after setting current ramp rate.")

        @property
        def magnetic_field(self):
            """Gets the magnetic field."""
            noun = 'DEV:' + self.axis + ':PSU:SIG:FLD'
            command = 'READ:' + noun + '\n'
            response = MercuryIps.Magnet.QUERY_AND_RECEIVE[self.mode](self, command)
            return self.extract_value(response, noun, 'T')

        def ramp_to_setpoint(self):
            """Ramps a magnet to the setpoint."""
            command = 'SET:DEV:' + self.axis + ':PSU:ACTN:RTOS\n'
            response = MercuryIps.Magnet.QUERY_AND_RECEIVE[self.mode](self, command)

            if not response:
                raise RuntimeWarning("No response after attempting to ramp to set point.")

        def ramp_to_zero(self):
            """Ramps a magnet from its current magnetic field to zero field."""
            command = 'SET:DEV:' + self.axis + ':PSU:ACTN:RTOZ\n'
            response = MercuryIps.Magnet.QUERY_AND_RECEIVE[self.mode](self, command)

            if not response:
                raise RuntimeWarning("No response after attempting to ramp to zero.")

        def ramping(self):
            """Queries if magnet is ramping."""
            # ask if ramping to zero
            # command = 'READ:DEV:' + self.axis + ':PSU:ACTN:RTOZ\n'
            # ask if ramping to set
            # command = 'READ:DEV:' + self.axis + ':PSU:ACTN:RTOS\n'
            # TODO: find out what kind of response you expect
            pass

        def hold(self):
            """Puts a magnet in a HOLD state.
            
            This action does one of the following:
            1) Stops a ramp
            2) Allows the field and current to ramp
            """
            command = 'SET:DEV:' + self.axis + ':PSU:ACTN:HOLD\n'
            response = MercuryIps.Magnet.QUERY_AND_RECEIVE[self.mode](self, command)

            if not response:
                raise RuntimeWarning("No response after telling Mercury iPS to hold.")

        def holding(self):
            """Queries if magnet is in a HOLD state."""
            # command = 'READ:DEV:' + self.axis + ':PSU:ACTN:HOLD\n'
            # response = MercuryIps.Magnet.QUERY_AND_RECEIVE[self.mode](self, command)
            # TODO: find out what kind of response you expect
            pass

        def clamp(self):
            """Puts a magnet in a CLAMP state."""
            command = 'SET:DEV:' + self.axis + ':PSU:ACTN:CLMP\n'
            response = MercuryIps.Magnet.QUERY_AND_RECEIVE[self.mode](self, command)

            if not response:
                raise RuntimeWarning("No response after telling Mercury iPS to clamp.")

        def clamped(self):
            """Queries if magnet is in a CLAMP state."""
            # command = 'READ:DEV:' + self.axis + ':PSU:ACTN:CLMP\n'
            # response = MercuryIps.Magnet.QUERY_AND_RECEIVE[self.mode](self, command)
            # TODO: find out what kind of response you expect
            pass

    def __init__(self, mode='ip',
                 resource_name=None,
                 ip_address=None, port=7020, timeout=10.0, bytes_to_read=2048):
        """
        Parameters:
        :param str mode: The connection to the iPS, either 'ip' or 'visa'
        :param str resource_name: VISA resource name of the Mercury iPS
        :param str ip_address: IP address of the Mercury iPS
        :param port: Port number of the Mercury iPS
        :type port: integer
        :param timeout: Time in seconds to wait for command acknowledgment
        :type timeout: float
        :param bytes_to_read: Number of bytes to read from query
        :type bytes_to_read: integer
        """
        supported_modes = ('ip', 'visa')

        if mode.lower().strip() in supported_modes:
            self.mode = mode
        else:
            raise RuntimeError('Mode is not currently supported.')

        self.x_magnet = MercuryIps.Magnet('GRPX', mode=mode, resource_name=resource_name, ip_address=ip_address,
                                          port=7020, timeout=timeout, bytes_to_read=bytes_to_read)
        self.y_magnet = MercuryIps.Magnet('GRPY', mode=mode, resource_name=resource_name, ip_address=ip_address,
                                          port=7020, timeout=timeout, bytes_to_read=bytes_to_read)
        self.z_magnet = MercuryIps.Magnet('GRPZ', mode=mode, resource_name=resource_name, ip_address=ip_address,
                                          port=7020, timeout=timeout, bytes_to_read=bytes_to_read)

    def circle_sweep(self, field_radius, number_points):
        pass
