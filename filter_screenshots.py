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

import math
import numpy as np
import ntpath
from scipy import misc, ndimage

from model.perceptual_model import display_center, ObserverSpecification, \
    DEFAULT_FOVEAL_RESOLUTION, make_perpendicular_display
from util import filter_image


if __name__ == '__main__':
    IMAGE_FILE = './image.png'
    OUT_FILE_PATTERN = '{}.png'

    image = ndimage.imread(IMAGE_FILE)

    observer_pos = np.array([0, 0, 0])
    DISTANCE = 0.4
    DISPLAY_SIZE = 0.02, 0.02
    DISPLAY_RESOLUTION = 200, 200
    h_angle, v_angle = 10, 20

    display = make_perpendicular_display(DISPLAY_SIZE[0],
                                         DISPLAY_SIZE[1],
                                         DISTANCE,
                                         math.radians(h_angle), math.radians(v_angle),
                                         DISPLAY_RESOLUTION[0],
                                         DISPLAY_RESOLUTION[1])

    observer_display_dir = display_center(display) - observer_pos
    observer_direct = ObserverSpecification(observer_pos, observer_display_dir, DEFAULT_FOVEAL_RESOLUTION)

    out_path = OUT_FILE_PATTERN.format("direct")
    if ntpath.exists(out_path):
        print('Skipped image')
    else:
        out_image = filter_image(image, display, observer_direct)
        misc.imsave(out_path, out_image[0])
        print('Saved image', out_path)

    observer_forward_dir = np.array([0, 1, 0])
    observer_forward = ObserverSpecification(observer_pos, observer_forward_dir, DEFAULT_FOVEAL_RESOLUTION)

    out_path = OUT_FILE_PATTERN.format("indirect")
    if ntpath.exists(out_path):
        print('Skipped image')
    else:
        out_image = filter_image(image, display, observer_forward)
        misc.imsave(out_path, out_image[0])
        print('Saved image', out_path)
