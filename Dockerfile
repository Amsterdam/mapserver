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


# Enable these Apache modules
RUN a2enmod actions cgid headers rewrite

# Configure localhost in Apache
RUN echo "ServerName localhost" >> /etc/apache2/apache2.conf
RUN rm /etc/apache2/mods-enabled/alias.conf
COPY docker/000-default.conf /etc/apache2/sites-available/
COPY docker/docker-entrypoint.sh /bin

COPY . /srv/mapserver/ 
COPY epsg /usr/share/proj

RUN useradd -M -u 999 -U datapunt
RUN chmod 775 $(find /srv -type d)
RUN chown -R datapunt:datapunt /srv/ && chown -R datapunt:datapunt /etc/apache2/ && chown -R datapunt:datapunt /var/lock/apache2
RUN rm -rf /srv/mapserver/private

EXPOSE 80

USER datapunt
CMD /bin/docker-entrypoint.sh