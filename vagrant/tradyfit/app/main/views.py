from flask import current_app
from . import main

@main.route('/')
def index():
    return '<h1>Hello World!</h1>'