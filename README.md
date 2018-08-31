SE-131 Group Project - JSONx
[![Build Status](https://travis-ci.org/SE-131-JSONx/jsonx-be.svg?branch=cit)](https://travis-ci.org/SE-131-JSONx/jsonx-be)

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