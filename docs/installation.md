This section contains all the programs, packages and tools needed in order to run the code in your own machine.

1. [Install VirtualBox](https://www.virtualbox.org/wiki/Downloads)

2. [Install Vagrant](http://www.vagrantup.com/downloads.html)

3. `git clone https://github.com/rosariomgomez/tradyfit.git`

4. `cd tradyfit`

5. `vagrant up`
    Check out the `Vagrantfile` and tradyfit/requirements.txt while this starts up.

6. `vagrant ssh`
    At this point you should be SSH'd into a shiny new Ubuntu Trusty VM. The
    `tradyfit` directory you started with should be synced to `/vagrant`.

    If not, run `vagrant reload` and `vagrant ssh` again. You should see the
    shared folder now.

7. `cd /vagrant/tradyfit`