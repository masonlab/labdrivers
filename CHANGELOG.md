# Changelog

## 0.9.1

- Started keeping a changelog to communicate changes with a wider
  audience (besides myself)
- Class names are now CamelCase and start with a capital letter
- Took out enable/disable_remote functions in Sr830 and Keithley2400
  because they just felt unnecessary. The instruments are now opened
  upon instantiation.

### To be implemented

- Quantum Design has a few other instruments such as a regular PPMS,
  an MPMS, and a VersaLab (whatever those are). The decompiled DLL
  file is actually really easy to read and interpret, so a future
  version of 0.9 should be seeing implementations of those. 
