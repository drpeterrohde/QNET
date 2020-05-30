from skyfield.api import EarthSatellite
from skyfield.api import Topos, load
import numpy as np

ts = load.timescale()
t = ts.now()
t1 = ts.utc(t.utc[0], t.utc[1], t.utc[2], t.utc[3], t.utc[4], t.utc[5] + 100 )

line1 = '1 25544U 98067A   20149.87174847  .00000715  00000-0  20865-4 0 9990'
line2 = '2 25544  51.6450  84.0707 0001897   8.7970  32.5061 15.49398379229025'
satellite = EarthSatellite(line1, line2, 'ISS (ZARYA)', ts)
print(satellite)


## define a reference position on earth ##
planets = load('de421.bsp')
earth = planets['earth']
boston = Topos('42.3583 N', '71.0603 W')
print("Boston geolocation Lat Long: ", boston.latitude, boston.longitude)
print("\n")



## find satellite location in topocentric coordinates at given time with boston at center ##
geometry = satellite.at(t1)
print(geometry)
subpoint = geometry.subpoint()
latitude = subpoint.latitude
longitude = subpoint.longitude
elevation = subpoint.elevation
print("Satellite position above earth")
print(latitude, longitude, elevation.km, "km")
print("\n")




