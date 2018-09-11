# Changelog

If you don't want to try and figure out all the changes from the diff and commits,
just read this. I wrote this to make the changes more robust.

## 0.9.6: Keithley read changes

- Keithley 2400s should be able to properly read out what they're supposed to.
  The Keithley2400.read() function takes a variable number of arguments that are
  in the list: 'voltage', 'current', 'resistance', 'time'. The internal workings
  assume that the function returns a list which has a length which is some
  multiple of 5. Keithley2400.read() returns a tuple of lists, the first element
  in the tuple being the mean values of the requested values to be read, the second
  being the standard deviation (if there are multiple readings in the buffer).

## 0.9.5: Quantum Design package major update

- New classes for PPMS, (PPMS) DynaCool, VersaLab, SVSM, and MPMS. The Dynacool class
  is just a rework of the old Dynacool class, but this time inherits from a general
  QdInstrument parent class. __init__.py has been updated for imports.
- There are two new functions so that users can interface with the rotator module. A
  user should be able to get and set the position of the rotator now. However, it
  should be noted that this still requires testing (!!!).
- Housekeeping: Lots of changes to whitespace/blank line issues in the SR830 package.
  Went ahead and cleaned up formatting issues in many other packages as well.
- More housekeeping: Removed old, unused import statements.
- Changed Nidaq output functions to the old form so that they take both the channel
  and the output value. It seemed extremely unwieldy to individually set the channel
  "state" and then write the output.
- Implemented some `RuntimeWarning`s if a user didn't receive a response from the Mercury
  iPS. The response is an acknowledgment that a command was received. Some functions
  have a `RuntimeError` if it's a function that deals with the limits of the magnet (e.g.
  making sure that the magnet doesn't go to 20 T!!!).
- Added some more instructions on usage in the README.md

#### Proposed changes

- For equipment that do not use cryogenics or vacuum pumps (e.g. NOT the Oxford Triton
  200 or the Mercury iPS), the unit tests should ensure that what is being read out
  are the types that are expected (e.g. you expect floats from a resistance reading or
  an integer from the state of the lock-in sensitivity). Set functions could have a
  test where a query is made to see if the set function set what you expected.

## 0.9.1

- Started keeping a changelog to communicate changes with a wider audience
- Class names are now CamelCase and start with a capital letter
- Took out enable/disable_remote functions in Sr830 and Keithley2400 because they just
  felt unnecessary. The instruments are now opened upon instantiation.

#### Proposed changes

- Quantum Design has a few other instruments such as a regular PPMS,
  an MPMS, and a VersaLab (whatever those are). The decompiled DLL
  file is actually really easy to read and interpret, so a future
  version of 0.9 should be seeing implementations of those.
