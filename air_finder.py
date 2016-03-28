""" Search flight results on airfinder.de """
from __future__ import unicode_literals, absolute_import, generators, \
    print_function

from lxml import html
from urllib import urlencode
import requests
from datetime import datetime, timedelta
import locale

locale.setlocale(locale.LC_TIME, str('de_DE.utf8'))


class AirFinder(object):
    """ Air Finder Screen Scraper. """
    def __init__(self):
        """ Initialize with base url """
        self.base_url = 'http://www.airfinder.de/Seats.aspx?'
        self.date = None

    def search(self, origin, destination, date, num_adults):
        """ Search using a simple get request including flight details.
        :param origin: string
        :param destination: string
        :param date: datetime object
        :param num_adults: number of adult passengers
        """
        params = {'city1': origin, 'city2': destination,
                  'date1': date.strftime('%d/%m/%Y'),
                  'adults': num_adults, 'ec_search': 1}
        self.date = date
        response = requests.get('{}{}'.format(self.base_url, urlencode(params)))
        return self.parse_response(response)

    def grab_xpath_text(self, element, xpath):
        """ Given an element and xpath pattern, return text content.
        :param element: lxml element
        :param xpath: string
        returns string
        """
        data = element.xpath(xpath)
        if len(data) == 1:
            return data[0].text
        elif len(data) > 1:
            return [x.text for x in data]
        return ''

    def parse_response(self, response):
        """ Given a requests response object, return a list of dictionaries
        containing the pertinent flight info.
        :params response: response obj
        returns list of dictionaries
        """
        page = html.fromstring(response.content)
        results = page.xpath('//div[contains(@class, "itemresult")]')
        final_results = []
        for res in results:
            item_dict = {}
            item_dict['price'] = float(self.grab_xpath_text(
                res, 'div/div/span[@class="FlightPrice"]').replace(',', '.'))
            item_dict['currency'] = self.grab_xpath_text(
                res, 'div/div/span[@class="Currency"]')
            item_dict['date'] = self.grab_xpath_text(
                res, 'div/div/span[contains(@id, "dateLabel")]')
            more_flight_info = [r.text for r in res.xpath('div/div/div/span')]
            try:
                date_str = '{} {}'.format(item_dict['date'],
                                          more_flight_info[0])
                item_dict['departure'] = datetime.strptime(date_str,
                                                           '%d %B %Y %H:%M')
            except Exception as e:
                print('error with locale: %s', e.message)
                time_list = more_flight_info[0].split(':')
                item_dict['departure'] = self.date + timedelta(
                    hours=int(time_list[0]), seconds=int(time_list[1]) * 60)
            item_dict['num_stops'] = more_flight_info[1]
            item_dict['arrival'] = more_flight_info[2]
            item_dict['carrier'] = more_flight_info[3]  # 4 is dummy text
            item_dict['duration'] = more_flight_info[5]
            item_dict['duration_hours'] = int(more_flight_info[5].split(
                'h')[0]) + (int(more_flight_info[5].split('h')[1].rstrip(
                    'm')) / 60.0)
            final_results.append(item_dict)
        return final_results
