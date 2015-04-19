Database model definition and a guide to check how to create a database, make a migration, ...

## Database model

![DB schema](img/tradyfit_db_model.png)

<h4>Users table</h4>
- Primary key: id
- Relationships:    
    - items:  
        - A query to the resource is returned when a user is loaded (``lazy='dynamic'``)  
        - When a user is deleted, all her items are also deleted (``cascade='all, delete-orphan'``)      
    - msgs_sent:  
        - A query to the resource is returned when a user is loaded (``lazy='dynamic'``)  
        - Specific relation: ``primaryjoin="User.id==Message.sender_id"``  
    - msgs_received:  
        - A query to the resource is returned when a user is loaded (``lazy='dynamic'``)  
        - Specific relation: ``primaryjoin="User.id==Message.receiver_id"``  
    - msgs_unread:  
        - Unread messages are loaded on demand the first time they are accessed (``lazy='select'``)  
        This is very important because we will be calling len(current_user.msg_unread) to display an "Unread notifications" icon in the NavBar (printed in each request when the user is logged in) so we need to make sure to not trigger a query each time we access the resource  
        - Specific relation: ``primaryjoin="and_(User.id==Message.receiver_id, Message.unread==True)"``  

<h4>Messages:</h4>  
- Primary key: id  
- Deletes for foreign keys: sender_id, receiver_id and item_id are set to ``ondelete='SET NULL'``, so if a user or item is deleted the message is still available.  


## Database creation  
From the command line on the VM go to psql and create the dev and test databases:
```>> psql```
```>> CREATE DATABASE tradyfit_dev;```
```>> CREATE DATABASE tradyfit_test;```

## Set up
Since the production app will be using a Postgres DB, it is a good idea to develop locally on the same database.  
In order to communicate the postgres database with the flask application, we need to use the following libraries:  
- psycopg2: Python adapter for Postgres  
- flask-sqlalchemy: Python ORM (Object-relational mapping). Flask wrapper for SQLAlchemy. SQLAlchemy is a relational database framework that supports several database backends.  
- Flask-Migrate: for database migrations (it makes use of Alembic)  

## Model definition
Tables are defined in models.py file

## config.py
In the config.py file we specify the URI for the database we will be using depending on the environment the application is running.

Amongst other configurations, we specify:
```SQLALCHEMY_COMMIT_ON_TEARDOWN = True```  
This will make automatic database commits at the end of each request we have modified the db.session.

## Run database operations from the shell
Thank you to the method make_shell_context() in manage.py, we can query the database tables from the console using the SQLAlchemy syntax. Some examples:  
```>> python manage.py shell```  
- Adding default values to DB from file (such as sports categories):  
```>> Category.insert_categories()```  
- Querying rows:  
```>> User.query.all()```  
```>> user1 = User.query.filter_by(username='emily34').first()```  
- Deleting:  
```>> db.session.delete(user1)```  
```>> db.session.commit()```  

## Migrations
Before database migrations can be maintained, it is necessary to create a migration repository with the init subcommand:   
```>> python manage.py db init```  
This command creates a migration folder, where all the migration scripts will be stored.  
  
Every time we make a change on the db schema, we need to run a db migration. We can use the db migrate subcommand that will generate an automatic migration script:  
```>> python manage.py db migrate -m “change we’ve made on the database”```  

Then, we should review the script to see if it was correctly generated. And finally we apply the change to the database with the db upgrade command:  
```>> python manage.py db upgrade```
