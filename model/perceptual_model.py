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

from collections import namedtuple
import numpy as np
from scipy import signal

DEFAULT_FOVEAL_RESOLUTION = 60.
"""
Resolution tested for with a Snellen chart to determine 20/20 vision (in cycles per degree).

This value is subject to inter-individual differences in eye-sight, lighting conditions and stimulus properties.

DEFAULT_FOVEAL_RESOLUTION : float

"""

DisplaySpecification = namedtuple('DisplaySpecification',
                                  ('p1', 'p2', 'p3', 'p4', 'x_res', 'y_res'))
"""
Specifies the parameters of a display.


p1           a            p2
  +----------------------+
  |                      |
 d|                      |b
  |                      |
  +----------------------+
p4           c            p3


Parameters
----------
p1, p2, p3, p4 : array_like
    3D coordinates of the vertices defining the display position.
x_res, y_res : numeric
    resolution for edges a, c and b, d.

"""

ObserverSpecification = namedtuple('ObserverSpecification',
                                   ('pos', 'dir', 'acuity'))
"""
Specifies the parameters of an observer_forward.
Parameters
----------
pos : array_like
    3D coordinates of position of the observer_forward.
dir : array_like
    3D vector specifying the viewing direction of the observer_forward.
acuity : numeric
    Visual acuity of the observer_forward in cpd.
"""

DEFAULT_VIEW_DIRECTION = np.array([0, 1, 0]) / np.linalg.norm(
    np.array([0, 1, 0]))
DEFAULT_OBSERVER_POSITION = np.array([0, 0, 0])
DEFAULT_OBSERVER = ObserverSpecification(DEFAULT_OBSERVER_POSITION,
                                         DEFAULT_VIEW_DIRECTION,
                                         DEFAULT_FOVEAL_RESOLUTION)


def visual_angle_for_points(p1, p2):
    """
    Return the visual angle of a line segment between two points.

    Parameters
    ----------
    p1, p2 : array_like
        3D position of the two points.

    Returns
    -------
    float
        Visual angle in radians.

    Examples
    --------
    >>> np.degrees(visual_angle_for_points((1, 0, 0), (1, 1, 0))) # doctest: +ELLIPSIS
    45.0...
    >>> np.degrees(visual_angle_for_points((1, 1, 0), (-1, 1, 0))) # doctest: +ELLIPSIS
    90.0...
    >>> np.degrees(visual_angle_for_points((0, 1, 0), (0, 1, 1))) # doctest: +ELLIPSIS
    45.0...
    >>> visual_angle_for_points((0, 4, 0), (0, 5, 0))
    0.0
    """
    return np.arccos(np.dot(p1, p2) / (np.linalg.norm(p1) * np.linalg.norm(p2)))


def visual_angles_for_display_axes(display, observer=DEFAULT_OBSERVER):
    """
    Computes the visual angle for each main axis of the display.


    Parameters
    ----------
    display : DisplaySpecification
        Specification of the given display
    observer : ObserverSpecification, optional
        Specification of the observer


    Returns
    -------
    ndarray
        Visual angle for each axis of the display in radians.

    Examples
    --------
    >>> p1, p2, p3, p4 = np.array([-1, 1, 1]), np.array([1, 1, 1]), np.array([1, 1, -1]), np.array([-1, 1, -1])
    >>> display = DisplaySpecification(p1, p2, p3, p4, 100, 100)
    >>> np.degrees(visual_angles_for_display_axes(display))
    array([ 90.,  90.])
    >>> p1, p2, p3, p4 = np.array([-1, 1, 0]), np.array([1, 1, 0]), np.array([1, 2, 0]), np.array([-1, 2, 0])
    >>> display = DisplaySpecification(p1, p2, p3, p4, 100, 100)
    >>> np.degrees(visual_angles_for_display_axes(display))
    array([ 67.38013505,   0.        ])
    """
    upper = ((display.p1 + display.p2) / 2) - observer.pos
    lower = ((display.p4 + display.p3) / 2) - observer.pos
    left = ((display.p1 + display.p4) / 2) - observer.pos
    right = ((display.p2 + display.p3) / 2) - observer.pos

    x = visual_angle_for_points(left, right)
    y = visual_angle_for_points(upper, lower)

    return np.array([x, y])


def resolution_per_axis_in_cpd(display, observer=DEFAULT_OBSERVER):
    """
    Computes resolution of the given display for each axis of the display in cycles per degree.

    Parameters
    ----------
    display : DisplaySpecification
        Specification of the given display

    Returns
    -------
    ndarray
        Resolution for each axis (x, y) of the display in cycles per degree.

    Examples
    --------
    >>> p1, p2, p3, p4 = np.array([-1, 1, 1]), np.array([1, 1, 1]), np.array([1, 1, -1]), np.array([-1, 1, -1])
    >>> x_res, y_res = 200, 100
    >>> display = DisplaySpecification(p1, p2, p3, p4, x_res, y_res)
    >>> resolution_per_axis_in_cpd(display)
    array([ 1.11111111,  0.55555556])

    """

    # Visual angle for each edge in degree
    visual_angles = np.degrees(
        visual_angles_for_display_axes(display, observer))

    # Resolution of each edge in cycles
    axis_resolutions = np.array([display.x_res, display.y_res]) / 2

    # Resolution in cycles per degree
    cpd = axis_resolutions / visual_angles

    return cpd


