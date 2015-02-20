TradyFit
==========

## Introduction
TradyFit allows users to buy/sell sports gear

## Installation
* Install Vagrant
* Install VirtualBox
* Clone this git repository

## How to run the code
* Run the command ``vagrant up``
     * Vagrant configuration base on ubuntu/trusty64
* Run the command ``vagrant ssh``
* ``cd vagrant/tradyfit``
* For launching the web application:
    - ```python manage.py runserver --host 0.0.0.0
    - Open a browser and go to localhost:5000
* For launching the unit tests
    - ```python manage.py test```