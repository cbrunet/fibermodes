# fibermodes
Multilayers fiber mode solver

[![Build Status](https://travis-ci.org/cbrunet/fibermodes.svg?branch=master)](https://travis-ci.org/cbrunet/fibermodes)

API documentation available on http://fibermodes.rtfd.org/


Installation
============

Requirements:

- Python >= 3.4
- numpy
- scipy

For GUI:

 - pyside
 - pyqtgraph


General installation
--------------------

1. Install required environment. For Windows, see below.
   For Linux, it depends on your distribution, but installing python
   (version 3.4 or higher),
   numpy, scipy, pyside, and pyqtgraph should be sufficient.
   For Mac OS, should be similar, but I haven't tested.
2. python setup.py install


Running tests
-------------

You need `nose`. Then, can ca either run `nosetests` or `python setup.py nosetests`.


Building documentation
----------------------

You need sphinx (and probably a few dependencies to be documented).

``
python setup.py build_sphinx
``

Documentation is generated under `doc/_build/html`.


Windows installation
--------------------

At the time of writing, python 3.4 (32 bits) is required to install binary version of PySide. 

1. Install Anaconda 3.5, **32 bits edition**. It can be downloaded from https://www.continuum.io/downloads
2. In a command shell, type the following commands:

<pre>
    conda install python=3.4
    conda install numpy scipy
    pip install -U pyside
    pip install pyqtgraph
</pre>
