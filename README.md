# About
This project is the sixth and final project for Udacity's Fullstack Web Development Nanodegree.  The goal of this project is to serve the Catalog App (Project Four) on an Amazon Lightsail Ubuntu server.

The project is named Linux Deployment for Catalog App. As of the time of writing this, it is viewable from the URL of its public IP Address http://34.200.217.14.  The main webpage serves information from the catalog database.  This stores very categories, and associated items for each category. For example, the item 'Shinguard' is associated with the category 'Soccer'. 


# Getting Started
To recreate my environment, you will a modern browser and a unix-like terminal.  I used the most updated version of Google Chrome.  As my time of writing this, that is version 67.0.3396.99.

# Execution
To view the web app, open up your browser and go to the URL http://34.200.217.14. The page should render and show the Catalog App.

# Entering my AWS Lightsail Ubuntu server:
To view the configuration of my server, you will need your unix-like terminal and my private key, which is only available to the grader.  So if you're not the grader, feel free to skip this section, otherwise if you want to learn how to log into any server, please continue reading.

Open your terminal.  The following steps will help you move my provided private key to your `~/.ssh` directory.  You may need to make the `~/.ssh` directory with the following command in your terminal.  It is also possible the terminal will tell you the folder already exists.

```
$ mkdir ~/.ssh
```
Navigate in your terminal with `cd` to the folder with `students_private_key` and run the following command.
```
$ mv students_private_key ~/.ssh
```
We will now ensure the `students_private_key` is protected.
**Please run the following to secure my private key.**

```
$ cd ~/.ssh
$ chmod 700 ~/.ssh
$ chmod 600 ~/.ssh/students_private_key
```

Now we have placed the private key in a safe folder `~/.ssh` (chmod 700) and it is also only viewable and writeable by our root user (chmod 600).

Let's jump into my Lightsail server!

This server is only configured to accept SSH connections on port 2200.  I have constructed a sudoer user `grader` so that you can navigate around the files as you please.  The following will log you into my server.

```
$ ssh grader@34.200.217.14 -p 2200 -i ~/.ssh/students_private_key
```

And voilà, you're in.

### Server Configurations
As briefly mentioned above, using the built in firewall `ufw`, I've restricted this server to only be accessible through `SSH` connections on the port 2200.  I have also opened ports 80 for `HTTP` and 123 for `NTP`.  PasswordAuthentication in`etc/ssh/sshd_config` has been set to `no`.  I have blocked access to my `.git` directory using a directive in my `/var/www/html/.htaccess` file.

# Required 3rd Party Software

The project is running on [Apache2](https://httpd.apache.org/docs/2.4/) server software in conjunction with [mod_wsgi](https://modwsgi.readthedocs.io/en/develop/) which is a go between my python application and Apache2.  The Catalog App uses [Postgresql](https://www.postgresql.org/) database software to store the category data.

### Python Library Dependencies

Successful execution requires the standard python library for python2.  I am using Ubuntu version 16.04.  I am running this in a Amazon Lightsail server. If you are the grader, please see the above if you want to replicate my environment. The Catalog App has the following dependencies:

I will now list out the packages and the versions that I have installed as of the time of me writing this.  To install any of the following packages, simply open a new bash terminal and write `$ pip install {package}`, of course replacing `{package}` with whatever you desire, like so `$ pip install flask`.  Depending on your user permissions, you may need to try to following to successfully install packages. `$ pip install {package} --user`.  If that doesn't work, one may need to use the following: `$ sudo pip install {package}`.
```
>>> flask.__version__
'1.0.2'
>>> httplib2.__version__
'0.11.3'
>>> requests.__version__
'2.18.4'
>>> oauth2client.__version__
'4.1.2'
>>> sqlalchemy.__version__
'1.2.7'
```

If you're having issues with a particular library, you can install any library's version with the following command. The below example is installing a specific version of flask, please change the package name to whatever suits your needs, and note that if you needed `--user` or `sudo` in the install, you'll need it down here too.

```
$ pip install flask==1.0.2 --user
```

Finally, if you want the quick and easy way to install every package as I have, just clone this repo and run the following once in the folder of the repo.
```
$ pip install -r requirements.txt
```

# JSON API Endpoints:
This project serves API endpoints.  To view all of the categories and their associated fields, send a GET request to:
```
http://34.200.217.14/sports/JSON/
```

To view all of the items for a category of name 'categoryname', send a GET request to:
```
http://34.200.217.14/sports/categoryname/JSON/
```

To view all a single item of name 'itemname' for a category of name 'categoryname', send a GET request to:
```
http://34.200.217.14/sports/categoryname/items/itemname/JSON/
```

# Resources used:
I have used [Stackoverflow](https://www.stackoverflow.com), a programming Q&A messageboard to help with configuration of virtually every part of this project. [Ask Ubuntu](https://askubuntu.com/) was also priceless in my configurations particularly as related to file permissions and firewall related tasks.  A special thanks to the askers and answerers on these websites.

The following websites were also helpful to me in my configuration:
https://optimalbi.com/blog/2016/03/31/apache-meet-python-flask/
https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-ubuntu-16-04
http://flask.pocoo.org/docs/0.12/deploying/mod_wsgi/

# Contributing
I am not looking for contributors as of the time of me writing this.
# Bugs
Please reach out to the project's author Jack Dealtrey at github@macavich for issues!
