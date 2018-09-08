import logging

import clr

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())

# load the C# .dll supplied by Quantum Design
clr.AddReference('QDInstrument')

if clr.FindAssembly('QDInstrument') is None:
    logger.exception('\n\tCould not find QDInstrument.dll')
else:
    logger.exception('\n\tFound QDInstrument.dll at {}'.format(clr.FindAssembly('QDInstrument')))
    logger.exception('\n\tTry right-clicking the .dll, selecting "Properties", and then clicking "Unblock"')

# import the C# classes for interfacing with the PPMS
from QuantumDesign.QDInstrument import QDInstrumentBase, QDInstrumentFactory

QDINSTRUMENT_TYPE = {'DynaCool': QDInstrumentBase.QDInstrumentType.DynaCool,
                     'PPMS': QDInstrumentBase.QDInstrumentType.PPMS,
                     'SVSM': QDInstrumentBase.QDInstrumentType.SVSM,
                     'VersaLab': QDInstrumentBase.QDInstrumentType.VersaLab,
                     'MPMS': 4121982}
DEFAULT_PORT = 11000


class QdInstrument:
    """A class to interface with Quantum Design instruments.

    This class is a thin wrapper around the C# QuantumDesign.QDInstrument.QDInstrumentBase class
    provided in the QDInstrument.dll file.

    There is now support for using a Quantum Design DynaCool, PPMS, SVSM, and VersaLab. The MPMS
    class requires testing, but should work. For some reason, the MPMS enum was hard-coded in
    as the number 4121982 casted as a QDInstrumentBase.QDInstrumentType enum.
    """

    def __init__(self, instrument_type, ip_address, remote=True):
        self.qdi_instrument = QDInstrumentFactory.GetQDInstrument(
            QDINSTRUMENT_TYPE[instrument_type], remote, ip_address, DEFAULT_PORT)

    def getTemperature(self):
        """Returns the instrument temperature in Kelvin.

        Parameters are from:
        SetTemperature(double Temperature, double Rate, QDInstrumentBase.TemperatureApproach Approach)
        """
        return self.qdi_instrument.GetTemperature(0, 0)

    def setTemperature(self, temp, rate=10):
        """Ramps the instrument temperature to the set point.

        Parameters are from:
        GetTemperature(ref double Temperature, ref QDInstrumentBase.TemperatureStatus Status)

        :param temp: Desired temperature in Kelvin
        :param rate: Temperature ramp rate in Kelvin/min.
        :return: None
        """
        if 0 <= temp <= 400:
            return self.qdi_instrument.SetTemperature(temp, rate, 0)
        else:
            raise RuntimeError("Temperature is out of bounds. Should be between 0 and 400 K")

    def waitForTemperature(self, delay=5, timeout=600):
        """
        Prevents other processes from executing while the QD instrument temperature
        is settling down.

        :param delay: Length of time to wait after wait condition achieved in seconds.
        :param timeout: Length of time to wait to achieve wait condition in seconds.
        :return: 0 when complete.
        """
        return self.qdi_instrument.WaitFor(True, False, False, False, delay, timeout)

    def getField(self):
        """Returns the Magnetic field in Gauss.

        Parameters are from:
        GetField(ref double Field, ref QDInstrumentBase.FieldStatus Status)

        :return: Field in Gauss.
        """
        return self.qdi_instrument.GetField(0, 0)

    def setField(self, field, rate=200):
        """Ramps the instrument magnetic field to the set point.

        Parameters are from:
        SetField(double Field, double Rate, QDInstrumentBase.FieldApproach Approach, QDInstrumentBase.FieldMode Mode)

        :param field: Set point of the applied magnetic field in Gauss.
        :param rate:  Ramp rate of the applied magnetic field in Gauss/sec.
        :return: None
        """
        return self.qdi_instrument.SetField(field, rate, 0, 0)

    def waitForField(self, delay=5, timeout=600):
        """
        Prevents other processes from executing while the QD instrument magnetic field
        is settling down.

        :param delay: Length of time to wait after wait condition achieved in seconds.
        :param timeout: Length of time to wait to achieve wait condition in seconds.
        :return: 0 when complete.
        """
        return self.qdi_instrument.WaitFor(False, True, False, False, delay, timeout)

    def getPosition(self):
        """Retrieves the position of the rotator.

        GetPosition(string Axis, ref double Position, ref QDInstrumentBase.PositionStatus Status)

        "Horizontal Rotator" seems to be the name that one should pass to GetPosition, as
        observed in the WaitConditionReached function.
        """
        return self.qdi_instrument.GetPosition("Horizontal Rotator", 0, 0)

    def setPosition(self, position, speed):
        """Ramps the instrument position to the set point.

        Parameters are from:
        SetPosition(string Axis, double Position, double Speed, QDInstrumentBase.PositionMode Mode)

        :param position: Position on the rotator to move to.
        :param speed: Rate of change of position on the rotator.
        """
        return self.qdi_instrument.SetPosition("Horizontal Rotator", position, speed, 0)

    def waitForPosition(self, delay, timeout):
        """
        Prevents other processes from executing while the QD instrument rotator position
        is settling down.

        :param delay: Length of time to wait after wait condition achieved in seconds.
        :param timeout: Length of time to wait to achieve wait condition in seconds.
        :return: 0 when complete.
        """
        return self.qdi_instrument.WaitFor(False, False, True, False, delay, timeout)


class Dynacool(QdInstrument):
    """QdInstrument subclass that connects to the Quantum Design PPMS DynaCool."""
    def __init__(self, ip_address):
        super().__init__(instrument_type='DynaCool', ip_address=ip_address)


class Ppms(QdInstrument):
    """QdInstrument subclass that connects to the Quantum Design PPMS."""
    def __init__(self, ip_address):
        super().__init__(instrument_type='PPMS', ip_address=ip_address)


class Svsm(QdInstrument):
    """QdInstrument subclass that connects to the Quantum Design SVSM."""
    def __init__(self, ip_address):
        super().__init__(instrument_type='SVSM', ip_address=ip_address)


class VersaLab(QdInstrument):
    """QdInstrument subclass that connects to the Quantum Design VersaLab."""
    def __init__(self, ip_address):
        super().__init__(instrument_type='VersaLab', ip_address=ip_address)


class Mpms(QdInstrument):
    """QdInstrument subclass that connects to the Quantum Design MPMS."""
    def __init__(self, ip_address):
        super().__init__(instrument_type='MPMS', ip_address=ip_address)
