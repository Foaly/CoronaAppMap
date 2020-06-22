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
import gmaps
from ipywidgets.embed import embed_minimal_html


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def main():
    db_file = "RaMBLE_playstore_v35.14_20200621_2000.sqlite"
    connection = sqlite3.connect(db_file)
    connection.row_factory = dict_factory
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
                      WHERE service_uuids = "fd6f"
                      ORDER BY locations.timestamp """)
    result = cursor.fetchall()
    connection.close()

    locations = []
    for line in result:
        locations.append([line["Latitude"], line["Longitude"]])

    # gmaps.configure(api_key='API_KEY')
    fig = gmaps.Map(width='100%', height='100vh', layout={'height': '98vh'})
    heatmap_layer = gmaps.heatmap_layer(
        locations, point_radius=30
    )
    dots = gmaps.symbol_layer(
        locations, fill_color='rgba(0, 150, 0, 0.6)',
        stroke_color='rgba(0, 100, 0, 0.6)', scale=3
    )
    fig.add_layer(heatmap_layer)
    fig.add_layer(dots)

    embed_minimal_html('export.html', views=[fig], title="Corona App Export")


if __name__ == '__main__':
    main()
