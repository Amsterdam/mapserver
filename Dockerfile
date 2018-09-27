FROM ubuntu:18.04
MAINTAINER datapunt@amsterdam.nl

# !!
# modified to use mapserver from apt-get.
#

#ENV LD_LIBRARY_PATH=/usr/lib:/usr/local/lib
#ENV LIBKML_DOWNLOAD=install-libkml-r864-64bit.tar.gz
#ENV FILEGDBAPI_DOWNLOAD=FileGDB_API_1_2-64.tar.gz
#ENV MRSID_DIR=MrSID_DSDK-8.5.0.3422-linux.x86-64.gcc44
#ENV MRSID_DOWNLOAD=MrSID_DSDK-8.5.0.3422-linux.x86-64.gcc44.tar.gz

RUN apt-get update && apt-get install -my wget gnupg -y
RUN apt install build-essential -y

# Setup build env
RUN mkdir /build
RUN apt-key adv --recv-keys --keyserver hkp://keyserver.ubuntu.com:80 16126D3A3E5C1192    \
  && apt-get update && apt-get install -y --fix-missing --no-install-recommends software-properties-common \
  && add-apt-repository ppa:ubuntugis/ubuntugis-unstable -y    \
  && apt-get update && apt-get install -y --fix-missing --no-install-recommends gcc-4.8 g++-4.8 build-essential ca-certificates curl wget git libaio1 make cmake python-dev \
      software-properties-common  libc6-dev openssh-client libpng16-16 libjpeg-dev libgif-dev liblzma-dev libgeos-dev \
      libproj-dev libxml2-dev libexpat-dev libxerces-c-dev libnetcdf-dev netcdf-bin libpoppler-dev libspatialite-dev swig  \
      libhdf5-serial-dev libpodofo-dev poppler-utils libfreexl-dev libwebp-dev libepsilon-dev libpcre3-dev gfortran libarpack2-dev \
      libpq-dev libflann-dev libhdf5-serial-dev libhdf5-dev libjsoncpp-dev clang-3.9  libhdf4-alt-dev libsqlite3-dev    \
      libltdl-dev libcurl4-openssl-dev ninja-build cython python-pip libpng-dev  \
      libprotobuf-c-dev libprotobuf-c1 protobuf-c-compiler protobuf-compiler \
      libboost-filesystem1.65-dev libboost-iostreams1.65-dev libboost-system1.65-dev libboost-thread1.65-dev libogdi3.2-dev time

RUN update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-4.8 20 && update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-4.8 20
#RUN CXX=clang++ && CC=clang
RUN apt-get install -y gdal-bin libgdal-dev gdal-data libgdal20
RUN apt-get install -y apache2 apache2-utils libmapcache1 libapache2-mod-mapcache cgi-mapserver \
      mapserver-bin libmapserver-dev

#RUN dpkg --add-architecture i386 && apt-get update && apt-get install -y openjdk-8-jre:i386
# Getting libKML

#RUN wget --no-verbose http://s3.amazonaws.com/etc-data.koordinates.com/gdal-travisci/${LIBKML_DOWNLOAD} -O /build/${LIBKML_DOWNLOAD} && \
# tar -C /build -xzf /build/${LIBKML_DOWNLOAD} && \
# cp -r /build/install-libkml/include/* /usr/local/include &&  \
# cp -r /build/install-libkml/lib/* /usr/local/lib \
# && rm -Rf /build/install-libkml
#
#RUN wget --no-verbose http://s3.amazonaws.com/etc-data.koordinates.com/gdal-travisci/${MRSID_DOWNLOAD} -O /build/${MRSID_DOWNLOAD} && \
#  tar -C /build -xzf /build/${MRSID_DOWNLOAD} && \
#  cp -r /build/${MRSID_DIR}/Raster_DSDK/include/* /usr/local/include && \
#  cp -r /build/${MRSID_DIR}/Raster_DSDK/lib/* /usr/local/lib \
#  && rm -Rf /build/${MRSID_DIR}
#
#RUN wget --no-verbose http://s3.amazonaws.com/etc-data.koordinates.com/gdal-travisci/${FILEGDBAPI_DOWNLOAD} -O /build/${FILEGDBAPI_DOWNLOAD} && \
# tar -C /build -xzf /build/${FILEGDBAPI_DOWNLOAD} &&  \
# cp -r /build/FileGDB_API/include/* /usr/local/include && \
# cp -r /build/FileGDB_API/lib/* /usr/local/lib \
# && rm -Rf /build/FileGDB_API
#
#ARG GDAL_VERSION
#RUN cd /build && \
#    git clone https://github.com/OSGeo/gdal.git && \
#    cd /build/gdal && \
#    git checkout ${GDAL_VERSION} && \
#    cd /build/gdal/gdal &&  \
#    ./configure --prefix=/usr \
#        --with-png=internal \
#        --with-jpeg=internal \
#        --with-libz=internal \
#        --with-libtiff=internal \
#        --with-geotiff=internal \
#        --with-gif=internal \
#        --with-libjson-c=internal \
#        --with-poppler \
#        --with-spatialite \
#        --with-liblzma \
#        --with-ogdi \
#        --with-webp \
#        --with-pg \
#        --with-mrsid=/usr/local \
#        --with-fgdb=/usr/local \
#        --with-libkml \
#        --with-hdf5 && \
#    make && \
#    make install && \
#    ldconfig && \
#    rm -Rf /build/gdal
#
#RUN apt-get update && apt-get install -y --fix-missing --no-install-recommends build-essential ca-certificates curl wget  \
#    subversion git libaio1 make cmake python-numpy python-dev software-properties-common libv8-dev libc6-dev libfreetype6-dev \
#    libcairo2-dev libpq-dev libharfbuzz-dev libfribidi-dev flex bison libfcgi-dev libxml2 libxml2-dev bzip2 apache2 apache2-utils apache2-dev \
#    libaprutil1-dev libapr1-dev libjpeg-dev libcurl4-gnutls-dev libpcre3-dev libpixman-1-dev libgeos-dev libsqlite3-dev libdb-dev libtiff-dev sudo \
#  && rm -rf /var/lib/apt/lists/partial/* /tmp/* /var/tmp/*

