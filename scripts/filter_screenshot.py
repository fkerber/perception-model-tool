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

import math
import ntpath

import click
import numpy as np
from scipy import misc, ndimage

from perceptual_model.perceptual_model import display_center, ObserverSpecification, \
    DEFAULT_FOVEAL_RESOLUTION, make_perpendicular_display
from scripts.util import filter_image


@click.command()
@click.argument('image_path',
                type=click.Path(exists=True))
@click.argument('output_path',
                type=click.Path())
@click.option('-d', '--distance',
              type=float,
              help='Distance of image to observer (m)')
@click.option('-s', '--display_size',
              nargs=2, type=float,
              help='Display width and height (m)')
@click.option('-r', '--display_resolution',
              nargs=2, type=int,
              help='Display resolution for width and height (px)')
@click.option('-ha', '--display_h_angle',
              type=float, default=0,
              help='Horizontal angle of display (deg)')
@click.option('-va', '--display_v_angle',
              type=float, default=0,
              help='Vertical angle of display (deg)')
@click.option('--observer_view_direction',
              nargs=3, type=float, default=None,
              help='Viewing direction of observer')
@click.option('--overwrite',
              is_flag=True,
              help="Overwrite existing files."
              )
def main(image_path, output_path,
         distance,
         display_size,
         display_resolution,
         display_h_angle,
         display_v_angle,
         observer_view_direction,
         overwrite):
    image = ndimage.imread(image_path)

    observer_pos = np.array([0, 0, 0])

    display = make_perpendicular_display(display_size[0],
                                         display_size[1],
                                         distance,
                                         math.radians(display_h_angle),
                                         math.radians(display_v_angle),
                                         display_resolution[0],
                                         display_resolution[1])

    observer_display_dir = display_center(display) - observer_pos
    observer_direct = ObserverSpecification(observer_pos, observer_display_dir,
                                            DEFAULT_FOVEAL_RESOLUTION)

    if (not overwrite) and ntpath.exists(output_path):
        print('Image already exists.')
        return

    if len(observer_view_direction) != 3:
        print('No valid viewing direction giving. Assuming observer looking '
              'directly at target.')
        out_image = filter_image(image, display, observer_direct)
    else:
        observer_forward_dir = np.array([observer_view_direction])
        observer_forward = ObserverSpecification(observer_pos,
                                                 observer_forward_dir,
                                                 DEFAULT_FOVEAL_RESOLUTION)

        out_image = filter_image(image, display, observer_forward)

    misc.imsave(output_path, out_image[0])
    print('Saved image', output_path)


if __name__ == '__main__':
    main()
