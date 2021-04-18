FROM ubuntu:20.04

RUN apt-get update \
  && apt-get install -y python3-pip python3-dev \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

EXPOSE 8080

RUN pip3 install -r requirements.txt

COPY . /app

CMD [ "gunicorn", "-b", "0.0.0.0:8080", "wsgi:app"]