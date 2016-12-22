"""Module containing a class to interface with a SR830 Lockin Amplifier

This module requires a National Instruments VISA driver, which can be found at
https://www.ni.com/visa/

Attributes:
    resource_manager: the pyvisa resource manager which provides the visa
                      objects used for communicating over the GPIB interface

    logger: a python logger object


Classes:
    sr830: a class for interfacing with a SR830 Lockin Amplifier

"""
import time
import logging

# non standard-lib libraries, wrapped w/ try catch so that 
# readthedocs doesn't fail to build the documentation
try:
    import visa
    from pyvisa.errors import VisaIOError
except ImportError:
    pass

# create a logger object for this module
logger = logging.getLogger(__name__)
# added so that log messages show up in Jupyter notebooks
logger.addHandler(logging.StreamHandler())

try:
    # the pyvisa manager we'll use to connect to the GPIB resources
    resource_manager = visa.ResourceManager()
except OSError:
    logger.exception("\n\tCould not find the VISA library. Is the National Instruments VISA driver installed?\n\n")
except NameError:
    # visa module not imported, allow this so that docs build
    pass


class sr830():
    """A class to interface with the SR830 lockin amplifier

    Args:
        GPIBaddr: the GPIB address of the instrument
    """
    
    def __init__(self, GPIBaddr):
        """Create an instance of the sr830 class.

        Args:
            GPIBaddr (int): The GPIB address of the instrument.
        """
        self._visa_resource = resource_manager.open_resource("GPIB::%d" % GPIBaddr)
        
    def setFrequency(self, freq):
        """Set the frequency of the amplifier.

        Args:
            freq (int): the frequency of the amplifier
        """
        self._visa_resource.write("FREQ {}".format(freq))
    
    def getFrequency(self):
        """Get the frequency of the amplifier.

        Returns:
            int: the frequency of the amplifier
        """
        return self._visa_resource.query_ascii_values('FREQ?')[0]
    
    def setInput(self, i):
        """Set the input configuration:
            0: A
            1: A-B
            2: I (1 MOhm)
            3: I (100 MOhm)

        Args:
            i (int): the input configuration to use
        """
        self._visa_resource.write("ISRC {}".format(i))
        
    def getPhase(self):
        """Get the phase of the amplifier.

        Returns:
            int: the phase of the amplifier
        """
        return self._visa_resource.query_ascii_values('PHAS?')[0]

    def getInput(self):
        """Get the input configuration of the amplifier.
            0: A
            1: A-B
            2: I (1 MOhm)
            3: I (100 MOhm)

        Returns:
            int: the input configuration
        """
        return self._visa_resource.query_ascii_values('ISRC?')
    
    def setAmplitude(self, level):
        """Set the amplitude of the amplifier.

        Args:
            level (int): the amplitude of the amplifier in Vrms
        """
        self._visa_resource.write("SLVL {}".format(level))
        
    def getAmplitude(self):
        """Get the amplitude of the amplifier.

        Returns:
            int: the frequency of the amplifier
        """
        return self._visa_resource.query_ascii_values('SLVL?')[0]
       
    def recordValue(self, i, j):
        """Record the current value of two instrument parameters
        to the internal buffer. Possible parameters are:
            1: X
            2: Y
            3: R
            4: Theta
            5: Aux in 1
            6: Aux in 2
            7: Aux in 3
            8: Aux in 4
            9: Reference frequency
            10: CH1 display
            11: CH2 display

        Args:
            i (int): the first parameter to measure
            j (int): the second parameter to measure
        """
        self._visa_resource.write("SNAP? {}, {}".format(i, j))
        
    def rampOutput(self, rampStart, rampStop, rampStep, timeStep=0.1):
        """Ramp the output of the amplitude.

        Args:
            rampStart (float): starting value for the output in Vrms
            rampStop (float): final value for the output in Vrms
            rampStep (float): ramp step size in Vrms
            timeStep (float, optional): time step between ramp steps in s
        """
        currentLevel = rampStart
        
        # if ramping up
        if rampStart < rampStop:
            while currentLevel < rampStop:
                currentLevel += rampStep
                self.setAmplitude(currentLevel)
                time.sleep(timeStep)
                
        # if ramping down
        if rampStart > rampStop:
            while currentLevel > rampStop:
                currentLevel -= rampStep
                self.setAmplitude(currentLevel)
                time.sleep(timeStep)
                
    def setDisplay(self, channel, display, ratio=0):
        """Set the display of the amplifier.

        Display options are:
        (for channel 1)     (for channel 2)
            0: X            0: Y
            1: R            1: Theta
            2: X Noise      2: Y Noise
            3: Aux in 1     3: Aux in 3
            4: Aux in 2     4: Aux in 4

        Ratio options are (i.e. divide output by):
            0: none         0: none
            1: Aux in 1     1: Aux in 3
            2: Aux in 2     2: Aux in 4

        Args:
            channel (int): which channel to modify (1 or 2)
            display (int): what to display
            ratio (int, optional): display the output as a ratio
        """
        self._visa_resource.write("DDEF {}, {}, {}".format(channel, display, ratio))
        
    def getDisplay(self, channel):
        """Get the display configuration of the amplifier.

        Display options are:
        (for channel 1)     (for channel 2)
            0: X            0: Y
            1: R            1: Theta
            2: X Noise      2: Y Noise
            3: Aux in 1     3: Aux in 3
            4: Aux in 2     4: Aux in 4

        Args:
            channel (int): which channel to return the configuration for

        Returns:
            int: the parameter being displayed by the amplifier
        """
        return self._visa_resource.query_ascii_values("DDEF? {}".format(channel))
    
    def getSinglePoint(self, parameter):
        """Get the current value of a single parameter.
        Possible parameter values are:
            1: X
            2: Y
            3: R
            4: Theta

        Returns:
            float: the value of the specified parameter
        """
        return self._visa_resource.query_ascii_values("OUTP? {}".format(parameter))
            
    def getSnapshot(self, *parameters):
        """Get the current value of between two and six instrument parameters.
        Possible parameters are:
            1: X
            2: Y
            3: R
            4: Theta
            5: Aux in 1
            6: Aux in 2
            7: Aux in 3
            8: Aux in 4
            9: Reference frequency
            10: CH1 display
            11: CH2 display

        Args:
            *parameters (*[int]): the indices of the parameters to get, separated by commas

        Returns:
            list: the values of the specified parameters
        """

        commandString = "SNAP?" +  " {},"*len(parameters)
        return self._visa_resource.query_ascii_values(commandString.format(*parameters))
    
    def dataTransfer(self, i):
        self._visa_resource.write("FAST {}".format(i))
        
    def queryPoint(self, channel):
        return self._visa_resource.query_ascii_values("TRCA ? {}".format(channel))

    def getTimeConst(self):
        const_dict = {0: '10 us',  10: '1 s',
                      1: '30 us',  11: '3 s',
                      2: '100 us', 12: '10 s',
                      3: '300 us', 13: '30 s',
                      4: '1 ms',   14: '100 s',
                      5: '3 ms',   15: '300 s',
                      6: '10 ms',  16: '1 ks',
                      7: '30 ms',  17: '3 ks',
                      8: '100 ms', 18: '10 ks',
                      9: '300 ms', 19: '30 ks'}

        const_index = self._visa_resource.query_ascii_values('OFLT?')[0]
        return const_dict[const_index]

    def setTimeConst(self, const_index):
        """Set the time constant of the amplifier.
        Possible values:
                      0: 10 us,      10: 1 s,
                      1: 30 us,      11: 3 s,
                      2: 100 us,     12: 10 s,
                      3: 300 us,     13: 30 s,
                      4: 1 ms,       14: 100 s,
                      5: 3 ms,       15: 300 s,
                      6: 10 ms,      16: 1 ks,
                      7: 30 ms,      17: 3 ks,
                      8: 100 ms,     18: 10 ks,
                      9: 300 ms,     19: 30 ks}


        Args:
            const_index (int): the time constant to use
        """
        self._visa_resource.write("OFLT {}".format(const_index))

    def getConfiguration(self):
        freq = self.getFrequency()
        ampl = self.getAmplitude()
        tau = self.getTimeConst()
        theta = self.getPhase()
        return "Frequency: {:4} Hz - Amplitude: {:4} V - Phase {:4} - Time Constant: {}".format(freq, ampl, theta, tau)
