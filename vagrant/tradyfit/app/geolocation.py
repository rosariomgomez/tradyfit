# -*- coding: utf-8 -*-
import maxminddb
from ipaddr import IPAddress, IPv4Address, IPv6Address


geo_db = maxminddb.open_database('geoip/GeoLite2-City.mmdb')


class Geolocation(object):

  def __init__(self, ip):
    self.location = Geolocation.get_location(ip)


  @staticmethod
  def validate_ip(string_ip):
    '''verify that the IP is a valid IPv4 or IPv6 address'''
    try:
      ip = IPAddress(string_ip)
      if type(ip) == IPv4Address or type(ip) == IPv6Address:
        return True
      else:
        return False
    except ValueError:
      return False


  @staticmethod
  def get_location(ip):
    '''use the MaxMind DB to find the user location from the IP address.
    maxminddb internally verify if it is a valid IP
    Input: (string) ip
    Output: (dict) geolocation info or None if an error occur'''
    try:
      return geo_db.get(ip)
    except:
      return None


  def get_city(self):
    '''return city from dict geolocation'''
    try:
      city = self.location.get('city').get('names').get('en')
      return True, city
    except:
      return False, None


  def get_country(self):
    '''return country from dict geolocation'''
    try:
      country = self.location.get('country').get('iso_code')
      return True, country
    except:
      return False, None


  def get_state(self):
    '''return state from dict geolocation if country is US'''
    r, country = self.get_country()
    if r and country == 'US':
      try:
        state = self.location.get('subdivisions')
        if state:
          state = state[0].get('iso_code')
        return True, state
      except:
        return False, None
    else:
      return False, None


  def get_latitude(self):
    '''return latitude from dict geolocation'''
    try:
      latitude = self.location.get('location').get('latitude')
      return True, latitude
    except:
      return False, None


  def get_longitude(self):
    '''return longitude from dict geolocation'''
    try:
      longitude = self.location.get('location').get('longitude')
      return True, longitude
    except:
      return False, None

