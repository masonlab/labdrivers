import ctypes

import PyDAQmx
from PyDAQmx import Task


class Nidaq:
    """Class to interface with a National Instruments DAQ
    
    Built on top of PyDAQmx. 
    
    Reference: NI-DAQmx C Reference Help
    """
    
    def __init__(self, device='Dev1'):
        self.device = device
        self._channel = None

    def reset(self):
        """Reset the device. Equivalent to <R click> -> Reset in NI MAX"""
        PyDAQmx.DAQmxResetDevice(self.device)
    
    def output_voltage(self, channel, output=0):
        """Outputs a voltage from the NI DAQ.

        :param channel: The name of the channel for output.
        :param output: The value of the output in Volts
        :return: None
        """
        
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
        
    def output_current(self, channel, output=0):
        """Outputs a current from the NI DAQ.

        :param channel: The name of the channel for output.
        :param output: The value of the output in Amps
        :return: None
        """
        
        task = Task()

        # from NI-DAQmx C Reference:
        # int32 DAQmxCreateAOCurrentChan (TaskHandle taskHandle, 
        #                                 const char physicalChannel[],
        #                                 const char nameToAssignToChannel[], 
        #                                 float64 minVal, 
        #                                 float64 maxVal, 
        #                                 int32 units, 
        #                                 const char customScaleName[]);
        task.CreateAOCurrentChan('/{}/{}'.format(self.device, channel),
                                 '',
                                 -10.0,
                                 10.0,
                                 PyDAQmx.DAQmx_Val_Amps,
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

    def read_voltage(self, channel, minVal=-10.0, maxVal=10.0):
        """Read the voltage input level of `channel`
        
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

    def read_current(self, channel, minVal=-10.0, maxVal=10.0):
        """Read the current input level of `channel`
        
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
        # int32 DAQmxCreateAICurrentChan (TaskHandle taskHandle, 
        #                                 const char physicalChannel[],
        #                                 const char nameToAssignToChannel[],
        #                                 int32 terminalConfig, 
        #                                 float64 minVal, 
        #                                 float64 maxVal, 
        #                                 int32 units, 
        #                                 int32 shuntResistorLoc, 
        #                                 float64 extShuntResistorVal, 
        #                                 const char customScaleName[]);
        task.CreateAICurrentChan('/{}/{}'.format(self.device, channel),
                                 '',
                                 PyDAQmx.DAQmx_Val_Cfg_Default,
                                 minVal,
                                 maxVal,
                                 PyDAQmx.DAQmx_Val_Amps,
                                 PyDAQmx.DAQmx_Val_Default,
                                 1.0,
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
