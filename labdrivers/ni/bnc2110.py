import ctypes
import numpy as np

import PyDAQmx
from PyDAQmx import Task

class bnc2110:
    """Class to interface with a National Instruments BNC-2110 DAC
    
    Built on top of PyDAQmx. 
    
    For task.<function> call signature explanations see:
        All Programs -> National Instruments -> NI-DAQ -> Text-based Code Support
                     -> NI-DAQmx C Reference Help
        
        """
    
    def __init__(self, device='Dev1'):
        self.device = device
        
        
    def reset(self):
        """Reset the device. Equivalent to <R click> -> Reset in NI MAX"""
        PyDAQmx.DAQmxResetDevice(self.device)
    
    
    def setOutput(self, channel='ao1', output=0):
        """Set the output level of `channel` to `output`
        
        Args:
            channel(str): the name of the channel to use
            output(float): the value to output"""
        
        task = Task()

        # from NI-DAQmx C Reference:
        # int32 DAQmxCreateAOVoltageChan (TaskHandle taskHandle, 
        #                                 const char physicalChannel[], 
        #                                 const char nameToAssignToChannel[], 
        #                                 float64 minVal, 
        #                                 float64 maxVal, 
        #                                 int32 units, 
        #                                 const char customScaleName[]);
        task.CreateAOVoltageChan('/{}/{}'.format(self.device, channel),
                                 '',
                                 -10.0,
                                 10.0,
                                 PyDAQmx.DAQmx_Val_Volts,
                                 None)

        task.StartTask()
        # from NI-DAQmx C Reference:
        # int32 DAQmxWriteAnalogScalarF64 (TaskHandle taskHandle, 
        #                                  bool32 autoStart, 
        #                                  float64 timeout, 
        #                                  float64 value, 
        #                                  bool32 *reserved); 
        task.WriteAnalogScalarF64(1,
                                  10.0,
                                  output,
                                  None)
        task.StopTask()
        
        
    def readInput(self, channel='ai1', minVal=-10.0, maxVal=10.0):
        """Read the input level of `channel`
        
        Using narrow bounds (with minVal and maxVal) will improve accuracy
        since the same digital resolution will be applied to a smaller
        analog range.
        
        Args:
            channel(str): the name of the channel to use
            minVal(float): the minimum value you expect to measure
            maxVal(float): the maximum value you expect to measure"""
        
        task = Task()
        measured_point = ctypes.c_double(0)
        
        # from NI-DAQmx C Reference:
        # int32 DAQmxCreateAIVoltageChan (TaskHandle taskHandle, 
        #                                 const char physicalChannel[], 
        #                                 const char nameToAssignToChannel[], 
        #                                 int32 terminalConfig, 
        #                                 float64 minVal, 
        #                                 float64 maxVal, 
        #                                 int32 units, 
        #                                 const char customScaleName[]);
        task.CreateAIVoltageChan('/{}/{}'.format(self.device, channel),
                                 '',
                                 PyDAQmx.DAQmx_Val_Cfg_Default,
                                 minVal,
                                 maxVal,
                                 PyDAQmx.DAQmx_Val_Volts,
                                 None)


        task.StartTask()
        # from NI-DAQmx C Reference:
        # int32 DAQmxReadAnalogScalarF64 (TaskHandle taskHandle, 
        #                                 float64 timeout, 
        #                                 float64 *value, 
        #                                 bool32 *reserved);
        task.ReadAnalogScalarF64(1.0,
                                 ctypes.POINTER(ctypes.c_double)(measured_point),
                                 None)
        
        # see http://stackoverflow.com/questions/1413851/expected-lp-c-double-instance-instead-of-c-double-array-python-ctypes-error
        # for an explanation of the POINTER black magic
        
        task.StopTask()

        return measured_point.value
