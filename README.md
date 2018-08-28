[![Documentation Status](https://readthedocs.org/projects/labdrivers/badge/?version=latest)](http://labdrivers.readthedocs.org/en/latest/?badge=latest)

## labdrivers

labdrivers is a Python module containing a collection of drivers for common research lab instruments.

It contains a suite of instrument-specific drivers which can be used to 
interface measurement hardware with Python code, along with a set of 
Jupyter notebooks demonstrating example use cases.
The drivers within the project are intended to be used 'manually', either in python scripts or
in Jupyter notebooks.

labdrivers is not a measurement framework with a GUI; if that's what you're looking
for then you might want to check out one of the projects listed at
[https://github.com/pyinstruments/pyinstruments](https://github.com/pyinstruments/pyinstruments).

### Documentation

For examples of how to use the drivers please see the Jupyter notebooks in the `example_nbs` folder.

For the full driver API documentation, along with a description of the design decisions underlying 
the driver implementations please see the full documentation at 
[labdrivers.readthedocs.org](https://labdrivers.readthedocs.org).


### Installation

You may install using:

`pip install labdrivers`

The latest version will only install `pyvisa` and `PyDAQmx` if they are not already installed.
However, `pythonnet` is necessary for the Quantum Design Dynacool class to work. Keep in mind that
.NET 4.0+ **must** be installed. The dependency on Cython (CPython?) is being investigated and
the `labdrivers` package will be updated as soon as more is known. This is not to say that the
Quantum Design package cannot be used; manual installation of `pythonnet` and its dependencies 
must be performed by the user.

### Contributing new drivers

Pull requests with new drivers are welcome! 

For a list of coding conventions used within `labdrivers`, along with some
guiding design principles please see [here](http://labdrivers.readthedocs.org/en/latest/contributing.html).

Also, Before submitting a request please
make sure your code follows the PEP8 Python style guidelines (except for the
one concerning maximum line length. 
