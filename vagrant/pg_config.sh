
apt-get -qqy update
apt-get -qqy install tree
apt-get -qqy install postgresql python-psycopg2
apt-get -qqy install python-flask python-sqlalchemy
apt-get -qqy install python-pip
createuser -dRS vagrant -U postgres
createdb tradyfit_dev -U vagrant
createdb tradyfit_test -U vagrant
