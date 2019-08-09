FROM alpine:3.10
VOLUME /usr/src/app/public
WORKDIR /usr/src/app
RUN apk update
RUN apk add --no-cache python3 && \
    if [ ! -e /usr/bin/python ]; then ln -sf python3 /usr/bin/python ; fi && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --no-cache --upgrade pip setuptools wheel && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi
RUN apk add --no-cache \
        uwsgi-python3 make automake gcc g++ subversion python3-dev
COPY . .
RUN rm -rf public/*
ENV TESTING TRUE
RUN pip3 install --no-cache-dir -r requirements.txt
CMD [ "uwsgi", "--socket", "0.0.0.0:3031", \
               "--uid", "uwsgi", \
               "--plugins", "python3", \
               "--protocol", "uwsgi", \
               "--wsgi", "app:app", \
               "-p", "4", \
               "--enable-threads"]