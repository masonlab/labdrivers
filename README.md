## labdrivers

labdrivers is a Python module containing a collection of drivers for common research lab instruments.

It contains a suite of instrument-specific drivers which can be used to 
interface measurement hardware with Python code, along with a set of 
Jupyter notebooks demonstrating example use cases.
These drivers are aimed at users who need to iteratively modify their experimental setup:
the drivers within the project are intended to be used in python scripts --
labdrivers is not a measurement framework with a GUI. 

Each driver is implemented as a class, named after the instrument with which it 
communicates.

### Organization of the project

Drivers within the project are organized by instrument brand. Each
instrument manufacturer has its own submodule under the `labdrivers` namespace, and
each individual instrument driver is in a file named after the class which
implements the driver.

Currently labdrivers contains drivers for the following instruments:

	labdrivers/
	|-- keithley
	    `-- keithley2400.py
	|-- quantumdesign
	    `-- dynacool.py
	|-- srs
	    `-- sr830.py

So for example, to load the driver for a Keithley 2400 SMU,

    from labdrivers.keithley.keithley2400 import Keithley2400


### Driver API design

Each driver is implemented as a class named after the corresponding instrument.
Each class contains the broadest subset of the following components
which makes sense for the given instrument type:

- a `read_point()` method which reads a single point using the current
instrument configuration
- a set of `get_<parameter>` and `set_<parameter>` methods which
query and specify the instrument configuration, respectively
- a pandas DataFrame which stores data collected by the instrument

The driver classes are intended to be used directly (for example, as part
of a Jupyter notebook-based workflow), therefore simplicity is prioritized
over completeness.

#### Minimize the amount of 'internal state' maintained by the driver

Wherever possible, implement methods which query the instrument about
its status instead of attributes which track the instrument's status
within the driver class.

E.g. do this:

    def get_output(self):
        ...
        return instrument.query("OUTPUT?")

instead of this:

    # is updated by self.set_output to keep track of the output 
    self.output = ('voltage', 0.05)

#### Limit the number of `get_<parameter>` and `set_<parameter>` methods.

For instrument parameters which take a finite set of categorical variables 
(for example the output of a digital multimeter, which can be set to source
either current or voltage) create a single function that takes the 
categorical variable as its first argument.

E.g. do this:

    def set_output(self, source_type, source_level):
        ...

instead of this:

    def set_output_voltage(self, source_level):
        ...

    def set_output_current(self, source_level):
        ...

### Contributing new drivers

Pull requests with new drivers are welcome! 

Before submitting a request please
make sure your code follows the PEP8 Python style guidelines (except for the
one concerning maximum line length. 
