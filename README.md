Python Flight Search
=========================

A simple and extendable series of Python scripts for searching flight options. Contributions welcome!

Scripts
--------

 * `air_finder.py` - A script to simply scrape flights from [airfinder.de](http://airfinder.de)
 * `sky_picker.py` - A script to interact with the [skypicker.com](http://skypicker.com) API. [More documentation available here](http://docs.skypickerpublicapi.apiary.io/#reference/flights). Note: this is the only one that supports a flight range (i.e. I want to travel sometime in between these dates...).
 * `qpx_express.py` - A script with some simple API, request and response classes for interacting with Google's [QPX Express API](https://developers.google.com/qpx-express/). For more documentation on the format of the request and response, see [the API Reference](https://developers.google.com/qpx-express/v1/).
 * `main.py` - Testing by searching them all and comparing in a `pandas` DataFrame.

Requirements
------------

Install the necessary requirements using the `requirements.txt` file. Not all scripts need all requirements, so please check the script you are interested in using if you'd like to individually install and use the packages.

The QPX Express API requires an API Key (which you can request on the Google Developer's Console). To use the `main.py` script for comparison, you'll need to have the api key stored in a config folder, in a file called `prod.cfg` (section `qpx`, key `api_key`). Or just modify the `main.py` script to your liking. >.<

TO DO (feel free to help / chime in!)
-----
 * Get return flight parsing for each working properly
 * Investigate child flying options for sky_picker / air_finder
 * Active "watching" lookup script (i.e. flight alert)
 * Clean up very messy qpx parsing :(

Questions?
----------
/msg kjam on twitter or freenode.

