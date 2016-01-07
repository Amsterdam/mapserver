# Mapserver for Docker
FROM ubuntu:14.04.3
MAINTAINER datapunt@amsterdam.nl

# Update and upgrade system
RUN apt-get -qq update --fix-missing && apt-get -qq --yes upgrade
# Install Apache and mapserver
RUN apt-get install -y software-properties-common apache2 mapserver-bin cgi-mapserver apache2-threaded-dev curl apache2-mpm-worker
# Add Ubuntu GIS apt key
RUN sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 314DF160
# Add Ubuntu GIS Repo
RUN sudo add-apt-repository 'deb http://ppa.launchpad.net/ubuntugis/ubuntugis-unstable/ubuntu trusty main'

# Configure localhost in Apache
RUN echo "ServerName localhost" >> /etc/apache2/apache2.conf
COPY docker_files/000-default.conf /etc/apache2/sites-available/

RUN echo 'deb http://archive.ubuntu.com/ubuntu trusty multiverse' >> /etc/apt/sources.list
RUN echo 'deb http://archive.ubuntu.com/ubuntu trusty-updates multiverse' >> /etc/apt/sources.list
RUN echo 'deb http://security.ubuntu.com/ubuntu trusty-security multiverse' >> /etc/apt/sources.list
RUN sudo apt-get update
# Install necessary modules
RUN sudo apt-get install -y libapache2-mod-fastcgi
# Enable these Apache modules
RUN sudo a2enmod actions cgid headers

# Mapserver content and config
RUN mkdir -p /srv/mapserver
COPY docker_files/connection.inc /srv/mapserver/
RUN mkdir -p /app
COPY docker_files/docker-entrypoint.sh /app/
COPY *.map /srv/mapserver/
COPY header.inc /srv/mapserver/

EXPOSE 80

CMD /app/docker-entrypoint.sh
