# CoronaAppMap - Maps bluetooth exposure notification beacons on a map
# Copyright (C) 2020  Foaly

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import sqlite3
import random
import collections
import math
import gmaps
from ipywidgets.embed import embed_minimal_html


RGB = collections.namedtuple('RGB', ['r', 'g', 'b'])


def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))


# convert hue to RGB
# hue has to be in range [0.f,1.f]
def hue_to_RGB(hue: float):
    r = abs(3.0 - 6.0 * hue) - 1.0
    g = 2.0 - abs(2.0 - 6.0 * hue)
    b = 2.0 - abs(4.0 - 6.0 * hue)

    return RGB(clamp(r, 0.0, 1.0) * 255, clamp(g, 0.0, 1.0) * 255, clamp(b, 0.0, 1.0) * 255)


def destination_point(start_lat, start_lon, distance, bearing):
    """
    Calculates the destination point given a start point, a distance traveled in the initial bearing.

    :param start_lat: latitude in degrees
    :param start_lon: longitude in degrees
    :param distance: distance traveled in meters
    :param bearing: initial bearing in degrees, clockwise from north
    :return: latitude in degrees, longitude in degrees
    """
    earth_radius = 6371000  # in meters
    φ1 = start_lat * math.pi / 180.0  # convert degrees to radians
    λ1 = start_lon * math.pi / 180.0  # convert degrees to radians
    θ = bearing * math.pi / 180.0  # convert degrees to radians
    ang_dist = distance / earth_radius

    φ2 = math.asin(math.sin(φ1) * math.cos(ang_dist) +
                   math.cos(φ1) * math.sin(ang_dist) * math.cos(θ))
    λ2 = λ1 + math.atan2(math.sin(θ) * math.sin(ang_dist) * math.cos(φ1),
                         math.cos(ang_dist) - math.sin(φ1) * math.sin(φ2))

    # convert result back to degrees
    end_lat = φ2 * 180.0 / math.pi
    end_lon = λ2 * 180.0 / math.pi
    return end_lat, end_lon


def main():
    db_file = "RaMBLE_playstore_v35.14_20200621_2000.sqlite"
    not_before_date = {"not_before_date": '2020-06-21'}

    connection = sqlite3.connect(db_file)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""SELECT 
                          datetime(locations.timestamp, 'unixepoch', 'localtime') as 'Timestamp',
                          devices.service_data as 'Rolling Proximity Identifier',
                          locations.rssi as 'RSSI',
                          locations.latitude as 'Latitude',
                          locations.longitude as 'Longitude',
                          locations.accuracy as 'Accuracy'
                      FROM devices
                      INNER JOIN locations ON devices.id = locations.device_id
                      WHERE 
                          service_uuids = "fd6f" AND
                          datetime(locations.timestamp, 'unixepoch', 'localtime') > datetime( :not_before_date , 'localtime')
                      ORDER BY devices.service_data """, not_before_date)
    result = cursor.fetchall()
    connection.close()

    if not result:
        print("No exposure notification beacons found!")
        return

    locations = []
    info_texts = []
    colors = []
    temp_color = 0
    r_p_id = 0

    for line in result:
        if r_p_id != line['Rolling Proximity Identifier']:
            rgb = hue_to_RGB(random.uniform(0.0, 1.0))
            temp_color = 'rgba(' + str(round(rgb.r)) + ', ' + str(round(rgb.g)) + ', ' + str(round(rgb.b)) + ', 1.0)'
            r_p_id = line['Rolling Proximity Identifier']

        lat, lon = destination_point(line["Latitude"], line["Longitude"], random.uniform(0, line["Accuracy"]), random.uniform(0, 360))

        locations.append([lat, lon])
        info_texts.append(line['Timestamp'] + "<br>" + line['Rolling Proximity Identifier'])
        colors.append(temp_color)

    # gmaps.configure(api_key='API_KEY')
    fig = gmaps.Map(width='100%', height='100vh', layout={'height': '98vh'})
    heatmap_layer = gmaps.heatmap_layer(
        locations, point_radius=30
    )
    dots = gmaps.symbol_layer(
       locations, fill_color=colors,
       stroke_color=colors, scale=3,
       info_box_content=info_texts, display_info_box=True
    )
    fig.add_layer(heatmap_layer)
    fig.add_layer(dots)

    embed_minimal_html('export.html', views=[fig], title="Corona App Export")


if __name__ == '__main__':
    main()
