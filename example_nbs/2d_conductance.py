'''
TODO:

- Set up program to allow for mid-experiment parameter changes
- Send a pull request to have the option of not resetting K2400
'''

# database manipulation/operations
import pandas as pd
import numpy as np

# data plotting
import matplotlib.pyplot as plt
import seaborn as sns

# import drivers for experiment
from labdrivers.ni import bnc2110
from labdrivers.keithley import keithley2400
from labdrivers.srs import sr830

# experimental constants
current_preamp_sensitivity = -7
lockin_voltage_amplitude = 0.100
ac_division = 1.0
dc_division = 1.0
single_mode_conductance = 0.000077480917310 # in Siemens/inverse Ohms

# set up instrument channels
daq_output_channel = 'ao1'
keithley_gpib_channel = 23
lockin_gpib_channel = 8

# initialize DAQ, K2400, SR830
daq = bnc2110()
keithley = keithley2400(keithley_gpib_channel)
lockin = sr830(lockin_gpib_channel)

# scanning parameters
gate_min = -10.0
gate_max = 10.0
gate_step = 0.1
bias_min = -5.0
bias_max = 5.0
bias_step = 0.1

# establish the range lists
gate_voltages = range(gate_min, gate_max + gate_step,
						gate_step)
bias_voltages = range(bias_min, bias_max + bias_step,
						bias_step)

# setting up data and meta-data
columns = ['Gate Voltage (V)','Bias Voltage (mV)','dI/dV (2e^2/h)']
experimental_data = pd.DataFrame(columns=columns)

# helper function to calculate differential conductance
def get_diff_conductance(lockin_output):
	
	current = lockin_output * 10 ** current_preamp_sensitivity
	input_voltage = lockin.getAmplitude() / ac_division
	
	return current / input_voltage

# experimental loops
for gate in gate_voltages:
	
	keithley.setSourceDC(source='voltage', value=gate)
	
	for bias in bias_voltages:
	
		daq.setVoltageOutput(channel=daq_output_channel)
		lockin_reading = daq.getSinglePoint(1)
		data_to_append = [gate, bias / dc_division,
								get_diff_conductance(lockin_reading)]
		
		data_to_append = pd.DataFrame(data_to_append,
										columns=columns)
		experimental_data.append(data_to_append,
								ignore_index=True)