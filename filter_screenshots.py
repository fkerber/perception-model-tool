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

import os
import math
import colour
import numpy as np
from scipy import misc, ndimage

from model.perceptual_model import display_center, ObserverSpecification, \
    DEFAULT_FOVEAL_RESOLUTION, observed_image, make_perpendicular_display


def sRGB_to_Lab(r, g, b):
    XYZ = colour.sRGB_COLOURSPACE.to_XYZ.dot(np.array([r, g, b]))
    L, a, b = colour.XYZ_to_Lab(XYZ)
    return L, a, b,


def Lab_to_sRGB(L, a, b):
    XYZ = colour.Lab_to_XYZ(np.array([L, a, b]),
                            illuminant=colour.ILLUMINANTS.get('CIE 1931 2 Degree Standard Observer').get('D65'))
    r, g, b = colour.sRGB_COLOURSPACE.to_RGB.dot(XYZ)
    return r, g, b


v_sRGB_to_Lab = np.vectorize(sRGB_to_Lab)
v_Lab_to_sRGB = np.vectorize(Lab_to_sRGB)


def filter_image(image, display, observer):
    r, g, b = image[..., 0], image[..., 1], image[..., 2]
    Lab_image = v_sRGB_to_Lab(r, g, b)
    filtered_luminance = observed_image(Lab_image[0], display, observer)
    l_image = filtered_luminance, np.zeros(filtered_luminance.shape), np.zeros(filtered_luminance.shape)
    out_image = v_Lab_to_sRGB(*l_image)
    return out_image


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
    if os.path.exists(out_path):
        print('Skipped image')
    else:
        out_image = filter_image(image, display, observer_direct)
        misc.imsave(out_path, out_image[0])
        print('Saved image', out_path)

    observer_forward_dir = np.array([0, 1, 0])
    observer_forward = ObserverSpecification(observer_pos, observer_forward_dir, DEFAULT_FOVEAL_RESOLUTION)

    out_path = OUT_FILE_PATTERN.format("indirect")
    if os.path.exists(out_path):
        print('Skipped image')
    else:
        out_image = filter_image(image, display, observer_forward)
        misc.imsave(out_path, out_image[0])
        print('Saved image', out_path)
