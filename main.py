""" Simple script to compare a very simple search across flight sites. """
from __future__ import unicode_literals, absolute_import, generators, \
    print_function

from air_finder import AirFinder
from qpx_express import QPXExpressApi, QPXRequest
from sky_picker import SkyPickerApi

from ConfigParser import ConfigParser
import pandas as pd
from datetime import datetime

config = ConfigParser()
config.read(['config/prod.cfg'])


def prepare_af_data(results):
    """ Prepare airfinder results so they can be easily compared. """
    af_df = pd.DataFrame(results)
    af_df['num_stops'] = af_df.num_stops.str.replace(r'[^\d]', '').astype(int)
    af_df['search_engine'] = 'airfinder.de'
    return af_df


def prepare_qpx_data(results):
    """ Prepare qpx results so they can be easily compared. """
    qpx_df = pd.DataFrame(results)
    qpx_df['num_stops'] = qpx_df['legs'].map(lambda x: len(x) - 1)
    qpx_df['search_engine'] = 'QPX Express'
    return qpx_df


def prepare_sp_data(results):
    """ Prepare skypicker results so they can be easily compared. """
    sp_df = pd.DataFrame(results)
    sp_df['search_engine'] = 'SkyPicker'
    sp_df['num_stops'] = sp_df['legs'].map(lambda x: len(x) - 1)
    return sp_df


def prepare_final(final_df):
    """ Some cleaning for easy sort and comparison. """
    final_df['price'] = final_df.price.astype(float)
    final_df['duration_hours'] = final_df.duration_hours.astype(float)
    final_df['departure_tod'] = final_df.departure.map(time_of_day)
    return final_df


def time_of_day(dt_obj):
    """ Mapping function to return a string representing time of day for
    the departure or arrival datetime objects. """
    if dt_obj.hour < 8 and dt_obj.hour > 2:
        return 'early am'
    elif dt_obj.hour < 12:
        return 'morning'
    elif dt_obj.hour < 16:
        return 'afternoon'
    elif dt_obj.hour < 22:
        return 'evening'
    return 'late evening'


def compare_all(origin, destination, travel_date, num_adults):
    """ Call search for each of the flight engines using simple one-way flight.
    :param origin: string
    :param destination: string
    :param travel_date: datetime
    :param num_adults: number of adults traveling
    """
    af_api = AirFinder()
    af_results = af_api.search(origin, destination, travel_date, num_adults)

    qpx_api = QPXExpressApi(api_key=config.get('qpx', 'api_key'))
    qpx_request = QPXRequest(origin, destination, travel_date, num_adults)
    qpx_resp = qpx_api.search(qpx_request)
    qpx_results = qpx_resp.top_flights()

    sp_api = SkyPickerApi()
    sp_results = sp_api.search_flights(origin, destination, travel_date,
                                       travel_date, num_adults)

    af_df = prepare_af_data(af_results)
    sp_df = prepare_sp_data(sp_results)
    qpx_df = prepare_qpx_data(qpx_results)

    final_df = pd.concat([af_df, sp_df, qpx_df], ignore_index=True)
    final_df = prepare_final(final_df)
    return final_df


if __name__ == '__main__':
    origin = raw_input('where are you flying from? ')
    destination = raw_input('where are you flying to? ')
    travel_date = raw_input('what date (%m/%d/%Y format plz)? ')
    num_adults = raw_input('number of adults traveling? ')
    final = compare_all(origin.strip(), destination.strip(),
                        datetime.strptime(travel_date, '%m/%d%Y'),
                        int(num_adults))
    print('lowest prices....')
    print(final.sort('price')[:5])
    print('shortest flights....')
    print(final.sort('duration_hours'))
