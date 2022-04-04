FROM ubuntu:18.04
LABEL maintainer="datapunt@amsterdam.nl"

RUN apt-get update && apt-get install -my curl wget gnupg -y
RUN apt install build-essential software-properties-common -y
RUN add-apt-repository -y ppa:ubuntugis/ppa

RUN apt-get install -y gdal-bin gdal-data libgdal20
RUN apt-get install -y apache2 apache2-utils libmapcache1 libapache2-mod-mapcache cgi-mapserver mapserver-bin

# for debugging db connz
RUN apt-get install -y postgresql-client traceroute

# Enable these Apache modules
RUN a2enmod actions cgid headers rewrite

# Configure localhost in Apache
RUN echo "ServerName localhost" >> /etc/apache2/apache2.conf
RUN rm /etc/apache2/mods-enabled/alias.conf
COPY docker/000-default.conf /etc/apache2/sites-available/
COPY docker/docker-entrypoint.sh /bin

COPY . /srv/mapserver/
RUN rm -rf /srv/mapserver/private


EXPOSE 80

ENV HOST_IP `ifconfig | grep inet | grep Mask:255.255.255.0 | cut -d ' ' -f 12 | cut -d ':' -f 2`
ENV ACCESS_SCOPE public

CMD /bin/docker-entrypoint.sh
