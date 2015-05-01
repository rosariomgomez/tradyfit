# Deployment

In this section I explain the deployment workflow, the production environment and some problems I've encountered during the process of deploying the application on Heroku. I've also set up Opbeat for error logging in production.

## Deployment set up
- The configuration settings for Heroku are specified on the [HerokuConfig](https://github.com/rosariomgomez/tradyfit/blob/master/vagrant/tradyfit/config.py#L78). In Heroku the config vars need to be [set up](https://devcenter.heroku.com/articles/config-vars).
- In order to automate repetitive tasks during deployment (create/update database, insert categories...), I've added the [deploy command](https://github.com/rosariomgomez/tradyfit/blob/master/vagrant/tradyfit/manage.py#L65) to manage.py
- Heroku does not provide a web server for the application, expecting the application to start its own server. The web server Flask uses for development only processes a single request at a time, so it's not a good solution for production.  
    -  I've installed [Gunicorn](http://gunicorn-docs.readthedocs.org/en/latest/) as it's the one [recommended by Heroku](https://devcenter.heroku.com/articles/python-gunicorn). To run the application locally with this server:
        +  gunicorn manage:app -b 0.0.0.0:5000
    -  In the [Procfile file](https://github.com/rosariomgomez/tradyfit/blob/master/vagrant/tradyfit/Procfile) is where I tell Heroku to start the web server.


## Deployment workflow
- Verify all the tests are passing locally 
- Push the code to Github. This automatically launches a build in Travis
- If the build passes, I push the code to Heroku running the following commands:  
    - heroku maintenance:on _(put the app offline and show a maintenance page)_
    - git subtree push --prefix vagrant/tradyfit heroku master _(because the application doesn’t reside on the top of the git repo)_  
    - heroku run python manage.py deploy _(upgrade db, insert categories...)_
    - heroku restart _(restart the app after the deploy to start cleanly)_
    - heroku maintenance:off _(put the app back online)_  
  

## Production environment
- python-2.7.9
- PostgreSQL 9.3.5
- PostGIS 2.1
- The rest of dependencies (with their version) are specified on the requirements.txt file  
  
  
## Some useful commands on Heroku console
- Running the shell: heroku run python manage.py shell
- Connect to the database: heroku pg:psql
- See the application logs: heroku logs

  
## Opbeat
In order to have real time information about errors occurring in the application, I configured [Opbeat](https://opbeat.com). After [setting it up](https://opbeat.com/docs/articles/error-logging-in-flask/) it automatically captures HTTP 500 errors occurring in the application.  

I also send some additional events for capturing errors related to the [REST API's rate limits](https://github.com/rosariomgomez/tradyfit/blob/master/vagrant/tradyfit/app/public_api_1_0/errors.py#L16) and 3rd party services: [Facebook login](https://github.com/rosariomgomez/tradyfit/blob/master/vagrant/tradyfit/app/auth/views.py#L68), [Amazon S3](https://github.com/rosariomgomez/tradyfit/blob/master/vagrant/tradyfit/app/helpers.py#L27) (connect, upload and delete) and [GoogleV3 geolocation API](https://github.com/rosariomgomez/tradyfit/blob/master/vagrant/tradyfit/app/geolocation.py#L65).  
  
  
## Troubleshooting
- Heroku [install by default](https://devcenter.heroku.com/articles/heroku-postgresql#version-support-and-legacy-infrastructure) PostgreSQL version 9.4, but PostGIS is [only supported with Postgres 9.3](https://devcenter.heroku.com/articles/heroku-postgres-extensions-postgis-full-text-search#postgis), so I needed to specify the version for the installation:  
```
heroku addons:add heroku-postgresql:standard-yanari --version 9.3
```

- Problem with Werkzeug version 0.9.4:  
In development I was using python 2.7.6 while in production the python version is 2.7.9. When I started the project, I had a [problem with Werkzeug version 0.10](http://tradyfit.readthedocs.org/en/latest/notes/) and I rolled back to v.0.9.4. But that version had this [bug](https://github.com/mitsuhiko/werkzeug/issues/537) for versions of python > 2.7.6. So I updated to Werkzeug to version 0.9.5.


