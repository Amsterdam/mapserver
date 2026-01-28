FROM ubuntu:24.04
LABEL maintainer="datapunt@amsterdam.nl"
ARG DEBIAN_FRONTEND=noninteractive
# build-time inputs
ARG EXTRA_ARG1
ARG EXTRA_ARG2
ENV MAP_URL="${EXTRA_ARG1}" LEGEND_URL="${EXTRA_ARG2}"

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

#config file
COPY mapserver.conf /usr/local/etc/
RUN echo "SetEnv MAPSERVER_CONFIG_FILE \"/usr/local/etc/mapserver.conf\"" >> /etc/apache2/apache2.conf

# apache config
RUN rm /etc/apache2/mods-enabled/alias.conf
COPY docker/conf/*.conf /etc/apache2/conf-enabled/
# rm 000-default.conf from repo
COPY docker/000-default.conf /etc/apache2/sites-available/
# COPY docker/sites/8080.conf /etc/apache2/sites-available/
COPY docker/docker-entrypoint.sh /bin
COPY epsg /usr/share/proj

# disable default site
# RUN a2dissite 000-default.conf 
# enable custom site
# RUN a2ensite 8080.conf

RUN echo ${LEGEND_URL}
RUN echo ${MAP_URL}

RUN : "${MAP_URL:?MAP_URL not set}" \
 && : "${LEGEND_URL:?LEGEND_URL not set}" \
 && find /srv/mapserver/ -type f -name '*.map' -print0 \
    | xargs -0 sed -i \
        -e "s#MAP_URL_REPLACE#${MAP_URL}#g" \
        -e "s#LEGEND_URL_REPLACE#${LEGEND_URL}#g"

# set apache user id matching ctr user id
RUN usermod --non-unique --uid 999 www-data
RUN groupmod -o -g 999 www-data
RUN mkdir /var/lock/apache2 && mkdir /var/run/apache2
RUN chown -R 999:999 /var/lock/apache2 && chown -R 999:999 /var/run/apache2 && chown -R 999:999 /var/log/apache2/
RUN chown -R 999:999 /srv/ && chown -R 999:999 /etc/apache2/
COPY  --chown=999:999 . /srv/mapserver/
RUN rm -rf /srv/mapserver/private
RUN python3 /srv/mapserver/tools/make_indexjson.py /srv/mapserver/*.map > /srv/mapserver/index.json

EXPOSE 8080

USER www-data
CMD /bin/docker-entrypoint.sh
