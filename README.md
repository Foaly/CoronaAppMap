CoronaAppMap
============

A small python script that maps collected bluetooth exposure notification beacons
and maps them as a heatmap on a map. The map is exported as a interactive html file.

The code is released under the GPL 3.0.


Instructions
------------

* Use the [RamBLE Android app](https://play.google.com/store/apps/details?id=com.contextis.android.BLEScanner) to collect bluetooth beacons.
* Export the RamBLE sqlite database and transfer it to your computer.
* Open the db file using `extract.py`
* Play with the `export.html` file :)
