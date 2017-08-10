FROM ubuntu:16.04
MAINTAINER datapunt.ois@amsterdam.nl

ENV DEBIAN_FRONTEND noninteractive
ENV LANG C.UTF-8

ARG MAP_URL
ENV MAP_URL=$MAP_URL

# Update and upgrade system
RUN apt-get -qq update --fix-missing && apt-get -qq --yes upgrade

# Install mapcache compilation prerequisites
RUN apt-get install -y software-properties-common g++ make cmake wget git openssh-server locales
RUN update-locale LANG=C.UTF-8

# Install mapcache dependencies provided by Ubuntu repositories
RUN apt-get install -y \
    libxml2-dev \
    libxslt1-dev \
    libproj-dev \
    libfribidi-dev \
    libcairo2-dev \
    librsvg2-dev \
    libmysqlclient-dev \
    libpq-dev \
    libcurl4-gnutls-dev \
    libexempi-dev \
    libgdal-dev \
    libgeos-dev

RUN apt-get install -y bzip2

# Package versions
ENV HARFBUZZ_VERSION 1.2.4

# Install libharfbuzz from source as it is not in a repository
RUN cd /tmp && wget http://www.freedesktop.org/software/harfbuzz/release/harfbuzz-$HARFBUZZ_VERSION.tar.bz2 && \
    tar xjf harfbuzz-$HARFBUZZ_VERSION.tar.bz2 && \
    cd harfbuzz-$HARFBUZZ_VERSION && \
    ./configure && \
    make && \
    make install && \
    ldconfig

# Install Mapserver itself
RUN git clone https://github.com/mapserver/mapserver/ /usr/local/src/mapserver

# Compile Mapserver for Apache with 3D point support
RUN mkdir /usr/local/src/mapserver/build && \
    cd /usr/local/src/mapserver/build && \
    cmake ../ -DWITH_THREAD_SAFETY=1 \
        -DWITH_PROJ=1 \
        -DWITH_KML=1 \
        -DWITH_SOS=1 \
        -DWITH_WMS=1 \
        -DWITH_FRIBIDI=1 \
        -DWITH_HARFBUZZ=1 \
        -DWITH_ICONV=1 \
        -DWITH_CAIRO=1 \
        -DWITH_RSVG=1 \
        -DWITH_MYSQL=1 \
        -DWITH_GEOS=1 \
        -DWITH_POSTGIS=1 \
        -DWITH_GDAL=1 \
        -DWITH_OGR=1 \
        -DWITH_CURL=1 \
        -DWITH_CLIENT_WMS=1 \
        -DWITH_CLIENT_WFS=1 \
        -DWITH_WFS=1 \
        -DWITH_WCS=1 \
        -DWITH_LIBXML2=1 \
        -DWITH_GIF=1 \
        -DWITH_EXEMPI=1 \
        -DWITH_XMLMAPFILE=1 \

	-DWITH_USE_POINT_Z_M=1 \
    -DWITH_FCGI=0 && \
    make && \
    make install && \
    ldconfig


# Apache 2
RUN apt-get update && apt-get install -y apache2 apache2-dev curl

# Enable these Apache modules
RUN a2enmod actions cgi alias rewrite headers

# Configure localhost in Apache
RUN echo "ServerName localhost" >> /etc/apache2/apache2.conf
RUN rm /etc/apache2/mods-enabled/alias.conf
COPY docker/000-default.conf /etc/apache2/sites-available/
COPY docker/docker-entrypoint.sh /bin

# Link to cgi-bin executable
RUN chmod o+x /usr/local/bin/mapserv
RUN ln -s /usr/local/bin/mapserv /usr/lib/cgi-bin/mapserv
RUN chmod 755 /usr/lib/cgi-bin

COPY . /srv/mapserver/

EXPOSE 80

ENV HOST_IP `ifconfig | grep inet | grep Mask:255.255.255.0 | cut -d ' ' -f 12 | cut -d ':' -f 2`

CMD /bin/docker-entrypoint.sh
