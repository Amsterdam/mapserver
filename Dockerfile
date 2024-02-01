FROM ubuntu:22.04
LABEL maintainer="datapunt@amsterdam.nl"
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

RUN apt-get update && apt-get install -my curl wget gnupg -y
RUN apt install build-essential software-properties-common -y
# RUN add-apt-repository -y ppa:ubuntugis/ppa

RUN apt-get install -y gdal-bin gdal-data libgdal30
RUN apt-get install -y apache2 apache2-utils libmapcache1 libapache2-mod-mapcache cgi-mapserver mapserver-bin

# Enable these Apache modules
RUN a2enmod actions cgi alias headers rewrite env

# Configure localhost in Apache
RUN echo "ServerName localhost" >> /etc/apache2/apache2.conf
RUN rm /etc/apache2/mods-enabled/alias.conf
COPY docker/000-default.conf /etc/apache2/sites-available/
COPY docker/docker-entrypoint.sh /bin

COPY . /srv/mapserver/

EXPOSE 80

CMD /bin/docker-entrypoint.sh