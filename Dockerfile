FROM ubuntu:16.04
MAINTAINER Caner Dagli
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential git
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT ["python", "run.py"]

# docker build -t jsonx-be .
# 
# For Development Container
# docker run -dt --name=jsonx-be -v $PWD:/app -p 5000:5000 -e 'WORK_ENV=DEV' jsonx-be
# 
# For Production Container
# docker run -dt --restart=always --name=jsonx-be -p 5000:5000 -e 'WORK_ENV=PROD' jsonx-be
# 
# Remove the container
# docker rm -f jsonx-be

# docker logs --follow jsonx-be
# docker exec -it jsonx-be bash
