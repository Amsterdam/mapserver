# Mapserver for Docker
FROM ubuntu:14.04
MAINTAINER datapunt@amsterdam.nl

ENV DEBIAN_FRONTEND noninteractive

RUN echo "deb http://ppa.launchpad.net/ubuntugis/ubuntugis-unstable/ubuntu trusty main" >> /etc/apt/sources.list \
	&& echo "deb-src http://ppa.launchpad.net/ubuntugis/ubuntugis-unstable/ubuntu trusty main" >> /etc/apt/sources.list \
	&& apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 314DF160 \
	&& apt-get -qq update \
	&& apt-get install -y \
		apache2 \
		apache2-threaded-dev \
		apache2-mpm-worker \
		cgi-mapserver \
		mapserver-bin=6.4.* \
	&& apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && a2enmod actions cgid headers alias

COPY docker/000-default.conf /etc/apache2/sites-available/
COPY docker/docker-entrypoint.sh /bin
COPY . /srv/mapserver/

EXPOSE 80

CMD /bin/docker-entrypoint.sh

