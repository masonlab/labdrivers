"""Module containing classes to interface with Keithley brand instruments

This module requires a National Instruments VISA driver, which can be found at
https://www.ni.com/visa/

Attributes:
    resource_manager: the pyvisa resource manager which provides the visa
                      objects used for communicating over the GPIB interface

    logger: a python logger object


Classes:
    Keithley2400: a class for interfacing with a Keithley2400 SMU

"""

from math import ceil
import os.path
import time
import logging
import visa
import pandas as pd
from numpy import linspace

DEFAULT_NUM_POINTS = 1  # number of data points to collect for each measurement
DEFAULT_SAVE_PATH = "C://Data/pythonData/",

# create a logger object for this module
logger = logging.getLogger(__name__)

try:
    # the pyvisa manager we'll use to connect to the GPIB resources
    resource_manager = visa.ResourceManager()
except OSError:
    logger.exception("\n\tCould not find the VISA library. Is the National Instruments VISA driver installed?\n\n")


class Keithley2400():
    """A class to interface with the Keithley 2400 sourcemeter

    Args:
        GPIBaddr: the GPIB address of the instrument

    Attributes:
        data: a pandas dataframe containing data recorded by the instrument

    Methods:
        setMeasure
            Set what to measure (current, voltage, or resistance).
        setSourceDC
            Set the type (voltage or current) and level of a DC output.
        setSourceSweep
            Set the type and parameters of an output sweep
        setCompliance
            Set the type and level of the output compliance limit.

        getMeasure
            Get what type of input is currently being measured.
        getSource
            Get the currently configured type and level of the output.
        getCompliance
            Get the type and level of the output compliance limit.
        getConfig
            Get a string summarizing the current instrument configuration.

        readPoint
            Perform a single measurement with the current configuration, read the result, and store it in self.data.
        readTrace
            Perform a sweep measurement with the current configuration, read the results, and store them in self.data.
        outputOn
            Turn the instrument's output on, at the currently configured source value.
        outputOff
            Turn the instrument's output off.

    """

    def __init__(self, GPIBaddr):
        """Create an instance of the Keithley2400 class

        Arguments:
            GPIBaddr -- The GPIB address of the instrument.
        """
        try:
            self._visa_resource = resource_manager.open_resource("GPIB::%d" % GPIBaddr)
            self._initialize()
            self._clearData()

            self.data = pd.DataFrame()

        except NameError:
            error_msg = "\n\tCannot instantiate Keithley2400 instance. Is the National Instruments VISA library installed?\n\n"
            logger.exception(error_msg)
            raise NameError

        except Exception:
            error_msg = ""
            logger.exception(error_msg)

    #####################################################################################################
    # Internal methods: these are used internally but shouldn't be necessary for basic use of the class #
    #####################################################################################################

    # adapted from http://pyvisa.sourceforge.net/pyvisa.html#a-more-complex-example
    def _initialize(self):
        """Initialize the instrument to its default configuration."""

        self._visa_resource.write("*RST")
        self._visa_resource.write("*CLS")
        self._visa_resource.write("STATUS:MEASUREMENT:ENABLE 512")
        self._visa_resource.write("*SRE 1")
        self._visa_resource.write("ARM:COUNT 1")
        self._visa_resource.write("ARM:SOURCE BUS")
        self._visa_resource.write("TRACE:FEED SENSE1")
        self._visa_resource.write("SYSTEM:TIME:RESET:AUTO 0")

    def _clearData(self):
        """Clear the saved data from the previous measurement."""

        self._visa_resource.write("TRACE:CLEAR")
        self.data = pd.DataFrame()

    def _startNoWait(self):
        """Turn the output on, trigger a measurement, and proceed without waiting for the
        'measurement is done' signal from the instrument.
        """

        self._visa_resource.write("OUTPUT ON")
        self._visa_resource.write("TRACE:FEED:CONTROL NEXT")
        self._visa_resource.write("INIT")
        self._visa_resource.trigger()

    def _catchSRQ(self):
        """Wait for the 'measurement is done' signal from the instrument."""

        self._visa_resource.wait_for_srq(None)
        self._visa_resource.query("STATUS:MEASUREMENT?")

    def _startMeasurement(self):
        """Start a measurement and wait for the 'measurement is done' signal from the instrument."""

        self._startNoWait()
        self._catchSRQ()

    def _pullData(self):
        """Retrieve data from the instrument's internal buffer and store it in self.data."""

        # returns (V, I, I/V, time, ?) for each data point in a flat list
        # I/V column is only meaningful if the instrument was configured to measure resistance
        dataList = self._visa_resource.query_values("TRACE:DATA?")
        dataDict = {'volts': dataList[0::5],
                    'amps': dataList[1::5],
                    'ohms': dataList[2::5],
                    'seconds': dataList[3::5]}
        dataDF = pd.DataFrame(dataDict)

        self.data = self.data.append(dataDF)

    def _stopMeasurement(self):
        """Turn the output off, clear the instrument's internal buffer, and reset status bytes
        to prepare for a new measurement."""

        self._visa_resource.write("OUTPUT OFF")
        self._visa_resource.write("TRACE:CLEAR")
        self._visa_resource.query("STATUS:MEASUREMENT?")

    def _rampOutput(self, rampStart, rampTarget, nSteps=20, timeStep=50E-3):
        """Ramp the output smoothly from one value to another.

        Arguments:
            rampStart  -- The starting value for the output ramp, in volts or amps.
            rampTarget -- The ending value for the output ramp, in volts or amps.
           [nSteps]    -- Optional. The number of steps in the ramp.
           [timeStep]  -- Optional. The time in seconds between each step in the ramp.

        Returns:
            sourceValue -- The output value currently being sourced as a result of the ramp.
        """

        source = self.getSource()[0]  # either 'voltage' or 'current'

        for sourceValue in linspace(rampStart, rampTarget, nSteps):
            self.setSourceDC(source, sourceValue)
            time.sleep(timeStep)

        return sourceValue

    ##############################################################
    # Configuration methods: use these to configure the instrument #
    ##############################################################

    def setSourceDC(self, source, value=0):
        """Configure the instrument to provide a constant output.

        Arguments:
            source -- The type of output to source. One of ['voltage' | 'current'].
            value  -- The output value to source, in volts or amps.
        """
        if self.getMeasure() == 'RES':
            self._visa_resource.write("SENSE:RESISTANCE:MODE MANUAL")

        if source.lower() == "voltage":
            self._visa_resource.write("SOURCE:FUNCTION:MODE VOLTAGE")
            self._visa_resource.write("SOURCE:VOLTAGE:MODE FIXED")
            self._visa_resource.write("SOURCE:VOLTAGE:RANGE " + str(value))
            self._visa_resource.write("SOURCE:VOLTAGE:LEVEL " + str(value))
        elif source.lower() == "current":
            self._visa_resource.write("SOURCE:FUNCTION:MODE CURRENT")
            self._visa_resource.write("SOURCE:CURRENT:MODE FIXED")
            self._visa_resource.write("SOURCE:CURRENT:RANGE " + str(value))
            self._visa_resource.write("SOURCE:CURRENT:LEVEL " + str(value))
        else:
            logger.error("Source not set. Expected one of ['voltage' | 'current'].")

    def setSourceSweep(self, source, startValue, stopValue, sourceStep):
        """Configure the instrument to perform a sweep measurement.

        Arguments:
            source     -- The type of output to source. One of ['voltage' | 'current'].
            startValue -- The output value to start the sweep at, in volts or amps.
            stopValue  -- The output value to stop the sweep at, in volts or amps.
            sourceStep -- The value by which to step the output, in volts or amps.

        Returns:
            numPts     -- The number of data points to be collected.
        """

        # configure the instrument to record the appropriate number of points
        numPts = ceil(abs((stopValue - startValue) / sourceStep)) + 1
        self._visa_resource.write("TRIGGER:COUNT %d" % numPts)
        self._visa_resource.write("TRACE:POINTS %d" % numPts)

        if self.getMeasure() == 'RES':
            self._visa_resource.write("SENSE:RESISTANCE:MODE MANUAL")

        if source.lower() == "voltage":
            self._visa_resource.write("SOURCE:FUNCTION:MODE VOLTAGE")
            self._visa_resource.write("SOURCE:VOLTAGE:MODE SWEEP")
            self._visa_resource.write("SOURCE:VOLTAGE:RANGE " + str(stopValue))
            self._visa_resource.write("SOURCE:VOLTAGE:START " + str(startValue))
            self._visa_resource.write("SOURCE:VOLTAGE:STOP " + str(stopValue))
            self._visa_resource.write("SOURCE:VOLTAGE:STEP " + str(sourceStep))
        elif source.lower() == "current":
            self._visa_resource.write("SOURCE:FUNCTION:MODE CURRENT")
            self._visa_resource.write("SOURCE:CURRENT:MODE SWEEP")
            self._visa_resource.write("SOURCE:CURRENT:RANGE " + str(stopValue))
            self._visa_resource.write("SOURCE:CURRENT:START " + str(startValue))
            self._visa_resource.write("SOURCE:CURRENT:STOP " + str(stopValue))
            self._visa_resource.write("SOURCE:CURRENT:STEP " + str(sourceStep))
        else:
            logger.error("Sweep not configured. Expected source to be one of ['voltage' | 'current'].")

        return numPts

    def setMeasure(self, measure, senseMode=0):
        """Specify what the instrument should measure.

        Arguments:
            measure     -- What to measure. One of ['voltage' | 'current' | 'resistance'].
           [senseMode]  -- Optional. If measuring resistance, set to 0 for two-wire, 1 for four-wire measurements.
        """

        self._visa_resource.write("SENSE:FUNCTION:OFF 'CURR:DC', 'VOLT:DC', 'RES'")

        if measure.lower() == "voltage":
            self._visa_resource.write("SENSE:FUNCTION:ON 'VOLTAGE:DC'")
        elif measure.lower() == "current":
            self._visa_resource.write("SENSE:FUNCTION:ON 'CURRENT:DC'")
        elif measure.lower() == "resistance":
            self._visa_resource.write("SENSE:FUNCTION:ON 'CURRENT:DC'")
            self._visa_resource.write("SENSE:FUNCTION:ON 'RESISTANCE'")

            # configure the instrument to use two- or four-wire sense mode
            if senseMode == 0:
                self._visa_resource.write("SYSTEM:RSENSE OFF")
            elif senseMode == 1:
                self._visa_resource.write("SYSTEM:RSENSE ON")

        else:
            logger.error("Measurement type not set. Expected one of ['voltage' | 'current' | 'resistance']")

    def setCompliance(self, source, limit):
        """Specify the compliance limit for whatever the instrument is sourcing.

        Arguments:
            source -- The type of output the instrument is sourcing. One of ['voltage' | 'current'].
            limit  -- The compliance limit, in volts or amps.
        """

        if source.lower() == 'voltage':
            self._visa_resource.write("SENS:VOLT:PROT " + str(limit))
        if source.lower() == 'current':
            self._visa_resource.write("SENS:CURR:PROT " + str(limit))
        else:
            logger.error("Compliance limit not set. Expected one of ['voltage' | 'current']")

    def getMeasure(self):
        """Get what the instrument is currently configured to measure.

        Returns:
            measuring -- One of ['voltage' | 'current' | 'resistance']
        """

        # instrument returns one of "VOLT:DC", "RES" or "CURR:DC"
        conversion_dict = {'VOLT:DC': 'voltage', 'CURR:DC': 'current', 'RES': 'resistance'}
        query_result = self._visa_resource.query("SENSE:FUNCTION?").split(",")[-1].strip('"')
        measuring = conversion_dict[query_result]

        return measuring

    def getSource(self):
        """Get the type and level of output the instrument is currently configured to source.

        Returns:
            (source, value) -- source: one of ['voltage' | 'current'].
                               value:  the level of the output, in volts or amps.
        """

        source = self._visa_resource.query("SOURCE:FUNCTION:MODE?")

        if source == "VOLT":
            return ('voltage', self._visa_resource.query_values("SOURCE:VOLTAGE:LEVEL?")[0])
        elif source == "CURR":
            return ('current', self._visa_resource.query_values("SOURCE:CURRENT:LEVEL?")[0])

    def getCompliance(self):
        """Get the type and level of the currently configured compliance limit.

        Returns:
            (source, value) -- source: one of ['voltage' | 'current'].
                               value:  the level of the compliance limit, in volts or amps.
        """
    ########################################################
    # Operation methods: use these to operate the instrument #
    ########################################################

    def outputOn(self):
        """Turn the output on."""

        self._visa_resource.write("OUTPUT ON")

    def outputOff(self):
        """Turn the output off."""

        self._visa_resource.write("OUTPUT OFF")

    def readPoint(self):
        """Perform a single measurement with the current configuration, read the result, and store it in self.data."""

        self._visa_resource.write("TRACE:FEED:CONTROL NEXT")
        self._visa_resource.write("INIT")
        self._visa_resource.trigger()
        self._catchSRQ()
        self._pullData()

    # perform a measurement w/ current parameters
    def readTrace(self):
        self._clearData()
        self._startMeasurement()
        self._pullData()
        self._stopMeasurement()

    # starting with the output off, turn the output on then ramp the output up/down to a specified level
    def rampOutputOn(self, rampTarget, step, timeStep=50E-3):
        rampStart = 0
        sourceValue = self._rampOutput(rampStart, rampTarget, step, timeStep)
        return sourceValue

    # starting with the output on, ramp the output to 0, then turn the output off
    def rampOutputOff(self, rampStart, step, timeStep=50E-3):
        rampTarget = 0
        sourceValue = self._rampOutput(rampStart, rampTarget, step, timeStep)
        self.outputOff()
        return sourceValue

    # save the collected data to file
    # mode 'a' appends to existing file, mode 'i' increments file counter ie test0001.txt, test0002,txt
    def saveData(self, filePath, fileName="test.csv", mode='i'):
        """Save the collected data to file in csv format.

        Arguments:
            filePath --
            fileName --
           [mode]    -- Optional.
        """

        # make sure the filePath has a trailing slash
        if filePath[-1] != '/':
            filePath += '/'

        # make sure the fileName ends with .csv
        if fileName[-4:] != '.csv':
            fileName += '.csv'

        # append to existing files
        if mode == 'a':
            filePathAndName = os.path.join(filePath, fileName)
            self.data.to_csv(filePathAndName, index=False, mode='a+')
        # create new files with incrementing filenames, e.g. filename0001.csv
        else:
            saveCounter = 0
            while True:
                saveCounter += 1

                incrementalFileName = fileName.rstrip('.csv') + "{:04d}".format(saveCounter) + ".csv"
                filePathAndName = os.path.join(filePath, incrementalFileName)

                if not os.path.exists(filePathAndName):
                    break
            self.data.to_csv(filePathAndName, index=False, mode='w')

    def getConfig(self):
        """Get a string summarizing the current instrument configuration.

        Returns:
            config_str -- A string describing the current instrument configuration.
        """

        configDict = {'Measuring: ': self.getMeasure(),
                      'Sourcing: ': self.getSource(),
                      'Compliance: ': self.getCompliance()}

        return ' - '.join(configDict.items())

    #####################################################################################################
    # Deprecated methods
    #####################################################################################################

    def _setTLINK(self, inputTrigs, outputTrigs):
        """Set the instrument to use TLINK triggering."""
        self._visa_resource.write("TRIG:SOURCE TLINK")
        self._visa_resource.write("TRIG:INPUT {}".format(inputTrigs))
        self._visa_resource.write("TRIG:OUTPUT {}".format(outputTrigs))
        raise DeprecationWarning

    def _setNoTLINK(self):
        """Set the instrument to use immediate triggering."""
        self._visa_resource.write("TRIG:SOURCE IMMEDIATE")
        self._visa_resource.write("TRIG:INPUT NONE")
        self._visa_resource.write("TRIG:OUTPUT NONE")
        raise DeprecationWarning
