# -*- coding: utf-8 -*-
from flask import jsonify
from . import public_api

def bad_request(message):
  response = jsonify({'error': 'bad request', 'message': message})
  response.status_code = 400
  return response