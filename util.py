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

import colour
import numpy as np
from perceptual_model.perceptual_model import observed_image


def sRGB_to_Lab(r, g, b):
    XYZ = colour.sRGB_COLOURSPACE.RGB_to_XYZ_matrix.dot(np.array([r, g, b]))
    L, a, b = colour.XYZ_to_Lab(XYZ)
    return L, a, b,


def Lab_to_sRGB(L, a, b):
    XYZ = colour.Lab_to_XYZ(np.array([L, a, b]),
                            illuminant=colour.ILLUMINANTS.get('CIE 1931 2 Degree Standard Observer').get('D65'))
    r, g, b = colour.sRGB_COLOURSPACE.XYZ_to_RGB_matrix.dot(XYZ)
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
