import logging

log = logging.getLogger(__name__)
log.addHandler(log.StreamHandler())

import clr

try:
    # load the C# .dll supplied by Quantum Design
    clr.AddReference('QDInstrument')

    # import the C# classes for interfacing with the PPMS
    from QuantumDesign.QDInstrument import QDInstrumentBase, QDInstrumentFactory

    # TODO: Casting (QDInstrumentBase.QDInstrumentType) 4121982, which refers
    # to the MPMS

    # TODO: Obtain the QdInstrumentBase.QDInstrumentType enum
    # and observe how it manifests in Python...could give a hint


    QDINSTRUMENT_TYPE = {'DynaCool': QDInstrumentBase.QDInstrumentType.DynaCool,
                            'PPMS': QDInstrumentBase.QDInstrumentType.PPMS,
                            'SVSM': QDInstrumentBase.QDInstrumentType.SVSM,
                            'VersaLab': QDInstrumentBase.QDInstrumentType.VersaLab}
    DEFAULT_PORT = 11000
except:
    if clr.FindAssembly('QDInstrument') is None:
        logger.exception('\n\tCould not find QDInstrument.dll')
    else:
        logger.exception('\n\tFound QDInstrument.dll at {}'.format(clr.FindAssembly('QDInstrument')))
        logger.exception('\n\tTry right-clicking the .dll, selecting "Properties", and then clicking "Unblock"')

class QDInstrument:
    """A general class to interface between a Quantum Design instrument and a computer.
    
    Currently supports the PPMS, PPMS DynaCool, VersaLab, and SVSM.
    
    Testing must still be done for the MPMS."""
    def __init__(self, instrument_type):
        if instrument_type in QDINSTRUMENT_TYPE.keys():
            instrument = QDInstrumentFactory.GetQDInstrument(
                QDINSTRUMENT_TYPE[instrument_type], remote, ip_address, DEFAULT_PORT)
        else:
            raise RuntimeError("Instrument given is not supported or non-existent."
                                + "Check that you are using one of the following: [DynaCool|PPMS|SVSM|VersaLab]")
        
    def getTemperature(self):
        """Obtains the temperature reading in Kelvin."""
