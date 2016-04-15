"""Module containing a class to interface with a QuantumDesign PPMS DynaCool

This module provides a python wrapper to the C# .dll provided by QuantumDesign.
Importing the C# .dll requirest the python module 'pythonnet'.

Attributes:
    logger: a python logger object


Classes:
    Dynacool: a class for interfacing with a QuantumDesign PPMS DynaCool

"""

# requires Python for .NET
# can be installed with 'pip install pythonnet'
import clr

# load the C# .dll supplied by Quantum Design
try:
    clr.AddReference('QDInstrument')
except:
    if clr.FindAssembly('QDInstrument') is None:
        print('Could not find QDInstrument.dll')
    else:
        print('Found QDInstrument.dll at {}'.format(clr.FindAssembly('QDInstrument')))
        print('Try right-clicking the .dll, selecting "Properties", and then clicking "Unblock"')

# import the C# classes for interfacing with the PPMS
from QuantumDesign.QDInstrument import QDInstrumentBase, QDInstrumentFactory


QDI_DYNACOOL_TYPE = QDInstrumentBase.QDInstrumentType.DynaCool
DEFAULT_PORT = 11000


class Dynacool:
    """Thin wrapper around the QuantumDesign.QDInstrument.QDInstrumentBase class"""

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
            rate (int): the sweep rate in Kevlin / minute

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
