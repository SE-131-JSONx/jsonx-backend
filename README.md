SE-131 Group Project - JSONx
[![Build Status](https://travis-ci.org/SE-131-JSONx/jsonx-be.svg?branch=cit)](https://travis-ci.org/SE-131-JSONx/jsonx-be)

Group 3
Ben Bierman  000124294
Salvatore Nicosia
Kyuhak Yuk
Ben Krig

To Run on the web, go to http://jsonx-fe.herokuapp.com/login  :
User Name: test, 
Password: test

Go to end of this file for abstract.


Other modules used are listed below; 
- sqlalchemy
- marshmallow
- sqlalchemy marshmallow
- flask sqlalchemy

###To run locally:

```
git clone
cd jsonx-be
virtualenv venv
source venv/bin/activate
cd src
pip install -r requirements.txt
python -m run 
```

Run tests:
```
nose2 -v
```

###Using Docker
Build with docker: 
```
git clone https://github.com/SE-131-JSONx/jsonx-be
cd jsonx-be
docker build -t jsonx-be .
```

Run in development mode: 
```
docker run -dt --name=jsonx-be -v $PWD:/app -p 5000:5000 -e 'WORK_ENV=DEV' jsonx-be
```

Run in production mode:
```
docker run -dt --restart=always --name=jsonx-be -p 5000:5000 -e 'WORK_ENV=PROD' jsonx-be
```

Remove the container:
```
docker rm -f jsonx-be
```

To see logs and connect the container:
```
docker logs --follow jsonx-be
docker exec -it jsonx-be bash

```

JSONx is envisioned as a web-based tool for developers of applications and websites using JSON for data interchange.  Users may access the app with any device running any operating system using a standard browser interface.

JSONx will provide an efficient way to streamline testing and development of any application or project that utilizes JSON. JSONx will serve as an independent, cross-platform, and cross-browser tool for developers and users to quickly explore and verify JSON data. The application will make use of self-contained, scalable, and reliable hosting through the usage of the cloud platform Heroku, which provides solutions for hosting, database, and networking all in one. As such, the application will not require management of any physical hardware.

The product will consist of a Front-end application and Back-end application that will work together to provide the user with a fast and modern solution to JSON development needs. The Front-end will be hosted in a separate instance on Heroku and will consist of an Angular application. The Back-end will be hosted on a separate instance on Heroku and will consist of an API developed in Python 3.6 utilizing the Flask library, and a data storage solution of MySQL. Separate hosting of each component will allow for parallel development and releases in the initial and future releases for Front-end and Back-end.

The Front-end application will consist of a client-side web application that will be accessed by the user. The Front-end application will take input requests from the user, e.g save, view, search, and make appropriate requests to the Back-end application perform required tasks.

The back-end application will consist of a RESTful Application Program Interface that will provide functionality to perform appropriate tasks, store, and manage data that is appropriate for JSONx. The Back-end application will validate requests from the Front-end and perform appropriate tasks, such as JSON validation, storage, search, retrieval, and access control. As data will be required to be saved in JSONx, a database will additionally be required for the Back-end to interact with.
