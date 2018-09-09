#########################
Contributing new drivers
#########################

Each driver is implemented as a class named after the corresponding instrument.
The driver classes are intended to be used directly and usable by anyone who decides to use
these for experiment.

^^^^^^^^^^^^^^^^^^
Coding conventions
^^^^^^^^^^^^^^^^^^

The modules in the `labdrivers` package follow the following conventions:

- Class names are all CamelCase, e.g.::

    Keithley2400
    Sr830
    Dynacool

- Method names are in lower case (there are exceptions,
  like in the Quantum Design instruments classes), e.g.::

    measure_single_point
    auto_gain
    set_output_voltage

Depending on the future of the use of the `labdrivers` package, the coding conventions may be revised
to maintain consistency.

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Driver design principles
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Minimize the amount of 'internal state' maintained by the driver

The only 'internal state' that an instance should keep are properties like an IP address
or a GPIB resource name. Most classes use the property decorator, but they are used only
to make a query and return the response directly to the user.

E.g. do this::

    def getOutput(self):
        return self.instrument.query("OUTPUT?")

instead of this::

    def setOutput(self, out_type, level):
        self.instrument.write("OUTPUT {out_type} {level}".format(out_type, level))
        self.output = (out_type, level)

    def getOutput():
        return self.output

- Use property decorators when possible to avoid writing getter and setter methods

- Use function names that are intuitive and minimize the amount of input required.

E.g. do this::

    def output_current(self, current):
        thing.output('current', current)

    def output_voltage(self, voltage):
        thing.output('voltage', voltage)

It might be more "efficient" to just allow for two inputs, but generally it would be less confusing
if there were only one input. This is a change from older versions of `labdrivers` (0.8.x and below?).

^^^^^^^^^^^^^^^^^^^^^^^
Documenting drivers
^^^^^^^^^^^^^^^^^^^^^^^

Each method in the driver should be documented using a the reStructuredText format.

Example::

    """
    First line of documentation.

    :param thing1: Description of thing1 parameter
    :param thing2: Description of thing2 parameter
    :returns: Description of the returned data
    :raises SomeError: Description of when SomeError shows up
    """

