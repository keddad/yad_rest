FROM python:3.7-alpine
WORKDIR /usr/src/app
RUN apk add --no-cache \
        uwsgi-python3
COPY . .
ENV TESTING TRUE
RUN pip3 install --no-cache-dir -r requirements.txt
CMD [ "uwsgi", "--socket", "0.0.0.0:3031", \
               "--uid", "uwsgi", \
               "--plugins", "python3", \
               "--protocol", "uwsgi", \
               "--wsgi", "app:app", \
               "-p", "4", \
               "--enable-threads"]