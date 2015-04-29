# Administration

I've developed a basic administration interface where I can easily see users and items created on the aplication. I've also set up Opbeat for error logging.

## Administration panel
Only admin user is allowed to access admin routes. Admin user is specified by setting up the is_admin attribute flag to True. The decorator [@admin_required](https://github.com/rosariomgomez/tradyfit/blob/master/vagrant/tradyfit/app/admin/decorators.py#L6) check for this authentication on admin views.

## Opbeat
After [setting it up](https://opbeat.com/docs/articles/error-logging-in-flask/) it automatically captures HTTP 500 errors that occur in the application.  

I also send some additional events for capturing errors related to the REST API's rate limits and 3rd party services: Facebook login, Amazon S3 and GoogleV3 geolocation API.  

Opbeat is based on [Raven](http://raven.readthedocs.org/en/latest/) (the oficial Python client for [Sentry](https://www.getsentry.com/docs/)).