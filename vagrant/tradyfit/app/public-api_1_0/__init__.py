from flask import Blueprint

public_api = Blueprint('public-api', __name__)

from . import views, errors