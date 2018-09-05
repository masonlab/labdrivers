#########################
Contributing new drivers
#########################

Each driver is implemented as a class named after the corresponding instrument.
Each class contains the broadest subset of the following components
which makes sense for the given instrument type::

    - a read_point() method which reads a single point using the current instrument configuration

    - a set of get_<parameter> and set_<parameter> methods which query and specify the instrument configuration, respectively

    - a pandas DataFrame which stores data collected by the instrument

The driver classes are intended to be used directly (for example, as part
of a Jupyter notebook-based workflow), therefore simplicity is prioritized
over completeness.

^^^^^^^^^^^^^^^^^^
Coding conventions
^^^^^^^^^^^^^^^^^^

The drivers in the labdrivers package follow the following conventions:

- Class names are all CamcelCase, e.g.::

    Keithley2400
    Sr830
    Dynacool

- Method names are in lower case (there are exceptions,
  like in the Quantum Design instruments classes), e.g.::

    measure_single_point
    auto_gain
    set_output_voltage


^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Driver design principles
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


- Minimize the amount of 'internal state' maintained by the driver

Wherever possible, implement methods which query the instrument about
its status instead of attributes which track the instrument's status
within the driver class.

E.g. do this::

    def getOutput(self):
        return self.instrument.query("OUTPUT?")

instead of this::

    def setOutput(self, out_type, level):
        self.instrument.write("OUTPUT {out_type} {level}".format(out_type, level))
        self.output = (out_type, level)

    def getOutput():
        return self.output


- Limit the number of :code:`get_<parameter>` and :code:`set_<parameter>` methods

For instrument parameters which take a finite set of categorical variables 
(for example the output of a digital multimeter, which can be set to source
either current or voltage) create a single function that takes the 
categorical variable as its first argument.

E.g. do this::

    def set_output(self, source_type, source_level):
        ...

instead of this::

    def set_output_voltage(self, source_level):
        ...

    def set_output_current(self, source_level):
        ...


^^^^^^^^^^^^^^^^^^^^^^^
Documenting drivers
^^^^^^^^^^^^^^^^^^^^^^^

Each method in the driver should be documented using a "`Google style <http://sphinxcontrib-napoleon.readthedocs.org/en/latest/example_google.html>`_"
docstring. Check the existing source code for examples.
