This section contains explanations of the decisions taken during building the
application, such as, why use one library against another or why implementing
a feature in a certain way.


## Search engine for items

I've implemented this full text indexing search via [SQLAlchemy-Searchable](https://sqlalchemy-searchable.readthedocs.org/en/latest/index.html) because it can be neatly integrated into Flask-SQLAlchemy using SearchQueryMixin class. It makes use of PostgreSQL built-in TSVectorType class to vectorize string columns and create the search vectors.

<h3>How to perform a search</h3>

SearchQueryMixin provides the search method for ItemQuery. You can chain calls just like when using query filter calls.  

In the following example, we search for the first 50 items that contain the word ‘ball’ ordered by creation time:
```  
Item.query.search('ball').order_by(Item.timestamp.desc()).limit(50).all()
```

<h3>Important notes</h3>
 - Followed documentation for [Flask-SQLAlchemy integration](https://sqlalchemy-searchable.readthedocs.org/en/latest/integrations.html)
 - Modified generated migration script to update the [search triggers](https://sqlalchemy-searchable.readthedocs.org/en/latest/alembic_migrations.html). Check the [applied migration script](https://github.com/rosariomgomez/tradyfit/blob/master/vagrant/tradyfit/migrations/versions/35b2b9f7b64e_added_search_vector_to_items_table.py) for reference.

<h3>Pitfalls</h3>
I did a first implementation using Whoosh via [Flask-WhooshAlchemy](https://pythonhosted.org/Flask-WhooshAlchemy/).
Problem: it stores the indices in files, so not compatible with Heroku deployment restrictions for accessing the filesystem.


## Nearby searches

When a user is logged in and has latitude and longitude values, the search's results are ordered by nearby location. The execution of a raw SQL query will be very expensive in processing, that's why I used the PostGIS extension for PostgreSQL and I perform the queries via GeoAlchemy2 library.  

The latitude, longitude user's values are converted to a [WKB element](http://en.wikipedia.org/wiki/Well-known_text) geometry point. The search results are ordered by the nearest neighbors' items to the user:  
```
Item.query.search(query).order_by(Item.location.distance_box(user_loc))
```
For more information about spatial queries, check the GeoAlchemy [documentaion](http://geoalchemy-2.readthedocs.org/en/latest/orm_tutorial.html#spatial-query)

<h3>Important notes</h3>
- Modified the automatic generated migration script from flask-migrate. Check the [migration applied]() for reference.
- Needed to enable PostGIS on [.travis.yml](https://github.com/rosariomgomez/tradyfit/blob/master/.travis.yml#L18) file for running tests on Travis-CI.

## External services

<h3>Facebook login</h3>
The reason of implementing social login instead of a personal sign up system is to avoid storing sensible users’ information.

In order to interact with the 3rd party log in services, I’ve used flask-oauthlib that implements Oauth.

- Documentation: https://flask-oauthlib.readthedocs.org/en/latest/
- Github: https://github.com/lepture/flask-oauthlib
- The view code was created following the flask-oauthlib [example provided on github](https://github.com/lepture/flask-oauthlib/blob/master/example/facebook.py)

I’ve created the __auth blueprint__ to include all the code related with the authentication process.
The config.py file contains the necessary set up for the service. The passwords and API keys are set up as environment variables.

__User model:__

- fb_id (facebook_id): unique not nullable
- email: unique not nullable
- avatar_url: user's avatar url to S3 (avatar is pulled from facebook the first time the user log in and stored in an S3 bucket).

<h3>Amazon S3</h3>
Amazon S3 is a popular and reliable storage option for storing files. I've used it to store user avatars and product images. Details on how to configure it [here](https://github.com/rosariomgomez/tradyfit/wiki/Notes#amazon-s3-configuration).

- I use [boto](https://github.com/boto/boto) Python library for handling the S3 upload.  
- Security checks for file uploading (useful [documentation](http://flask.pocoo.org/docs/0.10/patterns/fileuploads/)):
    - __Maximum size:__ Specified in `config.py` file via `MAX_CONTENT_LENGTH` constant. If user tries to upload a file bigger than 3MB, a 413 (File too large) error is raised. I capture it via error_handler and redirect to the item form.
    - __Allowed file extensions:__ Verified via FileAllowed method from flask_wtf.file library in ItemForm validators.
    - __Filename extension:__ In order to save the image in S3 with the correct extension, we need to extract it from the filename. Although I'm not using the filename provided from the user as destination filename, I use werkzeug.secure_filename() to extract the filename extension (for example it will remove ../..).

<h3>GoogleV3 geocoder service</h3>
When geolocation information cannot be extracted from user's IP. Read more in the next section.

## Geolocation
The geolocation data is stored in the User class and consist of: country, state, city, latitude and longitude.
All this information is extracted from the user's IP, by looking into the [Free GeoLite2 City](http://dev.maxmind.com/geoip/geoip2/geolite2/) MaxMind DB (a binary file format that stores data indexed by IP address subnets).
I use the [maxminddb python library](https://github.com/maxmind/MaxMind-DB-Reader-python) to interact with the MaxMind DB in my application.

<h3>Extracting user's IP security concerns</h3>
I use the ``request.access_route`` [method](https://github.com/mitsuhiko/werkzeug/blob/bf2456f11972f00b0156aa4f9a7f7d2cd7674970/werkzeug/wrappers.py#L608) to get the user's IP by accessing to the first value of the list.
This method uses the ``HTTP_X_FORWARDED_FOR`` header if available, if not, it returns the ``REMOTE_ADDR`` (which will return the proxy server address (Heroku) instead of the actual user making the request)

The user can easily modify the HTTP_X_FORWARDED_FOR value on its request.
```
def get_ip():
 return request.access_route[0]

@main.route('/')
def index():
  return 'Your IP is ' + get_ip()
```

See the returned value of a malicious request:
```~$ curl -H "X-Forwarded-For: <script>alert(1)</script>" http://0.0.0.0:5000```
``Your IP is <script>alert(1)</script>``

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

Latitude and longitude attributes will be extracted from the city, state, country information by using the [geopy](https://github.com/geopy/geopy) library to interact with the [GoogleV3 geocoder service](https://developers.google.com/maps/documentation/geocoding/).
I chose Google geocoder service because has a free API (with 2500 requests/24 hours), it's accurate and doesn't give me as much time outs as other I tested.
Example:
```
>> geolocator.geocode('Mountain View, CA, US')
Location((37.3855745, -122.08205, 0.0))
```