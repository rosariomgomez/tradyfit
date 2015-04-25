# Design

For giving the application a nicer look I used the [Bootstrap](http://getbootstrap.com/) client-side framework via the package [Flask-Bootstrap](http://pythonhosted.org/Flask-Bootstrap/) which makes the integration with Flask easier.  

For getting the bootstrap functionallity, templates extend from bootstrap/base.html template:  
```
{% extends "bootstrap/base.html" %} 
```

## Mobile requests

The design I've created for displaying the search results for desktop doesn't display nicely on mobile, so I decided to serve a different template depending on the device (desktop/mobile).  

For doing so, I've used the Flask-Mobility library, which simply checks before each request if the User Agent matches any of the devices of the mobile list, and if so, it changes the request object setting request.MOBILE = True.

So in the search_results.html template, I check this value and serve one or another item subtemplate accordingly:  

```
{% if request.MOBILE %}
  {% for item in items %}
    {% include "_item_box.html" %}
  {% endfor %}
{% else %}
  {% for item in items %}
    {% include "_item.html" %}
  {% endfor %}
{% endif %}
```
