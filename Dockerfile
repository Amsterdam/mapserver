FROM ubuntu:22.04
LABEL maintainer="datapunt@amsterdam.nl"
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ="Europe/Amsterdam"

RUN apt-get update -y \
    && apt-get install -y --no-install-recommends \
        apache2 \
        cgi-mapserver \
        curl \
        gdal-bin \
        gdal-data \
        mapserver-bin \
        python3-pip \
        wget \
    && apt-get clean

RUN python3 -m pip install mappyfile==0.9.7

# Enable these Apache modules
RUN a2enmod actions cgid headers rewrite

# Configure localhost in Apache
RUN echo "ServerName localhost" >> /etc/apache2/apache2.conf
RUN rm /etc/apache2/mods-enabled/alias.conf
COPY docker/000-default.conf /etc/apache2/sites-available/
COPY docker/docker-entrypoint.sh /bin

COPY . /srv/mapserver/
COPY epsg /usr/share/proj

EXPOSE 80

CMD /bin/docker-entrypoint.sh