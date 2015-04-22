TradyFit is an application that allows users to sell their sport gear. Potential buyers can search products by key-words. The results will be displayed by nearby location.  

It uses Python, Flask and PostgreSQL/PostGIS as framework.


## Installation requirements

The following steps will create an environment to run the code in your own machine:

1. [Install VirtualBox](https://www.virtualbox.org/wiki/Downloads)
2. [Install Vagrant](http://www.vagrantup.com/downloads.html)
3. Clone the repository: `git clone https://github.com/rosariomgomez/tradyfit.git`
4. Navigate to the cloned repository: `cd tradyfit`
5. Launch the virtual machine: `vagrant up` <br>Check out the `Vagrantfile` and `tradyfit/requirements.txt` while this starts up. They contain the necessary configuration of the VM and the libraries needed to run the code. You can also check the status of the dependencies at the [requires.io board](https://requires.io/github/rosariomgomez/tradyfit/requirements/?branch=master)
6. SSH into the VM: `vagrant ssh` <br>At this point you should be SSH'd into a new Ubuntu Trusty VM. The `tradyfit` directory you started with should be synced to `/vagrant`. If not, run `vagrant reload` and `vagrant ssh` again. You should see the shared folder now.
7. Go to the shared folder: `cd /vagrant/tradyfit`
  
  
## How to run the code

<h3>Launching the web application</h3>
From the command line, launch the webserver:
```
python manage.py runserver --host 0.0.0.0
```
Open a browser and go to the address http://localhost:5000

<h3>Running the tests</h3>
For launching the test suite locally, run:
```
python manage.py test
```
This will run unit, integration and functional tests.  

Functional tests use Selenium Webdriver, for instance, on the host machine a webdriver server needs to be up before running them (if the server is not running, these tests will be skipped). For launching the selenium server, run:
```
java -jar selenium-server-standalone-2.45.0.jar
```

If you want, you can only run the functional tests:
```
python manage.py acceptance_test
```

For getting the code coverage:
```
python manage.py test --coverage
```
To see the generated report, on the host machine:
```
open tmp/coverage/index.html
```



