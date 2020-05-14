import math
import os
from datetime import date

import geomag.constants as constants
from geomag.transforms import geo_to_spherical, normalise_decimal_degrees
from geomag.utils import (
    calculate_decimal_year,
    recursion_constants,
    scalar_potential,
    schmidt_quasi_normalisation,
    square_array,
)


class MagneticModelData:
    def __init__(self):

        self.max_order = constants.N_MAX
        self.array_size = self.max_order + 1
        self.coeffs = square_array(self.array_size, 0.0)
        self.coeffs_dot = square_array(self.array_size, 0.0)
        self.time_adjusted_coefficients_cache = square_array(self.array_size, 0.0)

        filename = os.path.join(os.path.dirname(__file__), "WMM2020.COF")
        with open(filename) as world_magnetic_model_file:
            for line in world_magnetic_model_file:
                linevals = line.strip().split()
                if len(linevals) == 3:
                    self.epoch = float(linevals[0])
                    self.model = linevals[1]
                    self.modeldate = linevals[2]
                elif len(linevals) == 6:
                    degree_n = int(float(linevals[0]))
                    order_m = int(float(linevals[1]))
                    gauss_g = float(linevals[2])
                    gauss_h = float(linevals[3])
                    gauss_g_dot = float(linevals[4])
                    gauss_h_dot = float(linevals[5])
                    self.coeffs[order_m][degree_n] = gauss_g
                    self.coeffs_dot[order_m][degree_n] = gauss_g_dot
                    if order_m != 0:
                        self.coeffs[degree_n][order_m - 1] = gauss_h
                        self.coeffs_dot[degree_n][order_m - 1] = gauss_h_dot
        self._unnormalise_gauss_coefficients()

    def _unnormalise_gauss_coefficients(self):
        """ Convert Schmidt normalized Gauss coefficients to unnormalized """
        schmidt_norm = schmidt_quasi_normalisation(self.array_size)
        for n in range(self.array_size):
            for m in range(self.array_size):
                if m <= n:
                    self.coeffs[m][n] = schmidt_norm[m][n] * self.coeffs[m][n]
                    self.coeffs_dot[m][n] = schmidt_norm[m][n] * self.coeffs_dot[m][n]
                else:
                    self.coeffs[m][n] = schmidt_norm[n + 1][m] * self.coeffs[m][n]
                    self.coeffs_dot[m][n] = (
                        schmidt_norm[n + 1][m] * self.coeffs_dot[m][n]
                    )

    def time_adjust_gauss(self, time):
        """
        Time adjust the Gauss Coefficients
        """
        current_delta_time = calculate_decimal_year(time) - self.epoch
        self._update_time_coefficients(current_delta_time)
        return self.time_adjusted_coefficients_cache

    def _update_time_coefficients(self, delta_time):
        for n in range(1, self.max_order + 1):
            for m in range(0, n + 1):
                self.time_adjusted_coefficients_cache[m][n] = (
                    self.coeffs[m][n] + delta_time * self.coeffs_dot[m][n]
                )
                if m != 0:
                    self.time_adjusted_coefficients_cache[n][m - 1] = (
                        self.coeffs[n][m - 1] + delta_time * self.coeffs_dot[n][m - 1]
                    )


class WorldMagneticModel:
    def __init__(self):
        self.data = MagneticModelData()

    def calc_field(self, lat, lng, alt=0, date=date.today()):
        """calc_field(self, dlat, dlng, alt=0, date=date.today())

        Calculates the magnetic field for a given latitude and longitude in decimal degrees.

        **Parameters**

            lat
                Unnormalised latitude in degrees [0, 180]
            lng
                Unnormalised longitude in degrees [0, 360]
            alt : optional
                Altitude above WGS 84 ellipsoid surface (kilometres)
            date : datetime.date - optional
                Time will default to today

        ** derived **
            dlat
                Normalised latitude in degrees [-90, 90]
            dlng
                Normalised longitude in degrees [-180, 180]
            rlat
                Normalised latitude in radians
            rlng
                Normalised longitude in radians
        """

        dlat = normalise_decimal_degrees(lat, "lat")
        dlng = normalise_decimal_degrees(lng, "lng")
        rlat = math.radians(dlat)
        rlng = math.radians(dlng)

        assert -1 <= alt <= 850, "invalid altitude"
        assert 2020 <= calculate_decimal_year(date) < 2025, "date not valid"
        assert -90 <= dlat <= 90, "invalid normalised latitude"
        assert -180 <= dlng <= 180, "invalid normalised longitude"

        spherical_latitude, _, radial = geo_to_spherical(rlat, rlng, alt)

        b_radius, b_theta, b_phi = scalar_potential(
            self.data.time_adjust_gauss(date),
            rlng,
            spherical_latitude,
            self.data.array_size,
            self.data.array_size,
            radial,
            k=recursion_constants(self.data.array_size),
        )
        # Matching the method in the document
        b_radius = -b_radius
        b_theta = -b_theta
        # /*
        # ROTATE MAGNETIC VECTOR COMPONENTS FROM SPHERICAL TO
        # GEODETIC COORDINATES
        # */
        delta_latitude_radians = spherical_latitude - rlat
        sin_delta_latitude = math.sin(delta_latitude_radians)
        cos_delta_latitude = math.cos(delta_latitude_radians)

        self.Bx = b_theta * cos_delta_latitude - b_radius * sin_delta_latitude
        self.By = b_phi
        self.Bz = b_theta * sin_delta_latitude + b_radius * cos_delta_latitude
        self.Bh = math.sqrt(self.Bx ** 2 + self.By ** 2)
        self.total_intensity = math.sqrt(self.Bh ** 2 + self.Bz ** 2)
        self.declination = math.degrees(math.atan2(self.By, self.Bx))
        self.inclination = math.degrees(math.atan2(self.Bz, self.Bh))
        self.grid_variation = self.calculate_grid_variation(dlat, dlng)
        return self

    @property
    def field(self):
        return {
            "X": self.Bx,
            "Y": self.By,
            "Z": self.Bz,
            "H": self.Bh,
            "F": self.total_intensity,
            "I": self.inclination,
            "D": self.declination,
            "GV": self.grid_variation,
        }

    def calculate_grid_variation(self, dlat, dlng):
        """Calculate the magnetic grid variation

        Compute magnetic grid variation if the current
        geodetic position is in the arctic or antarctic
        (i.e. glat > +55 degrees or glat < -55 degrees)
        Otherwise, set magnetic grid variation to 0
        """
        cur_lat = dlat
        grid_variation = self.declination
        if cur_lat > 55:
            grid_variation -= dlng
        elif cur_lat < -55:
            grid_variation += dlat
        grid_variation %= 360
        return grid_variation
