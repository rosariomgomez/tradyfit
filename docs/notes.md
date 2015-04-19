A place to collect all the gotchas and troubles encountered (and solved!)

# Installation problems
<h3> Werkzeug Version 0.10 package</h3>
It has numerous changes into the reloader. One change is that a default polling reloader is used. When I run the server, instead of saying "Restarting with reloader" it said "Restarting with stat" and then it crashed. I rolled back to previous version and fixed the problem.
More info on [this SO thread](http://stackoverflow.com/questions/28241989/flask-app-restarting-with-stat)

<h3> Ubuntu trusty (VM provided by Udacity)/precise (VM that runs in drone.io)/ pg_config.sh and requirements.txt</h3>
I had some dependencies problems after installing SQLAlchemy-Searchable.  
The default VM config provided by Udacity installed python-sqlalchemy via `apt-get install`.  
`python-sqlalchemy` package version for Ubuntu trusty and precise, doesn't contain a [module named "annotation"](http://packages.ubuntu.com/precise/all/python-sqlalchemy/filelist) that is a dependency for `sqlalchemy_utils` (which is a dependency for `sqlalchemy_searchable`) and for instance [the build in drone.io failed](https://drone.io/github.com/rosariomgomez/tradyfit/19).  
I fixed it installing SQLAlchemy via pip install instead of apt-get (added to requirements.txt and removed from pg_config.sh).  

# Amazon S3 configuration
- Create an account on http://aws.amazon.com/
- Create S3 buckets for production and development
- Create folders inside the bucket to store different data
- Create two Identity and Access Management users (IAM) different from the AWS account user for security reasons (as recommended [here](http://docs.aws.amazon.com/IAM/latest/UserGuide/Using_WorkingWithGroupsAndUsers.html))
  - [AWS IAM home](https://console.aws.amazon.com/iam/home#home)
- Create Policies to let those users programmatically read and write permissions on the S3 buckets:
  - One user can only be attached to 2 polices.
  - The users will also need access to the s3:PutObjectAcl API, as once the image is uploaded, the permission will be set to public-read.
  - [Policy example](http://stackoverflow.com/questions/21892437/s3-policy-to-allow-a-user-to-put-get-delete-and-modify-permissions)
- Attach the policies to the users (one user for production, another for dev and test).
- From the "Security Credentials" tab, create an Access Key. Set the Access key ID and Secret Access key as environment variables: S3_KEY, S3_SECRET.


# Forms

<h3> Uploading files</h3>
- Remember to set the enctype of the HTML form to multipart/form-data:
``<form action="" method=post enctype=multipart/form-data>``

- In order to avoid the upload of big images, I've set up the ``MAX_CONTENT_LENGTH`` variable in the ``config.py`` file. If a file with size bigger than this variable is tried to be uploaded, a 413 error will be raised, which is captured and a proper template is displayed.
__Note__: I've tried to redirect instead of render the template but it didn't work. Not quite sure why...

<h3>CSRF protection</h3>
- Remember to include ``{{ form.hidden_tag() }}`` that will get replaced with a hidden field that implements the CSRF prevention (handled by Flask-WTF) when WTF_CSRF_ENABLED is True (by default)