FROM ubuntu:22.04
LABEL maintainer="datapunt@amsterdam.nl"
ARG DEBIAN_FRONTEND=noninteractive
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


# Enable these Apache modules
RUN a2enmod actions cgid headers rewrite

# Configure localhost in Apache
RUN echo "ServerName localhost" >> /etc/apache2/apache2.conf
RUN rm /etc/apache2/mods-enabled/alias.conf
COPY docker/000-default.conf /etc/apache2/sites-available/
COPY docker/docker-entrypoint.sh /bin

COPY . /srv/mapserver/ 
COPY epsg /usr/share/proj

# set apache user id matching ctr user id
RUN usermod --non-unique --uid 999 www-data
RUN groupmod -o -g 999 www-data
RUN mkdir /var/lock/apache2 && mkdir /var/run/apache2 
RUN chown -R 999:999 /var/lock/apache2 && chown -R 999:999 /var/run/apache2 && chown -R 999:999 /var/log/apache2/
RUN chown -R 999:999 /srv/ && chown -R 999:999 /etc/apache2/
RUN rm -rf /srv/mapserver/private

EXPOSE 8080

USER www-data
CMD /bin/docker-entrypoint.shp