import time
import logging
import visa

# create a logger object for this module
logger = logging.getLogger(__name__)
# added so that log messages show up in Jupyter notebooks
logger.addHandler(logging.StreamHandler())

try:
    # the pyvisa manager we'll use to connect to the GPIB resources
    resource_manager = visa.ResourceManager()
except OSError:
    logger.exception("\n\tCould not find the VISA library. Is the National Instruments VISA driver installed?\n\n")


class sr830():
    
    def __init__(self, GPIBaddr):
        self._visa_resource = resource_manager.open_resource("GPIB::%d" % GPIBaddr)
        
    def setFrequency(self, freq):
        self._visa_resource.write("FREQ {}".format(freq))
    
    def getFrequency(self):
        return self._visa_resource.query_ascii_values('FREQ?')
    
    def setInput(self, i):
        self._visa_resource.write("ISRC {}".format(i))
        
    def getInput(self):
        return self._visa_resource.query_ascii_values('ISRC?')
    
    def setAmplitude(self, level):
        self._visa_resource.write("SLVL {}".format(level))
        
    def getAmplitude(self):
        return self._visa_resource.query_ascii_values('SLVL?')
       
    def __init__(self, GPIBaddr):
        super(sr830, self).__init__("GPIB::%d" % GPIBaddr)
  
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
