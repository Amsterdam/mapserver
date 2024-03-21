FROM ubuntu:22.04
MAINTAINER datapunt@amsterdam.nl
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y \
    apache2 \
    cgi-mapserver \
    curl \
    gdal-bin \
    gdal-data \
    libmapcache1 \
    libapache2-mod-mapcache \
    mapserver-bin \
    python3-pip \
    wget

RUN python3 -m pip install mappyfile==0.9.7

# Enable these Apache modules
RUN a2enmod actions cgid headers rewrite

# Configure localhost in Apache
RUN echo "ServerName localhost" >> /etc/apache2/apache2.conf
RUN rm /etc/apache2/mods-enabled/alias.conf
COPY docker/000-default.conf /etc/apache2/sites-available/
COPY docker/docker-entrypoint.sh /bin

COPY . /srv/mapserver/

EXPOSE 80

CMD /bin/docker-entrypoint.sh