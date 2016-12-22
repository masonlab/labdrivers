"""Module containing a class to interface with a QuantumDesign PPMS DynaCool

This module provides a python wrapper to the C# .dll provided by QuantumDesign.
Importing the C# .dll requires the python module 'pythonnet'.

Attributes:
    logger: a python logger object


Classes:
    dynacool: a class for interfacing with a QuantumDesign PPMS DynaCool

"""

import logging

# create a logger object for this module
logger = logging.getLogger(__name__)
# added so that log messages show up in Jupyter notebooks
logger.addHandler(logging.StreamHandler())

# requires Python for .NET
# can be installed with 'pip install pythonnet'
try:
    import clr

    try:
        # load the C# .dll supplied by Quantum Design
        clr.AddReference('QDInstrument')

        # import the C# classes for interfacing with the PPMS
        from QuantumDesign.QDInstrument import QDInstrumentBase, QDInstrumentFactory

        QDI_DYNACOOL_TYPE = QDInstrumentBase.QDInstrumentType.DynaCool
        DEFAULT_PORT = 11000

    except:
        if clr.FindAssembly('QDInstrument') is None:
            logger.exception('\n\tCould not find QDInstrument.dll')
        else:
            logger.exception('\n\tFound QDInstrument.dll at {}'.format(clr.FindAssembly('QDInstrument')))
            logger.exception('\n\tTry right-clicking the .dll, selecting "Properties", and then clicking "Unblock"')

except ImportError:
    logger.exception('\n\tCould not import clr. Install Python for .NET with "pip install pythonnet"')


class dynacool:
    """A class to interface with the QuantumDesign PPMS Dynacool.

    This class is a thin wrapper around the C# QuantumDesign.QDInstrument.QDInstrumentBase class
    provided in the QDInstrument.dll file.
    """

    def __init__(self, ip_address, remote=True):
        self.qdi_instrument = QDInstrumentFactory.GetQDInstrument(
            QDI_DYNACOOL_TYPE, remote, ip_address, DEFAULT_PORT)

    def getTemperature(self):
        """Get the current temperature in Kelvin.

        Returns:
            float: current chamber temperature in Kelvin
        """
        return self.qdi_instrument.GetTemperature(0, 0)

    def setTemperature(self, temp, rate=10):
        """Set a target temperature and sweep rate.

        Args:
            temp (float): the target temperature in Kelvin
            rate (int): the sweep rate in Kelvin / minute

        Returns:
            int: status
        """
        return self.qdi_instrument.SetTemperature(temp, rate, 0)

    def waitForTemperature(self, delay=5, timeout=600):
        """Pause execution until the chamber reaches its target temperature.

        Args:
            delay (int): ?
            timeout (int): ?

        Returns:
            float: status
        """
        return self.qdi_instrument.WaitFor(True, False, False, False, delay, timeout)

    def getField(self):
        """Get the current magnetic field in gauss.

        Returns:
            float: current magnetic field in gauss
        """
        return self.qdi_instrument.GetField(0, 0)

    def setField(self, field, rate=200):
        """Set a target magnetic field and sweep rate.

        Args:
            field (int): target magnetic field in gauss
            rate (int): field sweep rate in gauss / second

        Returns:
            float: status
        """
        return self.qdi_instrument.SetField(field, rate, 0, 0)

    def waitForField(self, delay=5, timeout=600):
        """Pause execution until the chamber reaches its target field.

        Args:
            delay (int): ?
            timeout (int): ?

        Returns:
            float: status
        """
        return self.qdi_instrument.WaitFor(False, True, False, False, delay, timeout)
