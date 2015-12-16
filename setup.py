#!/usr/bin/env python3

# This file is part of FiberModes.
#
# FiberModes is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# FiberModes is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with FiberModes.  If not, see <http://www.gnu.org/licenses/>.

import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages


setup(name='fibermodes',
      version='0.2.0',
      description='Multilayers optical fiber mode solver',
      author='Charles Brunet',
      author_email='charles@cbrunet.net',
      url='https://github.com/cbrunet/fibermodes',
      packages=find_packages(exclude=['plots', 'scripts', 'tests']),
      include_package_data=True,
      entry_points={
        'gui_scripts': [
            'fibereditor = fibermodesgui.fibereditorapp:main',
            'materialcalculator = fibermodesgui.materialcalculator:main',
            'modesolver = fibermodesgui.modesolverapp:main',
            'wavelengthcalculator = fibermodesgui.wavelengthcalculator:main'
        ]
      },
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: X11 Applications :: Qt',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Telecommunications Industry',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Scientific/Engineering :: Physics'],
      install_requires=[
        'numpy >= 1.9.0',
        'scipy >= 0.15.0',
        'pyqtgraph >= 0.9.10',
        # 'PyQt4 >= 4.11'  # see http://stackoverflow.com/questions/4628519/is-it-possible-to-require-pyqt-from-setuptools-setup-py
      ],
      extras_require={
        'test': ['nose >= 1.3.2', 'coverage >= 3.7']
      }
      )
