# README #

### What is this repository for? ###

* Quick summary

This is a Python wrapper for the Avalanche Tcl API.
It is designed to provide the same Tcl API functionality for Python.
All commands and attributes should be identical to the Tcl API, but with a Python "flavor".
This functionality is enabled by placing a Python translation layer on top of the Tcl API. The Python translation layer converts the user's Python commands into their corresponding Tcl equivalent, and also converts the Tcl API response.

### How do I get set up? ###

The code is hosted here: 
    https://github.com/canadianjeans/avalanche

You can download a copy of the library directly:
    https://github.com/canadianjeans/avalanche/archive/master.zip

Or use PyPI:
    pip install avalancheapi

* Summary of set up
    PyPI should automatically install the module. However, if you download the Zip file, extract the archive in the desired location. You will need to point your Python script to this location.
        e.g. sys.path.append('/home/somebody/spirent/avalancheapi')       

* Dependencies
    OS:            Any OS supported by the Avalanche API
    Python:        2.7.x and 3.x 
    Tcl:           8.4 or 8.5.x (ActiveTcl is recommended)
    Tcl Libraries: msgcat, tcllib1.15+, tbcload and Tclx (not included)

### Who do I talk to? ###

Please contact Spirent support for any issues: support@spirent.com
