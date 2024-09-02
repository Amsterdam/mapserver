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

RUN useradd -M -U datapunt
COPY . /srv/mapserver/ 
RUN chmod 755 $(find /srv -type d)

RUN chown -R datapunt:datapunt /srv/ && rm -rf /srv/mapserver/private
COPY epsg /usr/share/proj

EXPOSE 80

USER datapunt
CMD /bin/docker-entrypoint.sh