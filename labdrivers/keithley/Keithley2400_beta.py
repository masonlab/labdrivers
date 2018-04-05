from pyvisa.highlevel import VisaLibraryBase
import visa

class Keithley2400(VisaLibraryBase):
    
    def __init__(self, GPIBaddr):
        """Constructor for Keithley2400 class.

        Args:
            GPIBaddr (str): GPIB address of Keithley 2400.
        """
        self.GPIBaddr = GPIBaddr
        self.resource_manager = visa.ResourceManager()
        self.resource = None

    ####################
    # Session handling #
    ####################

    def open_resource(self):
        """Opens a session with the Keithley 2400."""
        resource = self.resource_manager.open_resource(self.GPIBaddr)
        self.resource = resource

    def close_resource(self):
        """Closes a session with the Keithley 2400."""
        self.resource_manager.close()
        self.resource = None

    ######################
    # Configure Commands #
    ######################

    def set_output(self, state):
        """Configures output to be on or off.
        
        Args:
            state (int): 1 for on, 0 for off
        """
        state = str(state)
        return self.resource.query(':outp:stat ' + state)

    def get_output(self):
        """Returns the state of the output."""
        return self.resource.query(':outp:stat?')

    ###################
    # Common Commands #
    ###################

    """
    There are more common commands for the IEEE-488.2 standard,
    but not all of them are particularly useful for our group so
    I am omitting them.
    """

    def clear_status(self):
        """Clears event registers and error queues."""
        return self.resource.query('*cls')

    def identify(self):
        """Returns manufacturer, model number, serial number, and 
        firmware revision levels.
        """
        return self.resource.query('*idn?')

    def reset_to_default(self):
        """Resets the Keithley 2400 to its default conditions."""
        return self.resource.query('*rst')