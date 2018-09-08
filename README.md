[![Documentation Status](https://readthedocs.org/projects/labdrivers/badge/?version=latest)](http://labdrivers.readthedocs.org/en/latest/?badge=latest)

## labdrivers

labdrivers is a Python module containing a collection of drivers for common research lab instruments.

It contains a suite of instrument-specific drivers which can be used to interface measurement hardware with Python code,
along with a set of Jupyter notebooks demonstrating example use cases. The drivers within the project are intended to
be used 'manually', either in python scripts or in Jupyter notebooks.

`labdrivers` is not a measurement framework with a GUI; if that's what you're looking
for then you might want to check out one of the projects listed at
[https://github.com/pyinstruments/pyinstruments](https://github.com/pyinstruments/pyinstruments).

### Usage

The package structure is as follows (with the __init__.py omitted):

	labdrivers/
	|-- keithley
	    `-- keithley2400.py
	|-- lakeshore
	    `-- ls332.py
	|-- ni
	    `-- nidaq.py
	|-- oxford
	    |-- itc503.py
	    |-- ips120.py
		|-- mercuryips.py
		`-- triton200.py
	|-- quantumdesign
	    `-- qdinstrument.py
	|-- srs
	    `-- sr830.py

As an example, you can connect to a Mercury iPS magnet:

```python
from labdrivers.oxford import MercuryIps

mercury_ps = MercuryIps(mode='ip', ip_address='123.456.789.0')
```

Several of the packages exploit the property and setter decorators to query the state of
the equipment or to set the state of the machine. Of course, not everything can be
considered an attribute of the system, so functions can and do exist, as shown below:

```python
# Internally, these query the Mercury iPS and receive a response
mercury_ps.x_magnet.field_setpoint = 1.0
mercury_ps.x_magnet.field_ramp_rate = 0.05

# These are functions that work in the usual way
if mercury_ps.x_magnet.clamped():
    mercury_ps.x_magnet.hold()

mercury_ps.x_magnet.ramp_to_setpoint()

with open('test.txt', 'a') as f:
    # Note the use of an attribute. There are no opening and closing
    # parenthesis after magnetic_field. Writing a () after magnetic_field
    # would give a TypeError.
    f.write('{}\n'.format(mercury_ps.x_magnet.magnetic_field))
```

You should look through the documentation or the source code itself in order to determine
the correct usage.

### Documentation

For examples of how to use the drivers please see the Jupyter notebooks in the `example_nbs` folder.

For the full driver API documentation, along with a description of the design decisions underlying 
the driver implementations please see the full documentation at 
[labdrivers.readthedocs.org](https://labdrivers.readthedocs.org).

### Installation

You may install using:

`pip install labdrivers`

`pip` will also automatically install `pyvisa` and `PyDAQmx` if they are not already installed.

#### Using the Quantum Design instruments package

In order for `labdrivers` to read through the C# code of the Quantum Design DLL file, `pythonnet` is required.
In principle, `pythonnet` could be included in the pip-installation but there have been many issues with the
documentation not building and installation issues that have been traced back to installing this module.
Note that `pythonnet` is compatible with Python 3.6 at most (see its repository), and that it requires non-Python
dependencies like .NET 4.0+. As of writing this, it is not entirely clear what else is required,
though errors regarding Cython have been observed. It might not hurt to have other C/C++ related things installed,
like Visual Studio (if you're on Windows).

As the problems and solutions become clear, the documentation will be updated.

### Contributing new drivers

Pull requests with new drivers are welcome! 

For a list of coding conventions used within `labdrivers`, along with some
guiding design principles please see [here](http://labdrivers.readthedocs.org/en/latest/contributing.html).

Also, Before submitting a request please make sure your code follows the PEP8 Python style guidelines (except for the
one concerning maximum line length. 
