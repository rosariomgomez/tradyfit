# Administration

I've developed a basic administration panel interface where I can easily see users and items created on the aplication.  

Only admin users are allowed to access admin routes. An admin user is specified by setting up her __is_admin__ attribute flag to True. The decorator [@admin_required](https://github.com/rosariomgomez/tradyfit/blob/master/vagrant/tradyfit/app/admin/decorators.py#L6) check for this authentication on the admin views.