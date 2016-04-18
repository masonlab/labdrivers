Welcome to labdrivers' documentation!
======================================

labdrivers is a Python module containing a collection of drivers for common research lab instruments.

It contains a suite of instrument-specific drivers which can be used to 
interface measurement hardware with Python code, along with a set of 
Jupyter notebooks demonstrating example use cases.
The drivers within the project are intended to be used 'manually', either in python scripts or in Jupyter notebooks.

Labdrivers is not a measurement framework with a GUI; if that's what you're looking for 
then you might want to check out one of the projects listed at https://github.com/pyinstruments/pyinstruments.

Organization of the project
----------------------------

Drivers within the project are organized by instrument brand. Each
instrument manufacturer has its own submodule under the :code:`labdrivers` namespace, and
each individual instrument driver is in a file named after the class which
implements the driver.

Currently labdrivers contains drivers for the following instruments::

	labdrivers/
	|-- keithley
	    `-- keithley2400.py
	|-- quantumdesign
	    `-- dynacool.py
	|-- srs
	    `-- sr830.py

So for example, to load the driver for a Keithley 2400 SMU::

    from labdrivers.keithley import keithley2400


Documentation Table of Contents
-------------------------------

.. toctree::
   :maxdepth: 4

   installation
   usage
   moduleapis
   contributing
