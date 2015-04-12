# -*- coding: utf-8 -*-
import maxminddb
from ipaddr import IPAddress


geo_db = maxminddb.open_database('geoip/GeoLite2-City.mmdb')


class Geolocation(object):

  def __init__(self, ip):
    self.location = Geolocation.get_location(ip)


  @staticmethod
  def validate_ip(string_ip):
    '''verify that the IP is a valid IPv4 or IPv6 address'''
    try:
      ip = ipaddr.IPAddress(string_ip)
      if type(IPAddress(string_ip)) == ipaddr.IPv4Address or \
          type(IPAddress(string_ip)) == ipaddr.IPv6Address:
        return string_ip
      else:
        return None
    except ValueError:
      return None


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
      return self.location.get('city').get('names').get('en') or ''
    except:
      return ''


  def get_country(self):
    '''return country from dict geolocation'''
    try:
      return self.location.get('country').get('iso_code') or ''
    except:
      return ''


  def get_state(self):
    '''return state from dict geolocation if country is US'''
    country = self.get_country()
    state = ''
    if country == 'US':
      try:
        state = self.location.get('subdivisions') or ''
        if state:
          state = state[0].get('iso_code')
        return state
      except:
        return ''
    else:
      return state


  def get_latitude(self):
    '''return latitude from dict geolocation'''
    try:
      return self.location.get('location').get('latitude') or None
    except:
      return None


  def get_longitude(self):
    '''return longitude from dict geolocation'''
    try:
      return self.location.get('location').get('longitude') or None
    except:
      return None

