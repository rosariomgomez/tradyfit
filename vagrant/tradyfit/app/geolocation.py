# -*- coding: utf-8 -*-
import os
import maxminddb
from flask import current_app
from . import geolocator, opbeat
from ipaddr import IPAddress

path = os.path.dirname(os.path.abspath(__file__))
db_file = os.path.join(path,'../geoip/GeoLite2-City.mmdb')
geo_db = maxminddb.open_database(db_file)


class Geolocation(object):

  def __init__(self, ip):
    self.location = Geolocation.get_location(ip)


  @staticmethod
  def validate_ip(string_ip):
    '''verify that the IP is a valid IPv4 or IPv6 address'''
    try:
      IPAddress(string_ip)
      return True
    except ValueError:
      return False


  @staticmethod
  def get_location(ip):
    '''use the MaxMind DB to find the user location from the IP address.
    maxminddb internally verify if it is a valid IP.
    If an error occur (not a valid IP) an exception is raised. If there is no
    info for that ip e.g. 127.0.0.1, None is also the returned value
    Input: (string) ip
    Output: (dict) geolocation info or None
    '''
    try:
      return geo_db.get(ip)
    except ValueError:
      return None


  @staticmethod
  def create_address(city, state, country):
    '''generate a string with an address'''
    if country == 'US' and state != 'NU': #'NU'== 'Not US'
      return ', '.join([city, state, country])
    else:
      return ', '.join([city, country])


  @staticmethod
  def get_geolocation(address):
    '''use GoogleV3 geolocation service to extract latitude and longitude
    coordinates from an address
    Input: (string) address
    Output: (float, float) (latitude, longitude)'''
    if not current_app.testing:
      try:
        location = geolocator.geocode(address)
        return (location.latitude, location.longitude)
      except:
        #send exception to error log
        opbeat.captureException()
        return None


  def get_city(self):
    '''return city from dict geolocation.
    Even that get the city doesn't throws an exception, it could be None
    Possible Outputs: (True, <string>city) or (False, None)
    '''
    try:
      city = self.location.get('city').get('names').get('en')
      if city:
        return True, city
      return False, None
    except AttributeError:
      return False, None


  def get_location_value(self, param1, param2):
    '''helper method to retrieve country, latitude or longitude values
    Possible Outputs: (True, <string>) or (False, None)'''
    try:
      value = self.location.get(param1).get(param2)
      if value:
        return True, value
      return False, None
    except AttributeError:
      return False, None


  def get_country(self):
    '''return country from dict geolocation
    Possible Outputs: (True, <string>country) or (False, None)
    '''
    return self.get_location_value('country', 'iso_code')


  def get_state(self):
    '''return state from dict geolocation if country is US
    Possible Outputs: (True, <string>state) or (False, None)
    '''
    r, country = self.get_country()
    if r and country == 'US':
      try:
        state = self.location.get('subdivisions')
        if state:
          state = state[0].get('iso_code')
        return True, state
      except AttributeError:
        return False, None
    else:
      return False, None


  def get_latitude(self):
    '''return latitude from dict geolocation
    Possible Outputs: (True, <string>latitude) or (False, None)
    '''
    return self.get_location_value('location', 'latitude')


  def get_longitude(self):
    '''return longitude from dict geolocation
    Possible Outputs: (True, <string>longitude) or (False, None)
    '''
    return self.get_location_value('location', 'longitude')

