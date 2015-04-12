# -*- coding: utf-8 -*-
import unittest
from mock import patch
from app import create_app, db
from app.geolocation import Geolocation


class GeolocationTestCase(unittest.TestCase):
  def setUp(self):
    self.app = create_app('testing')
    self.app_context = self.app.app_context()
    self.app_context.push()
    db.create_all()

  def tearDown(self):
    db.session.remove()
    db.drop_all()
    self.app_context.pop()

  def test_validate_ip(self):
    #valid IPv4
    self.assertTrue(Geolocation.validate_ip('76.102.12.224'))
    #valid IPv6 address (from RFC4291)
    self.assertTrue(Geolocation.validate_ip('FF01:0:0:0:0:0:0:101'))
    #invalid parameter
    self.assertFalse(Geolocation.validate_ip('not an address'))

  def test_get_location(self):
    self.assertTrue(type(Geolocation.get_location('76.102.12.224')) == dict)
    self.assertTrue(Geolocation.get_location('127.0.0.1') == None)

  def test_get_valid_city(self):
    geo_obj = Geolocation('76.102.12.224')
    r, city = geo_obj.get_city()
    self.assertTrue(r and city == 'Mountain View')

  def test_get_invalid_city(self):
    geo_obj = Geolocation('not an addres')
    r, city = geo_obj.get_city()
    self.assertTrue(r is False and city == None)

  def test_get_valid_country(self):
    geo_obj = Geolocation('80.28.239.170')
    r, country = geo_obj.get_country()
    self.assertTrue(r and country == 'ES')

  def test_get_invalid_country(self):
    #proxy IP
    geo_obj = Geolocation('221.10.40.238:80')
    r, country = geo_obj.get_country()
    self.assertTrue(r is False and country == None)

  def test_get_state_US(self):
    geo_obj = Geolocation('76.102.12.224')
    r, state = geo_obj.get_state()
    self.assertTrue(r and state == 'CA')

  def test_get_state_noUS(self):
    #spain IP
    geo_obj = Geolocation('80.28.239.170')
    r, state = geo_obj.get_state()
    self.assertTrue(r is False and state == None)

  @patch('app.geolocation.Geolocation.get_country', return_value=(True, 'US'))
  def test_get_invalid_state(self, mock_country):
    geo_obj = Geolocation('not an address')
    r, state = geo_obj.get_state()
    self.assertTrue(r is False and state == None)

  def test_get_none_state(self):
    geo_obj = Geolocation('76.102.12.224')
    #manually modify the entrance for state value
    geo_obj.location['subdivisions'] = None
    r, state = geo_obj.get_state()
    self.assertTrue(r is True and state == None)

  def test_get_valid_latitude(self):
    geo_obj = Geolocation('76.102.12.224')
    r, latitude = geo_obj.get_latitude()
    self.assertTrue(r and latitude == 37.386)

  def test_get_invalid_latitude(self):
    geo_obj = Geolocation('not an addres')
    r, latitude = geo_obj.get_latitude()
    self.assertTrue(r is False and latitude == None)

  def test_get_valid_longitude(self):
    geo_obj = Geolocation('76.102.12.224')
    r, longitude = geo_obj.get_longitude()
    self.assertTrue(r and longitude == -122.0838)

  def test_get_invalid_longitude(self):
    geo_obj = Geolocation('not an addres')
    r, longitude = geo_obj.get_longitude()
    self.assertTrue(r is False and longitude == None)

