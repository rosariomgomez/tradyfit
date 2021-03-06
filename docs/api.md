# REST API

This RESTful API gives public access to the items' resources via GET requests without user's authentication needed. The API responds with the application/json content-type.

## Implementation
The routes associated with the API are contained in the blueprint [public_api](https://github.com/rosariomgomez/tradyfit/tree/master/vagrant/tradyfit/app/public_api_1_0).  

Items need to be converted to JSON in order to be served by the API. This is achieved calling the item's property method [serialize](https://github.com/rosariomgomez/tradyfit/blob/master/vagrant/tradyfit/app/models.py#L209). Responses are easily generated by using Flask's jsonify() helper function.

## API Resources
| Resource URL                | HTTP Methods |  Description                   |
| --------------------------- | :---------:  | -------------------------------|
| /items/category/<category\> |  GET         |  All the items from category   |
| /items/search/<query\>      |  GET         |  All the items from the query  |
| /items/<int:id\>            |  GET         |  An item                       |
  

<h3>Example code to parse the API's response</h3>
```python
import json
import urllib
response = urllib.urlopen('http://tradyfit.herokuapp.com/public-api/v1.0/items/category/soccer')
resp = json.loads(response.read())
for item in resp['items']:
    print item['name']
    print item['description']
```
  

<h3>Possible returned status codes</h3>
| HTTP status code | Name | Description
------------- | ----------- | ------------------------------------------------
200           | OK          | The request was completed successfully
400           | Bad request | Invalid request. Response with 'message' field
404           | Not found   | The resource referenced in the URL was not found
429           | Rate limit exceeded | The request exceeds the rate limit
500           | Internal server error | An unexpected error has occurred
  

<h3>Errors</h3>
If an error occur, the response will be a JSON object with the keys 'error' and can also include a 'message'. Example of a response with an invalid search:
```
curl --header "Accept: application/json" --verbose http://tradyfit.com/public-api/v1.0/items/search/\<script\>hi

> GET /public-api/v1.0/items/search/<script>hi HTTP/1.1
> User-Agent: curl/7.36.0
> Accept: application/json
> 

< HTTP/1.0 400 BAD REQUEST
< Content-Type: application/json
< Content-Length: 63

{
  "error": "bad request",
  "message": "Not a valid search"
}
```
    
  
  
## Rate limiting
I've implemented a rate limit feature for trying to avoid been flooded with requests (as the designed API is public and doesn't need user authentication).  
I've used the [Flask-Limiter library](http://flask-limiter.readthedocs.org/en/stable/) with a _Fixed Window with Elastic Expiry_ rate limiting strategy, allowing 10 requests per resource per minute or 2 requests per resource per second: 
```
@limiter.limit("10/minute;2/second")
```
With this technique, for example, if the minute rate limit is breached, the attacker will be locked out of the resource for an extra 60 seconds after the last hit.  

The rate limit is specified by IP address. In the method [get_ipaddr()](https://github.com/alisaifee/flask-limiter/blob/master/flask_limiter/util.py#L8) Flask-limiter uses the value of request.access_route[0] or request.remote_addr to retrieve the user IP.
  
  
## Notes
- [404](https://github.com/rosariomgomez/tradyfit/blob/master/vagrant/tradyfit/app/main/errors.py#L13) and [500](https://github.com/rosariomgomez/tradyfit/blob/master/vagrant/tradyfit/app/main/errors.py#L23) error handlers were adapted to serve their responses (HTML or JSON) based on the format requested by the client (content negotiation technique).
- To avoid API requests to be rate limited during testing, I've implemented the [ip_whitelist()](https://github.com/rosariomgomez/tradyfit/blob/master/vagrant/tradyfit/app/public_api_1_0/item.py#L13) method, that uses the request_filter decorator. No rate limit will be applied for any API request that return True to this method.
