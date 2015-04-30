# Administration

I've developed a basic administration interface where I can easily see users and items created on the aplication.

## Administration panel
Only admin user is allowed to access admin routes. Admin user is specified by setting up the is_admin attribute flag to True. The decorator [@admin_required](https://github.com/rosariomgomez/tradyfit/blob/master/vagrant/tradyfit/app/admin/decorators.py#L6) check for this authentication on admin views.