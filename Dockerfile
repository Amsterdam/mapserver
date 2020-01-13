FROM ubuntu:18.04
MAINTAINER datapunt@amsterdam.nl

RUN apt-get update && apt-get install -my wget gnupg -y
RUN apt install build-essential software-properties-common -y

# Setup build env
RUN mkdir /build
RUN add-apt-repository -y ppa:ubuntugis/ppa
RUN apt-get update && apt-get install -y --fix-missing --no-install-recommends gcc-4.8 g++-4.8 build-essential ca-certificates curl wget git libaio1 make cmake python-dev \
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

# Force buit libraries dependencies
RUN ldconfig

# Enable these Apache modules
RUN  a2enmod actions cgid headers rewrite 

# Added mpm event for performance tuning

# Configure localhost in Apache
RUN echo "ServerName localhost" >> /etc/apache2/apache2.conf
RUN rm /etc/apache2/mods-enabled/alias.conf
COPY docker/mpm_event.conf /etc/apache2/mods-available/ 
COPY docker/000-default.conf /etc/apache2/sites-available/ 
COPY docker/docker-entrypoint.sh /bin

# Link to cgi-bin executable
# RUN chmod o+x /usr/local/bin/mapserv
# RUN ln -s /usr/local/bin/mapserv /usr/lib/cgi-bin/mapserv
# RUN chmod 755 /usr/lib/cgi-bin

COPY . /srv/mapserver/
RUN rm -rf /srv/mapserver/private


EXPOSE 80

ENV HOST_IP `ifconfig | grep inet | grep Mask:255.255.255.0 | cut -d ' ' -f 12 | cut -d ':' -f 2`
ENV ACCESS_SCOPE public

CMD /bin/docker-entrypoint.sh
