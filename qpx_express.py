""" Python client to use for requesting Google's QPX Express API. """
from __future__ import unicode_literals, absolute_import, generators, \
    print_function

import requests
import json
import re
from datetime import datetime


class QPXExpressApi(object):
    """ QPX Express API """

    def __init__(self, api_key=None):
        """ API Contrstructor
        :param api_key: Google API Key
        """
        self.api_key = api_key
        self.request_count = 0
        self.request_url = 'https://www.googleapis.com/qpxExpress/' + \
            'v1/trips/search?key={}'.format(api_key)

    def search(self, request):
        """ Search the API
        :param request: QPXRequest object

        returns QPXResponse object
        """
        headers = {'content-type': 'application/json'}
        resp = requests.post(self.request_url, data=request.get_json(),
                             headers=headers)
        self.request_count += 1
        return QPXResponse(resp.json())

    def estimate_api_costs(self):
        """ Estimate API costs based on current count. """
        return '${.2f}'.format((lambda x: x if x > 0 else 0)(
            (self.request_count - 50) * .035))


class QPXRequest(object):
    """ QPX Request formatter. """
    def __init__(self, origin, destination, date, num_adults, return_date=None):
        """ Create request object.
        :param origin: origin airport or IATA code
        :param destination: destination airport or IATA code
        :param date: datetime object
        :param num_adults: integer representing the number of adults
        :kwarg return_date: datetime object
        """
        self.origin = origin
        self.destination = destination
        self.date = date
        self.return_date = return_date
        self.num_adults = num_adults
        self.passengers = {
            'kind': 'qpxexpress#passengerCounts',
            'adultCount': num_adults,
        }
        self.slices = [{
            'kind': 'qpxexpress#sliceInput',
            'origin': origin,
            'destination': destination,
            'date': date.strftime('%Y-%m-%d')
        }]
        if return_date:
            self.slices.append({
                'kind': 'qpxexpress#sliceInput',
                'origin': destination,
                'destination': origin,
                'date': return_date.strftime('%Y-%m-%d')
            })

    def add_passengers(self, num_child, num_senior=0, num_inf_lap=0,
                       num_inf_seat=0):
        """ Add passengers to your request.
        :param num_child: integer representing number of children
        :kwarg num_senior: integer representing number of seniors
        :kwarg num_inf_lap: integer representing number of infants in lap
        :kwarg num_inf_seat: integer representing number of infants in seats
        """
        self.passengers['childCount'] = int(num_child)
        self.passengers['seniorCount'] = int(num_senior)
        self.passengers['infantInLapCount'] = int(num_inf_lap)
        self.passengers['infantInSeatCount'] = int(num_inf_seat)

    def get_json(self):
        """ Returns json representation to send to the API."""
        json_format = {'request': {}}
        json_format['request']['passengers'] = self.passengers
        json_format['request']['slice'] = self.slices
        json_format['request']['refundable'] = False
        return json.dumps(json_format)


class QPXResponse(object):
    """ QPX Response object. """
    def __init__(self, json_resp):
        self.raw_data = json_resp
        self.flight_options = json_resp.get('trips').get('tripOption')

    def sort_by_base_price(self):
        """ Sort all flights by base price, putting lowest first. """
        self.flight_options = sorted(self.flight_options,
                                     key=lambda x: float(re.search(
                                         r'\d+', x[
                                             'pricing'][0]['baseFareTotal']
                                     ).group(0)))

    def sort_by_total_price(self):
        """ Sort all flights by total price, putting lowest first. """
        self.flight_options = sorted(self.flight_options,
                                     key=lambda x: float(re.search(
                                         r'\d+', x['saleTotal']).group(0)))

    def sort_by_duration(self):
        """ Sort all flights by duration, putting shortest first. """
        self.flight_options = sorted(self.flight_options, key=lambda x:
                                     x['slice'][0]['duration'])

    def top_flights(self, num=10, sort='price'):
        """ Return a smaller (more readable) dictionary of top cheapest flights.
        :kwargs num: integer of how many to show (default: 10)
        :kwargs sort: 'price' or 'duration' sort method (default: 'price')

        returns sorted list with some (but not all) details for easy reading
        """
        if sort == 'price':
            self.sort_by_total_price()
        elif sort == 'duration':
            self.sort_by_duration()
        top_flights = []
        for flight in self.flight_options[:num]:
            flight_info = {'price': re.search(r'[\d.]+',
                                              flight.get('saleTotal')).group(),
                           'currency': re.search(r'[^\d.]+',
                                                 flight.get(
                                                     'saleTotal')).group(),
                           'duration': flight['slice'][0]['duration'],
                           'duration_hours': flight['slice'][0][
                               'duration'] / 60.0,
                           'departure': datetime.strptime(
                               flight['slice'][0]['segment'][0][
                                   'leg'][0]['departureTime'][:15],
                               '%Y-%m-%dT%H:%S'),
                           'arrival': datetime.strptime(
                               flight['slice'][0]['segment'][-1][
                                   'leg'][0]['arrivalTime'][:15],
                               '%Y-%m-%dT%H:%S'),
                           'legs': []}
            for segment in flight['slice'][0]['segment']:
                flight_info['legs'].append({
                    'origin': segment['leg'][0]['origin'],
                    'departure': segment['leg'][0]['departureTime'],
                    'arrival': segment['leg'][0]['arrivalTime'],
                    'destination': segment['leg'][0]['destination'],
                    'carrier': segment['flight']['carrier'],
                    'total_duration': (lambda x: segment[x] if x in
                                       segment.keys() else segment['duration'])(
                                           'connectionDuration')
                })
            flight_info['carrier'] = ', '.join(set([c.get('carrier') for c in
                                                    flight_info['legs']]))
            top_flights.append(flight_info)
        return top_flights