# RUN echo "msuser ALL=NOPASSWD: ALL" >> /etc/sudoers

# ARG MAPSERVER_VERSION
# RUN cd /build && \
#     git clone https://github.com/mapserver/mapserver.git mapserver && \
#     cd /build/mapserver && \
#     git checkout ${MAPSERVER_VERSION} \
#     && mkdir /build/mapserver/build \
#     && cd /build/mapserver/build \
#     && cmake  \
#       -DCMAKE_BUILD_TYPE=Release \
#       -DHARFBUZZ_INCLUDE_DIR=/usr/include/harfbuzz \
#       -DWITH_CLIENT_WFS=ON \
#       -DWITH_CLIENT_WMS=ON \
#       -DWITH_CURL=ON \
#       -DWITH_GDAL=ON \
#       -DWITH_GIF=ON \
#       -DWITH_ICONV=ON \
#       -DWITH_KML=ON \
#       -DWITH_LIBXML2=ON \
#       -DWITH_OGR=ON \
#       -DWITH_POINT_Z_M=ON \
#       -DWITH_PROJ=ON \
#       -DWITH_SOS=ON  \
#       -DWITH_THREAD_SAFETY=ON \
#       -DWITH_WCS=ON \
#       -DWITH_WFS=ON \
#       -DWITH_WMS=ON \
#       -DWITH_FCGI=ON \
#       -DWITH_FRIBIDI=ON \
#       -DWITH_CAIRO=ON \
#       -DWITH_HARFBUZZ=ON \
#       -DWITH_POSTGIS=on \
#       -DWITH_PROTOBUFC=OFF \
#       -DWITH_V8=OFF \
#       ..  \
#     && make  \
#     && make install \
#     && ldconfig \
#     && rm -Rf /build/mapserver

# Install Mapcache itself
# ARG MAPCACHE_VERSION
# RUN cd /build  \
#     && mkdir -p /msconfig/mapcache \
#     && git clone https://github.com/mapserver/mapcache/ \
#     && cd /build/mapcache  \
#     && git checkout ${MAPCACHE_VERSION} \
#     && mkdir /build/mapcache/build \
#     && cd /build/mapcache/build \
#     && cmake ../ \
#     -DWITH_FCGI=0 -DWITH_APACHE=1 -DWITH_PCRE=1 \
#     -DWITH_TIFF=1 -DWITH_BERKELEY_DB=1 -DWITH_MEMCACHE=1 \
#     -DCMAKE_PREFIX_PATH="/etc/apache2" && \
#     make && \
#     make install


# Force buit libraries dependencies
RUN ldconfig

# Enable these Apache modules
RUN  a2enmod actions cgi alias headers rewrite

# Configure localhost in Apache
RUN echo "ServerName localhost" >> /etc/apache2/apache2.conf
RUN rm /etc/apache2/mods-enabled/alias.conf
COPY docker/000-default.conf /etc/apache2/sites-available/
COPY docker/docker-entrypoint.sh /bin

# Link to cgi-bin executable
# RUN chmod o+x /usr/local/bin/mapserv
# RUN ln -s /usr/local/bin/mapserv /usr/lib/cgi-bin/mapserv
# RUN chmod 755 /usr/lib/cgi-bin
#

COPY . /srv/mapserver/
RUN rm -rf /srv/mapserver/private


EXPOSE 80

ENV HOST_IP `ifconfig | grep inet | grep Mask:255.255.255.0 | cut -d ' ' -f 12 | cut -d ':' -f 2`

CMD /bin/docker-entrypoint.sh
