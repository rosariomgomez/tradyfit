
apt-get -qqy update
apt-get -qqy install tree
apt-get -qqy install postgresql python-psycopg2
apt-get install postgis postgresql-9.3-postgis-2.1
apt-get -qqy install python-dev
apt-get -qqy install python-flask
apt-get -qqy install python-pip
su postgres -c 'createuser -dRS vagrant'
su vagrant -c 'createdb tradyfit_dev'
su vagrant -c 'createdb tradyfit_test'
sudo -u postgres psql -c "CREATE EXTENSION postgis; CREATE EXTENSION postgis_topology;" tradyfit_dev
sudo -u postgres psql -c "CREATE EXTENSION postgis; CREATE EXTENSION postgis_topology;" tradyfit_test