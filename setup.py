#!/usr/bin/env python3

"""
This file is part of the perception model tool.

The perception model tool is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

The perception model tool is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with the perception model tool.  If not, see <http://www.gnu.org/licenses/>.
"""

from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='perception-model',
      version='1.0',
      description='Perception Model',
      long_description=long_description,
      long_description_content_type='text/markdown',
      author='Michael Mauderer, Frederic Kerber',
      author_email='fkerber@gmail.com',
      url='https://github.com/fkerber/perception-model-tool',
      license='GNU Lesser General Public License v3.0',
      entry_points={
      'console_scripts': [
                          'filter_screenshot=scripts.filter_screenshot:main',
                          ],
      'gui_scripts': [
                      'filter_screenshot_gui=scripts.filter_screenshot_gui:main',
                          ],
      },
      packages=['perceptual_model', 'scripts'],
      install_requires=['numpy','scipy', 'colour-science', 'click'],
      python_requires='>=3',
     )