def magnification_factor_reddy(E):
    """
    Returns an approximation of the cortical magnification factor.

    Parameters
    ----------
    E : float
        Eccentricity in degree.

    Returns
    -------
    float
        Cortical magnification factor.

    Raises
    ------
    ValueError
       If an invalid area is given, or E is out of range for the given area.

    References
    ----------
    .. [1]  Reddy, M. (1997). Perceptually modulated level of detail for virtual environments.

    Examples
    --------
    >>> magnification_factor_reddy(0)
    1.0
    >>> magnification_factor_reddy(45)
    0.035624256837098696

    """

    if E <= 5.79:
        return 1.0
    else:
        return 7.49 / ((0.3 * E + 1) ** 2)


def angle_between_vectors(v1, v2):
    """
    Return angle between two vectors in radians.
    """
    if np.array_equal(v1, v2):
        return 0.
    argument = (np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
    if (argument > 1.0):
        argument = 1.0
    return np.arccos(argument)


def magnification_factor_for_display_reddy(display, observer=DEFAULT_OBSERVER):
    """
    Return the cortical magnification factor for the center of mass of the given display.
    Observer is assumed to be looking in direction of positive y-axis.

    Parameters
    ----------
    display : DisplaySpecification
        Specification of the given display

    Returns
    -------
    float
        Interpolated cortical magnification factor.

    Raises
    ------
    ValueError
        If display is out of range for cortical magnification computations.

    Examples
    --------
    >>> p1, p2, p3, p4 = np.array([-1, 1, 1]), np.array([1, 1, 1]), np.array([1, 1, -1]), np.array([-1, 1, -1])
    >>> display = DisplaySpecification(p1, p2, p3, p4, 100, 100)
    >>> magnification_factor_for_display_reddy(display)
    1.0
    >>> p1, p2, p3, p4 =  np.array([-5, 1, -5]), np.array([-5, 1, -5]), np.array([-5, 1, -5]), np.array([-5, 1, -5])
    >>> display = DisplaySpecification(p1, p2, p3, p4, 100, 100)
    >>> magnification_factor_for_display_reddy(display)
    0.011442094924422112
    """
    center_of_mass = display_center(display)
    center_of_mass_relative = center_of_mass - observer.pos
    center_of_mass_relative_norm = center_of_mass_relative / np.linalg.norm(
        center_of_mass_relative)

    angle = np.degrees(
        angle_between_vectors(observer.dir, center_of_mass_relative_norm))
    return magnification_factor_reddy(angle)


def observed_cycles_per_axis(display, observer=DEFAULT_OBSERVER):
    """
    Return observed resolution of the display in cycles per axis, taking into account distance, eccentricity and visual
    acuity. Observer is assumed to be facing in direction of the positive y axis.

    Parameters
    ----------
    display : DisplaySpecification
        Specification of the given display
    observer : ObserverSpecification, optional
        Specification of the observer. Defaults to DEFAULT_OBSERVER.

    Returns
    -------
    array_like
        Resolution for each axis (x, y) of the display in cycles per edge.

    Raises
    ------
    ValueError
        If display is out of range for cortical magnification computations.

    Examples
    --------
    >>> p1, p2, p3, p4 = np.array([-1, 10, 1]), np.array([1, 10, 1]), np.array([1, 10, -1]), np.array([-1, 10, -1])
    >>> display = DisplaySpecification(p1, p2, p3, p4, 100, 100)
    >>> observed_cycles_per_axis(display)
    array([ 50.,  50.])
    >>> p1, p2, p3, p4 = np.array([-1, 100, 1]), np.array([1, 100, 1]), np.array([1, 100, -1]), np.array([-1, 100, -1])
    >>> display = DisplaySpecification(p1, p2, p3, p4, 100, 100)
    >>> observed_cycles_per_axis(display)
    array([ 34.37632186,  34.37632186])
    >>> p1, p2, p3, p4 = np.array([0, 10, 1]), np.array([1, 10, 1]), np.array([1, 10, 0]), np.array([0, 10, 0])
    >>> display = DisplaySpecification(p1, p2, p3, p4, 100, 100)
    >>> observed_cycles_per_axis(display)
    array([ 50.,  50.])

    """

    # Get resolution for display in cycles per degree (cpd).
    resolution_cpd = resolution_per_axis_in_cpd(display, observer)
    # Take into account that there is a maximum for the observable resolution.
    # If the resolution of the edge is higher than what can be observed (including factor for eccentricity),
    # use the observed resolution instead.
    magnification = magnification_factor_for_display_reddy(display, observer)
    resolution_cpd = np.minimum(resolution_cpd, magnification * observer.acuity)
    # Get the size of each edge in degree.
    size = np.degrees(visual_angles_for_display_axes(display, observer))
    # Now multiply the cpd resolution with the display angles to get the cycles per edge.
    # Cutoff is the actual display resolution (won't increase just because display is closer).
    max_cycles = np.array([display.x_res, display.y_res]) / 2
    observed_cycles = np.minimum(resolution_cpd * size, max_cycles)

    return observed_cycles


def observed_image(image, display, observer=DEFAULT_OBSERVER):
    """
    Return observed resolution of the display in cycles per edge, taking into account distance, eccentricity and visual acuity.
    Observer is assumed to be facing in direction of the positive y axis.

    Parameters
    ----------
    image : array_like
        Greyscale image to be transformed in array form.
    display : DisplaySpecification
        Specification of the given display.
    observer : ObserverSpecification, optional
        Specification of the observer. Defaults to DEFAULT_OBSERVER.

    Returns
    -------
    array_like,
        Output image as array.

    """
    cycles = observed_cycles_per_axis(display, observer)
    x_res = cycles[0]
    y_res = cycles[1]

    b_x, a_x = signal.butter(2, x_res / (image.shape[1]))
    b_y, a_y = signal.butter(2, y_res / (image.shape[0]))

    out_image = signal.lfilter(b_x, a_x, image, axis=1)
    out_image = signal.lfilter(b_y, a_y, out_image, axis=0)

    return out_image


def make_display(width, height, distance, tilt, x_res, y_res):
    """
    Return display.
          |t /
          | /
          |/
    -------------
         /|
        / |
       /  |

    Parameters
    ----------
    width, height : numeric
        Width and height of the display.
    distance : numeric
        Distance of the from the coordinate zero in y-direction.
    tilt : numeric
        Backwards tilt of the display around its center in radians.
    x_res, y_res : numeric
        Resolution oif the display along its x- and y-axis.

    Returns
    -------
    DisplaySpecification,
        Display created according to specified parameters.

    """
    upper_distance = distance + np.sin(tilt) * (height / 2)
    lower_distance = distance - np.sin(tilt) * (height / 2)

    upper_height = np.cos(tilt) * height / 2
    lower_height = - upper_height

    p1 = np.array([-width / 2, upper_distance, upper_height])
    p2 = np.array([width / 2, upper_distance, upper_height])
    p3 = np.array([width / 2, lower_distance, lower_height])
    p4 = np.array([-width / 2, lower_distance, lower_height])
    return DisplaySpecification(p1, p2, p3, p4, x_res, y_res)


def spherical_to_cartesian(r, h_angle, v_angle):
    """
    Convert the spherical coordinates to caertesian coordinates.

    Parameters
    ----------
    r : numeric
        Radial distance.
    h_angle, v_angle : numeric
        Horizontal and vertical angle in radians

    Returns
    -------
    ndarray (3,)
        Cartesian coordinates.
    """

    # The vector.
    return np.array([r * np.sin(h_angle) * np.cos(v_angle),
                     r * np.cos(h_angle) * np.cos(v_angle),
                     r * np.sin(v_angle)])


def rotation_matrix(axis, theta):
    """
    Return the rotation matrix associated with counterclockwise rotation about
    the given axis by theta radians.

    Source:
     * http://stackoverflow.com/questions/6802577/python-rotation-of-3d-vector
    """
    axis = np.asarray(axis)
    theta = np.asarray(theta)
    axis = axis / np.sqrt(np.dot(axis, axis))
    a = np.cos(theta / 2)
    b, c, d = -axis * np.sin(theta / 2)
    aa, bb, cc, dd = a * a, b * b, c * c, d * d
    bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
    return np.array([[aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
                     [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
                     [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc]])


def make_perpendicular_display(width, height, distance, h_angle, v_angle,
                               x_res, y_res):
    """
    Return display that is facing the coordinates's system origin.

    Parameters
    ----------
    width, height : numeric
        Width and height of the display.
    distance : numeric
        Distance of the from the coordinate zero in y-direction.
    h_angle, v_angle : numeric
        Horizontal and vertical angle of the display position in radians.
    x_res, y_res : numeric
        Resolution oif the display along its x- and y-axis.

    Returns
    -------
    DisplaySpecification,
        Display created according to specified parameters.

    """

    base_display = make_display(width, height, 0, 0, x_res, y_res)
    display_offset = spherical_to_cartesian(distance, h_angle, v_angle)
    # our h_angle is clockwise
    rotation_matrix_h = rotation_matrix(np.array([0, 0, 1]), -h_angle)
    rotation_matrix_v = rotation_matrix(np.array([1, 0, 0]), v_angle)
    rotation = rotation_matrix_h.dot(rotation_matrix_v)

    p1 = rotation.dot(base_display.p1) + display_offset
    p2 = rotation.dot(base_display.p2) + display_offset
    p3 = rotation.dot(base_display.p3) + display_offset
    p4 = rotation.dot(base_display.p4) + display_offset

    return DisplaySpecification(p1, p2, p3, p4, x_res, y_res)


def display_center(display):
    """
    Return the center of the display.
    Parameters
   ----------
    display : DisplaySpecification
        Specification of the given display.
    Returns
    -------
    array_like,
        3D point of the display center.
    """
    return (display.p1 + display.p2 + display.p3 + display.p4) / 4
