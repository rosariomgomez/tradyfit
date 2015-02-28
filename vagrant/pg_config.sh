
apt-get -qqy update
apt-get -qqy install tree
apt-get -qqy install postgresql python-psycopg2
apt-get -qqy install python-dev
apt-get -qqy install python-flask python-sqlalchemy
apt-get -qqy install python-pip
su postgres -c 'createuser -dRS vagrant'
su vagrant -c 'createdb tradyfit_dev'
su vagrant -c 'createdb tradyfit_test'
