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

`pip` will also automatically install `pyvisa`, `PyDAQmx`, and `pythonnet` if they are not already installed. Installation of `pythonnet` is usually the failure point of this pip installation procedure, so it would be recommended to try installing that first to ensure that the rest of the installation will succeed. Note that `pythonnet` is compatible with Python 3.6 at most (see its repository), and that it requires non-Python
dependencies like .NET 4.0+. As of writing this, it is not entirely clear what else is required, though errors regarding Cython have been
observed. It might not hurt to have other C/C++ related things installed, like Visual Studio (if you're on Windows).

As the problems and solutions become clear, the documentation will be updated.

### Contributing new drivers

Pull requests with new drivers are welcome! 

For a list of coding conventions used within `labdrivers`, along with some
guiding design principles please see [here](http://labdrivers.readthedocs.org/en/latest/contributing.html).

Also, Before submitting a request please
make sure your code follows the PEP8 Python style guidelines (except for the
one concerning maximum line length. 
