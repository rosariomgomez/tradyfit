# -*- coding: utf-8 -*-
from mock import patch
from base import UnitTestCase
from app.geolocation import Geolocation

VALID_IPv4_US = '76.102.12.224' #Mountain View IP
VALID_IPv4_ES = '80.28.239.170' #Madrid IP
VALID_IPv6 = 'FF01:0:0:0:0:0:0:101' #from RFC4291
LOCAL_IP = '127.0.0.1'
PROXY_IP = '221.10.40.238:80'
STRING_IP = 'not an address'

class GeolocationTestCase(UnitTestCase):

  def test_validate_ip(self):
    self.assertTrue(Geolocation.validate_ip(VALID_IPv4_US))
    self.assertTrue(Geolocation.validate_ip(VALID_IPv6))
    self.assertFalse(Geolocation.validate_ip(STRING_IP))

  def test_get_location(self):
    self.assertTrue(type(Geolocation.get_location(VALID_IPv4_US)) == dict)
    self.assertTrue(Geolocation.get_location(LOCAL_IP) == None)

  def test_get_valid_city(self):
    geo_obj = Geolocation(VALID_IPv4_US)
    r, city = geo_obj.get_city()
    self.assertTrue(r and city == 'Mountain View')

  def test_get_invalid_city(self):
    geo_obj = Geolocation(STRING_IP)
    r, city = geo_obj.get_city()
    self.assertTrue(r is False and city == None)

  def test_get_valid_country(self):
    geo_obj = Geolocation(VALID_IPv4_ES)
    r, country = geo_obj.get_country()
    self.assertTrue(r and country == 'ES')

  def test_get_invalid_country(self):
    geo_obj = Geolocation(PROXY_IP)
    r, country = geo_obj.get_country()
    self.assertTrue(r is False and country == None)

  def test_get_state_US(self):
    geo_obj = Geolocation(VALID_IPv4_US)
    r, state = geo_obj.get_state()
    self.assertTrue(r and state == 'CA')

  def test_get_state_noUS(self):
    geo_obj = Geolocation(VALID_IPv4_ES)
    r, state = geo_obj.get_state()
    self.assertTrue(r is False and state == None)

  @patch('app.geolocation.Geolocation.get_country', return_value=(True, 'US'))
  def test_get_invalid_state(self, mock_country):
    geo_obj = Geolocation(STRING_IP)
    r, state = geo_obj.get_state()
    self.assertTrue(r is False and state == None)

  def test_get_none_state(self):
    geo_obj = Geolocation(VALID_IPv4_US)
    #manually modify the entrance for state value
    geo_obj.location['subdivisions'] = None
    r, state = geo_obj.get_state()
    self.assertTrue(r is True and state == None)

  def test_get_valid_latitude(self):
    geo_obj = Geolocation(VALID_IPv4_US)
    r, latitude = geo_obj.get_latitude()
    self.assertTrue(r and latitude == 37.386)

  def test_get_invalid_latitude(self):
    geo_obj = Geolocation(STRING_IP)
    r, latitude = geo_obj.get_latitude()
    self.assertTrue(r is False and latitude == None)

  def test_get_valid_longitude(self):
    geo_obj = Geolocation(VALID_IPv4_US)
    r, longitude = geo_obj.get_longitude()
    self.assertTrue(r and longitude == -122.0838)

  def test_get_invalid_longitude(self):
    geo_obj = Geolocation(STRING_IP)
    r, longitude = geo_obj.get_longitude()
    self.assertTrue(r is False and longitude == None)

