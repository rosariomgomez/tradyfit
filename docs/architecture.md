# Architecture design

This section contains explanations of the decisions taken during building the
application.


## Search engine for items

I've implemented the full text indexing search via [SQLAlchemy-Searchable](https://sqlalchemy-searchable.readthedocs.org/en/latest/index.html) because it can be neatly integrated into Flask-SQLAlchemy using SearchQueryMixin class. It makes use of PostgreSQL built-in TSVectorType class to vectorize string columns and create the search vectors.

<h3>How to perform a search</h3>

SearchQueryMixin provides the search method for ItemQuery. You can chain calls just like when using query filter calls.  

In the following example, we search for the first 50 items that contain the word ‘ball’ ordered by creation time:
```  
Item.query.search('ball').order_by(Item.timestamp.desc()).limit(50).all()
```

<h3>Notes</h3>
 - I followed the documentation for [Flask-SQLAlchemy integration](https://sqlalchemy-searchable.readthedocs.org/en/latest/integrations.html)
 - Modified generated migration script to update the [search triggers](https://sqlalchemy-searchable.readthedocs.org/en/latest/alembic_migrations.html). Check the [applied migration script](https://github.com/rosariomgomez/tradyfit/blob/master/vagrant/tradyfit/migrations/versions/35b2b9f7b64e_added_search_vector_to_items_table.py) for reference.

<h3>Pitfalls</h3>
I did a first implementation using Whoosh via [Flask-WhooshAlchemy](https://pythonhosted.org/Flask-WhooshAlchemy/).
Problem: it stores the indices in files, so not compatible with Heroku deployment restrictions for accessing the filesystem.


## Nearby searches

When a user is logged in and has latitude and longitude values set up, the search's results are ordered by nearby location. The execution of a raw SQL query would be very expensive in processing, that's why I used the geographic extension [PostGIS](http://postgis.net/) for PostgreSQL. I performed the queries with the support of the GeoAlchemy2 library.  

The latitude, longitude user's values are converted to a [WKB element](http://en.wikipedia.org/wiki/Well-known_text) geometry point. The search results are ordered by the nearest neighbors' items to the user:  
```
Item.query.search(query).order_by(Item.location.distance_box(user_loc))
```

<h3>Notes</h3>
- I modified the automatic generated migration script from flask-migrate. Check the [migration applied](https://github.com/rosariomgomez/tradyfit/blob/master/vagrant/tradyfit/migrations/versions/49b6d8f6d4c8_added_geoalchemy_point_to_search_items_.py) for reference.
- Needed to enable PostGIS on [.travis.yml](https://github.com/rosariomgomez/tradyfit/blob/master/.travis.yml#L18) file for running tests on Travis-CI.
- More information about spatial queries, on the GeoAlchemy [documentaion](http://geoalchemy-2.readthedocs.org/en/latest/orm_tutorial.html#spatial-query)


## External services

<h3>Facebook login</h3>
The reason of implementing a social login instead of a personal sign up system is to avoid storing sensible users’ information (passwords). I’ve integrated the service using [flask-oauthlib](https://flask-oauthlib.readthedocs.org/en/latest/) that implements Oauth.

I’ve created the __auth blueprint__ to include all the code related with the authentication process.
The [config.py](https://github.com/rosariomgomez/tradyfit/blob/master/vagrant/tradyfit/config.py#L12) file contains the necessary set up for the service. The passwords and API keys are set up as environment variables.

- The view code was created following the flask-oauthlib [example provided on github](https://github.com/lepture/flask-oauthlib/blob/master/example/facebook.py)


<h3>Amazon S3</h3>
Amazon S3 is a popular and reliable storage option for storing files. I've used it to store user avatars and product images. I detailed how to configure it [here](https://github.com/rosariomgomez/tradyfit/wiki/Notes#amazon-s3-configuration).

- I used [boto](https://github.com/boto/boto) Python library for handling the S3 upload.  
- Security checks for file uploading (useful [documentation](http://flask.pocoo.org/docs/0.10/patterns/fileuploads/)):
    - __Maximum size:__ Specified in `config.py` file via `MAX_CONTENT_LENGTH` constant. If user tries to upload a file bigger than 3MB, a 413 (File too large) error is raised. I capture it via an [error handler](https://github.com/rosariomgomez/tradyfit/blob/master/vagrant/tradyfit/app/main/errors.py#L6) and redirect to the item form.
    - __Allowed file extensions:__ Verified via FileAllowed method from flask_wtf.file library in ItemForm validators.
    - __Filename extension:__ In order to save the image in S3 with the correct extension, we need to extract it from the filename. Although I'm not using the filename provided from the user as destination filename, I use werkzeug.secure_filename() to extract the filename extension (for example it will remove ../..).

<h3>GoogleV3 geocoder service</h3>
I use this [Google service](https://developers.google.com/maps/documentation/geocoding/) when geolocation information cannot be extracted from user's IP and the user manually enters her location on the profile page. Full explanation of the process on next section.

## Geolocation
The geolocation data is stored in the User class and consist of: country, state, city, latitude and longitude.
All this information is extracted from the user's IP, by looking into the [Free GeoLite2 City](http://dev.maxmind.com/geoip/geoip2/geolite2/) MaxMind DB (a binary file format that stores data indexed by IP address subnets).
I use the [maxminddb python library](https://github.com/maxmind/MaxMind-DB-Reader-python) to interact with the MaxMind DB in the application.

<h3>Extracting user's IP security concerns</h3>
In the [get_ip()](https://github.com/rosariomgomez/tradyfit/blob/master/vagrant/tradyfit/app/auth/views.py#L115) method, I call to [request.access_route()](https://github.com/mitsuhiko/werkzeug/blob/bf2456f11972f00b0156aa4f9a7f7d2cd7674970/werkzeug/wrappers.py#L608) to get the user's IP, by accessing to the first value of the list of IP addresses (list containing from the client IP to the last proxy server).  

_Side note:_ request.access_route() method uses the ``HTTP_X_FORWARDED_FOR`` header if available, if not, the method returns the ``REMOTE_ADDR``. In my case REMOTE_ADDR will return the proxy server address ([Heroku](https://devcenter.heroku.com/articles/http-routing#heroku-headers)) instead of the actual user making the request. So in my method, if I cannot access to the first element of the array, I return None as IP (to avoid store Heroku IP as user address). 

Retrieving the user's IP from the request header raises the security problem that the user could modify the HTTP_X_FORWARDED_FOR value on its request. See the following code as example:
```
def get_ip():
 return request.access_route[0]

@main.route('/')
def index():
  return 'Your IP is ' + get_ip()
```

The returned value of a malicious request:
```
~$ curl -H "X-Forwarded-For: <script>alert(1)</script>" http://0.0.0.0:5000
Your IP is <script>alert(1)</script>
```

In order to avoid IP Spoofing, I first check whether or not this string represents a valid IP address (IPv4 or IPv6) by using the ``ipaddr`` library (which is also used by the maxminddb library, so we have it already installed):
```
>> import ipaddr
>> ipaddr.IPAddress('127.0.0.1')
IPv4Address('127.0.0.1')
>> ipaddr.IPAddress('foo')
ValueError: 'fooo' does not appear to be an IPv4 or IPv6 address
```

<h3>When geolocation data is not available</h3>
If the IP doesn’t match any geolocation information or for example the IP belongs to a proxy, the nearby search will not be performed.
To solve this problem, the user can manually modify their location on their profile settings.

Country and State fields are populated from Country and State classes, coming from the [geonamescache](https://github.com/yaph/geonamescache) python library. City should be filled by the user.

Latitude and longitude attributes will be extracted from the city, state and country information by using the [geopy](https://github.com/geopy/geopy) library to interact with the [GoogleV3 geocoder service](https://developers.google.com/maps/documentation/geocoding/).
I chose Google geocoder service because has a free API (with 2500 requests/24 hours), it's accurate and doesn't give me as much time outs as other services I tested.
Example call:
```
>> geolocator.geocode('Mountain View, CA, US')
Location((37.3855745, -122.08205, 0.0))
```