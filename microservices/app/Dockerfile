FROM python:2-stretch

WORKDIR /usr/src/app

# Install postgres
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# install requirements
# this way when you build you won't need to install again
# and since COPY is cached we don't need to wait
COPY app/conf/requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

# Copy the Configuration and the Scripts
COPY app/conf /conf
COPY app/scripts /usr/src/scripts
RUN chmod a+x /usr/src/scripts/runserver.sh
RUN pip install google-cloud
RUN pip install google-cloud-firestore

# Copy the source.
COPY app/src /usr/src/app

WORKDIR /usr/src/app/PyGeon

# App port number is configured through the gunicorn config file
ENTRYPOINT ["/usr/src/scripts/runserver.sh"]
RUN ls /usr/src/app/PyGeon
