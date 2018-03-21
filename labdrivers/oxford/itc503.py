"""Module containing a class to interface with an Oxford Instruments ITC 503.

Note: Our (Mason Group) laboratory does not have a working motorized needle
        valve, so the gas functions are not totally useful. However, if
        it somehow is fixed or if someone not from the group decides to use
        this module, then it may be of use.

This module requires a National Instruments VISA driver, which can be found at
https://www.ni.com/visa/

Attributes:
    resource_manager: the pyvisa resource manager which provides the visa
                      objects used for communicating over the GPIB interface

    logger: a python logger object


Classes:
    itc503: a class for interfacing with a ITC 503 temperature controller

"""
import datetime as dt
import time
import logging

import visa
from pyvisa.errors import VisaIOError

# create a logger object for this module
logger = logging.getLogger(__name__)
# added so that log messages show up in Jupyter notebooks
logger.addHandler(logging.StreamHandler())

try:
    # the pyvisa manager we'll use to connect to the GPIB resources
    resource_manager = visa.ResourceManager()
except OSError:
    logger.exception("\n\tCould not find the VISA library. Is the National Instruments VISA driver installed?\n\n")


class itc503():
    
    def __init__(self, GPIBaddr=24):
        """Connect to an ITC 503 S at the specified GPIB address

        Args:
            GPIBaddr(int): GPIB address of the ITC 503 
        """
        self._visa_resource = resource_manager.open_resource("GPIB::%d" % GPIBaddr)
        self._visa_resource.read_termination = '\r'


    def setControl(self, state=3):
        """Set the LOCAL / REMOTE control state of the ITC 503

        0 - Local & Locked (default state)
        1 - Remote & Locked
        2 - Local & Unlocked
        3 - Remote & Unlocked
        
        Locked = Front panel is disabled
        Unlocked = Front panel usable

        Args:
            state(int): the state in which to place the ITC 503
        """
        assert type(state) == int, 'argument must be integer'
        assert state in [0,1,2,3], 'argument must be one of [0,1,2,3]'

        self._visa_resource.write("$C{}".format(state))


	def setTemperature(self, temperature=0.010):
		"""Change the temperature set point.
		
		Args:
			temperature(float): temperature to move to in Kelvin.
				Default: 0.010 K (10 mK) for default no heating
				above base temperature for any system.
		"""
		assert type(temperature) in [int, float], 'argument must be a number'
		
		command = '$T' + str(int(1000*temperature))
		self._visa_resource.write(command)
	
		
    def getValue(self, variable=0):
        """Read the variable defined by the index.
        
        There are values 11-13 but generally useless for
        general use. These are omitted.
        
        0: SET TEMPERATURE           6: HEATER O/P (as V)
        1: SENSOR 1 TEMPERATURE      7: GAS FLOW O/P (a.u.)
        2: SENSOR 2 TEMPERATURE      8: PROPORTIONAL BAND
        3: SENSOR 3 TEMPERATURE      9: INTEGRAL ACTION TIME
        4: TEMPERATURE ERROR        10: DERIVATIVE ACTION TIME
        5: HEATER O/P (as %)
        
        Args:
            variable: Index of variable to read.
        """
        assert type(variable) == int, 'Argument must be an integer.'
        assert variable in range(0,11), 'Argument is not a valid number.'
        
        self._visa_resource.write('$R{}'.format(variable))
        self._visa_resource.wait_for_srq()
        value = self._visa_resource.read()
        
        return float(value.strip('R+'))
        
        
    def setProportional(self, prop=0):
        """Sets the proportional band.
        
        Args:
            prop: Proportional band, in steps of 0.0001K.
        """
        self._visa_resource.write('$P{}'.format(prop))
        return None
        
        
    def setIntegral(self, integral=0):
        """Sets the integral action time.
        
        Args:
            integral: Integral action time, in steps of 0.1 minute.
                        Ranges from 0 to 140 minutes.
        """
        self._visa_resource.write('$I{}'.format(integral))
        return None
        
        
    def setDerivative(self, derivative=0):
        """Sets the derivative action time.
        
        Args:
            derivative: Derivative action time.
                        Ranges from 0 to 273 minutes.
        """
        self._visa_resource.write('$D{}'.format(derivative))
        return None
        
        
    def setHeaterSensor(self, sensor=1):
        """Selects the heater sensor.
        
        Args:
            sensor: Should be 1, 2, or 3, corresponding to
                    the heater on the front panel.
        """
        
        assert sensor in [1,2,3], 'Heater not on list.'
        
        self._visa_resource.write('$H{}'.format(sensor))
        return None
        
    
    def setHeaterOutput(self, heater_output=0):
        """Sets the heater output level.
        
        Args:
            heater_output: Sets the percent of the maximum
                        heater output in units of 0.1%.
                        Min: 0. Max: 999.
        """
        
        self._visa_resource.write('$O{}'.format(heater_output))
        return None
        
        
    def setGasOutput(self, gas_output=0):
        """Sets the gas (needle valve) output level.
        
        Args:
            gas_output: Sets the percent of the maximum gas
                    output in units of 0.1%.
                    Min: 0. Max: 999.
        """
        self._visa_resource.write('$G{}'.format(gas_output))
        return None
        
        
    def setAutoControl(self, auto_manual=0):
        """Sets automatic control for heater/gas(needle valve).
        
        Value:Status map
            0: heater manual, gas manual
            1: heater auto  , gas manual
            2: heater manual, gas auto
            3: heater auto  , gas auto
        
        Args:
            auto_manual: Index for gas/manual.
        """
        self._visa_resource.write('$A{}'.format(automanual))