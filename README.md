# fibermodes
Multilayers fiber mode solver

[![Build Status](https://travis-ci.org/cbrunet/fibermodes.svg?branch=master)](https://travis-ci.org/cbrunet/fibermodes)
[![Coverage Status](https://coveralls.io/repos/cbrunet/fibermodes/badge.svg?branch=master&service=github)](https://coveralls.io/github/cbrunet/fibermodes?branch=master)

API documentation available on http://fibermodes.rtfd.org/


Installation
============

Requirements:

- Python >= 3.4
- numpy
- scipy

For GUI:

 - PyQt4
 - pyqtgraph

To run unit tests:

 - nose
 - coverage (for coverage tests)


This software is still under heavy development. Therefore, it is recommended to
install it in a development environment, to be able to quickly pull newest changes
from the GitHub repository, and to be able to propose pull requests. However,
we also describe a *simple* installation, in case you only want to run  the 
software, without hacking it.


Installing the required environment
-----------------------------------

### For Linux

On **Ubuntu** / **Debian**, install the following packages:
`python3`, `python3-numpy`, `python3-scipy`, `python3-pyqt4`, `python3-pyqtgraph`,
`python3-nose`, `python3-coverage`.

On **Arch**, the required packages are:
`python`, `python-numpy`, `python-scipy`, `python-pyqt4`, `python-nose`,
`python-coverage`, `python-pip`.


### For Windows

I recommend to use a distribution that includes scientific Python.
Choose a distribution that includes Python 3.4 or higher. I recommend
using either
[WinPython](http://winpython.github.io/) or
[Anaconda](https://www.continuum.io/downloads).
Follow the installation instructions, and everything should work out-of-the-box.


### For Mac OS

I do not have a machine to test installation on Mac OS. However, it *should* work.
Please fell free to share me your experience.


*Simple* installation
---------------------

This is not the recommended way. You should consider *development* installation
instead. However, this is the simplest installation, as it does not require `git`.

1. Download the [ZIP archive from GitHub](https://github.com/cbrunet/fibermodes).
2. Unzip it!
3. On a command line, go inside the `fibermodes` directory.
4. Run `python setup.py install`

The command on line 4 may vary.
For instance, it should be `sudo python3 setup.py install` on Ubuntu / Debian.


Development installation
------------------------

The first step is to install `git`. For Linux, the package should be called `git`.
For Windows, it is a little more complicated. I recommend using
[Git for Windows](https://git-for-windows.github.io/). Follow the installation
instructions from their page.
You could also install [GitHub Desktop](https://desktop.github.com/) instead.

The second step is to create a GitHub account, if you do not already have one.
Then you should configure you machine with ssh keys, and configure your name
and email for git.

The third step is to fork and clone the
[fibermodes repository](https://github.com/cbrunet/fibermodes).
I recommend forking it first, as it will allow you to commit your changes
on GitHub, and to suggest pull requests.

Then you should install the software in `develop` mode. This is similar
to `install`, but it uses links instead of moving the files. Therefore, you
do not need to reinstall each time you pull changes from GitHub.
The command is: `python setup.py develop`. You may need to use `python3`
instead of `python` if you are on Ubuntu / Debian, and you may need to use
`sudo` to run this command.


Running tests
-------------

To ensure you have all the required dependencies to run tests, you can
do, from the `fibermodes` directory: `pip install .[test]`.

Then, you can either run `nosetests` or `python setup.py nosetests`.


Building documentation
----------------------

You need sphinx (and probably a few dependencies to be documented).

``
python setup.py build_sphinx
``

Documentation is generated under `doc/_build/html`.


