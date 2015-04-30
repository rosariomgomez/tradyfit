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

## Images

Here are the credits for the awesome images I've used, thank you all!!!

- [Coco Ho](https://www.flickr.com/photos/funeralbell/14982897679/) by [Steven Tyler PJs](https://www.flickr.com/photos/funeralbell/)
- [London 2012 Olympic Women's Triathlon Final](https://www.flickr.com/photos/idarrenj/7724435280/) by [Darren Johnson](https://www.flickr.com/photos/idarrenj/)
- [CU Swimming and Diving 3](https://www.flickr.com/photos/walkingthedeepfield/3030728199/) by [Angela Radulescu](https://www.flickr.com/photos/walkingthedeepfield/)
- [ODU v W&M Women's Soccer](https://www.flickr.com/photos/mobili/9543090542/) by [Mobilus In Mobili](https://www.flickr.com/photos/mobili/)
- [Baseball](https://www.flickr.com/photos/pmillera4/16880380082/) by [Peter Miller](https://www.flickr.com/photos/pmillera4/)
- [Women's Basketball](https://www.flickr.com/photos/tulanesally/3333629830) by [Tulane Public Relations](https://www.flickr.com/photos/tulanesally/)
- [Robot Model No. [7]](https://www.flickr.com/photos/ad7m/3597656172) by [Adam McIver](https://www.flickr.com/photos/ad7m/)
- [Cup of robots](https://www.flickr.com/photos/striatic/1276095/) by [hobvias sudoneighm](https://www.flickr.com/photos/striatic/) 
- [Bike](https://www.flickr.com/photos/moff/4863871155) by [Mathew Wilson](https://www.flickr.com/photos/moff/)
