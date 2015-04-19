Step guide explaining how to run the web application, tests and coverage.

* ``cd /vagrant``
* Run the command ``vagrant up``
     * Vagrant configuration base on ubuntu/trusty64
* Run the command ``vagrant ssh``
* ``cd /vagrant/tradyfit``
* For launching the web application:
    - ```python manage.py runserver --host 0.0.0.0```
    - Open a browser and go to localhost:5000
* Unit and Integration tests:
    * For launching the test suit locally, run:
        - ```python manage.py test```
    * Tests also run in a CI every time code is pushed to Github in drone.io
        - https://drone.io/github.com/rosariomgomez/tradyfit
* Functional tests:
    * For launching the test suit locally, run:
        - ```python manage.py acceptance_test```
        - First, in the host machine a webdriver server needs to be up:
          - ```java -jar selenium-server-standalone-2.45.0.jar```
* For getting the code coverage:
     - ```python manage.py test --coverage```
     - ```open tmp/coverage/index.html``` to see the report