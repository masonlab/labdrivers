##############
Installation
##############

Before attempting to use the drivers for the Quantum Design instruments,
please be sure that you are using a version of Python which is 3.6.x
and below. Additionally, please be sure that .NET 4.0+ is installed,
as that allows for access to the classes within the compiled C# code.

There are a couple ways to install labdrivers.

Installing to the system Python Folder
--------------------------------------

To install labdrivers to the default Python installation you
can use `pip`::

    > pip install labdrivers

Note that this requires `git`, which can be found here: https://git-scm.com/. 

If you are running an outdated version of `labdrivers`, please upgrade::

    > pip install --upgrade labdrivers

If you prefer to install manually, download the labdrivers package from 
here: https://github.com/masonlab/labdrivers, then copy the `labdrivers` folder
to::

    (system python path)/lib/site-packages/