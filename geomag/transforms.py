import math

from geomag.constants import *


def normalise_decimal_degrees(value, norm_range):
    norm_range_dict = {"lat": 90, "lng": 180}
    try:
        valid_range = norm_range_dict[norm_range]
        value %= [-1, 1][value > 0] * valid_range * 2
    except KeyError:
        valid_range = norm_range
    if abs(value) > valid_range:
        return value % ([1, -1][value > 0] * valid_range)
    else:
        return value


def geo_to_spherical(rlat, rlng, alt):
    """
    Convert a set of normalised geographical coordinates to spherical
    rlat: (latitude) in radians
    rlng: (longitude) in radians
    alt: (altitude) in kilometres
    return: (theta, phi, r) in radians, degrees and metres respectively
    """

    alt = alt * 1000  # convert km to m

    normal_section = EQUATOR_RADIUS / math.sqrt(1 - EE2 * math.sin(rlat) ** 2)
    p = (normal_section + alt) * math.cos(rlat)
    z = (normal_section * (1 - EE2) + alt) * math.sin(rlat)
    r = math.sqrt(p ** 2 + z ** 2)

    theta = math.asin(z / r)
    phi = math.degrees(rlng)

    return (theta, phi, r)


def spherical_to_geo(theta, phi, r):
    pass
