# from https://www.ngdc.noaa.gov/geomag/WMM/data/WMM2020/WMM2020_Report.pdf
EQUATOR_RADIUS = 6378137
FLATTENING = 1 / 298.257223563
EE2 = FLATTENING * (2 - FLATTENING)  # eecentricity squared
N_MAX = 12  # degree of expansion
