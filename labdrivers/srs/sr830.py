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
    
    def __init__(self, GPIBaddr):
        self._visa_resource = resource_manager.open_resource("GPIB::%d" % GPIBaddr)
        
    def setFrequency(self, freq):
        self._visa_resource.write("FREQ {}".format(freq))
    
    def getFrequency(self):
        return self._visa_resource.query_ascii_values('FREQ?')[0]
    
    def setInput(self, i):
        self._visa_resource.write("ISRC {}".format(i))
        
    def getPhase(self):
        return self._visa_resource.query_ascii_values('PHAS?')[0]

    def getInput(self):
        return self._visa_resource.query_ascii_values('ISRC?')
    
    def setAmplitude(self, level):
        self._visa_resource.write("SLVL {}".format(level))
        
    def getAmplitude(self):
        return self._visa_resource.query_ascii_values('SLVL?')[0]
       
    def recordValue(self, i, j):
        self._visa_resource.write("SNAP? {}, {}".format(i, j))
        
    def rampOutput(self, rampStart, rampStop, rampStep, timeStep=0.1):
        
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
        self._visa_resource.write("DDEF {}, {}, {}".format(channel, display, ratio))
        
    def getDisplay(self, channel):
        return self._visa_resource.query_ascii_values("DDEF? {}".format(channel))
    
    def getSinglePoint(self, parameter):
        return self._visa_resource.query_ascii_values("OUTP? {}".format(parameter))
            
    def getSnapshot(self, *parameters):
        commandString = "SNAP?" +  " {},"*len(parameters)
        return self._visa_resource.query_ascii_values(commandString.format(*parameters))
    
    def dataTransfer(self, i):
        self._visa_resource.write("FAST {}".format(i))
        
    def queryPoint(self, channel):
        return ("TRCA ? {}".format(channel))

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
        self._visa_resource.write("OFLT {}".format(const_index))

    def getConfiguration(self):
        freq = self.getFrequency()
        ampl = self.getAmplitude()
        tau = self.getTimeConst()
        theta = self.getPhase()
        return "Frequency: {:4} Hz - Amplitude: {:4} V - Phase {:4} - Time Constant: {}".format(freq, ampl, theta, tau)
