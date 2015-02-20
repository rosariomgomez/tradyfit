from flask import current_app, render_template
from . import main

@main.route('/')
def index():
    return render_template('index.html')