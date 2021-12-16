# Using the Amsterdam mapserver for local testing

*This document describes how to serve your own datasets using the Datapunt Amsterdam Mapserver container.*

The [Datapunt Amsterdam mapserver][1] docker container is used to provide [WMS][7] and
[WFS][8] services as part of the [Amsterdam Data en Informatie portal][2]. This container
provides a webserver with the [Mapserver][3] scripts pre-configured for some of
the Amsterdam Data en Informatie data sets.

While you cannot access all the datasets that are served using this container you
can re-use it for your own purposes such as local testing. How you can adapt it
is described below.

*Note: web browsers do not implement the WMS and WFS protocols, you need a dedicated client.*


## Pre-requisites

The rest of this document assumes that you know how to use:

* Git
* Docker
* docker-compose
* Mapserver ``.map`` files
* [QGIS][9] (or any other WMS / WFS client)
* PostGIS

We furthermore assume you have containerized spatial database, in our example
we have a [GeoDjango][5] application with a [PostGIS][6] database, both set up to
run from a Docker container.


## (1) Create a docker-compose.yml file

Create a ``docker-compose.yml`` file that can start your database and web
service. Add an entry for the Mapserver (in our example application it is
called ``mapserver``). An example from the ``reistijdenauto`` project (NOTE: This project has been discontinued):
```yaml
version: "3.0"
services:
  database:
    build: database/
    ports:
      - "5432:5432"
    environment:
      POSTGRES_DB: reistijdenauto
      POSTGRES_USER: reistijdenauto
      POSTGRES_PASSWORD: insecure

  web:
    build: src/
    ports:
      - "8000:8000"
    links:
      - database
    volumes:
      - "./src/:/app/"
    command: >
      bash -c "cd /app && \
               bash -c /app/docker-wait.sh && \
               python manage.py runserver 0.0.0.0:8000"
    environment:
      SECRET_KEY: insecure

  mapserver:
    build: mapserver/
    ports:
      - "8070:80"
    links:
      - database
    environment:
      REISTIJDENAUTO_DB_NAME: reistijdenauto
      REISTIJDENAUTO_DB_USER: reistijdenauto
      REISTIJDENAUTO_DB_PASSWORD: insecure
      REISTIJDENAUTO_DB_HOST: database
```
For the use of the environment variables in the ``mapserver`` service see the
section about connecting the Mapserver to the database.


### (2) Check out the Datapunt Amsterdam mapserver project
Git clone the Datapunt [Amsterdam mapserver Docker project][1] to a directory
that matches the ``build`` directory you specified in the ``mapserver`` section
of your ``docker-compose.yml`` file. To test whether you did this correctly
run the following ``docker-compose`` command from the directory with your
``docker-compose.yml`` file:
```shell
docker-compose build
```
(This should build images for the three services mentioned above.)


### Connect Mapserver to database
To make sure that Mapserver can access the spatial database, you will have to
change the Docker entry point script for the Mapserver container. You will have
to change the Docker entrypoint script that is defined in the ``mapserver``
source checkout.

* ``/docker/docker-entry-point.sh``

This file is executed when the container starts and will at that point apply
the final, environment specific, changes to the Mapserver configuration by
writing a number of values a specific ``connection.inc`` file. These values can be
set through environment variables in the docker-compose file that you created.
You should add a block of variables for your project. The example block of
environment variables below is taken from the ``reistijdenauto`` project,
whose variables all start with ``REISTIJDENAUTO``:

```sh
REISTIJDENAUTO_DB_HOST=${REISTIJDENAUTO_DB_HOST:-postgres-read.service.consul}
REISTIJDENAUTO_DB_PORT=${REISTIJDENAUTO_DB_PORT:-5432}
REISTIJDENAUTO_DB_NAME=${REISTIJDENAUTO_DB_NAME:-reistijdenauto}
REISTIJDENAUTO_DB_USER=${REISTIJDENAUTO_DB_USER:-${REISTIJDENAUTO_DB_NAME}}
REISTIJDENAUTO_DB_PASSWORD=${REISTIJDEN_AUTO_DB_PASSWORD:-insecure}
```

Furthermore also add a block of code that updates the relevant ``connection.inc``
file, example again taken from the ``reistijdenauto`` service and map layer:


```sh
cat > /srv/mapserver/connection_reistijdenauto.inc <<EOF
CONNECTIONTYPE postgis
CONNECTION "host=${REISTIJDENAUTO_DB_HOST} dbname=${REISTIJDENAUTO_DB_NAME} user=${REISTIJDENAUTO_DB_USER} password=${REISTIJDENAUTO_DB_PASSWORD} port=${REISTIJDENAUTO_DB_PORT}"
PROCESSING "CLOSE_CONNECTION=DEFER"
EOF
```

Make sure to reference this specific ``connection.inc`` file in the ``.map``
you create for your new map layer. You will furthermore have to rebuild the
``mapserver`` Docker image.


### (3) Adding a ``.map`` file for your map layer
Explaining the intricacies of Mapserver ``.map`` files is out of scope for this
document, instead see the [Mapfile documentation][4]. Having said that, below
is a snippet from the Mapfile for the ``reistijdenauto`` map layer that shows
how the database connection is configured at the Mapfile level. The full
file can be found in the [Datapunt Amsterdam mapserver Docker project][1].

```
MAP
  NAME "REISTIJDENAUTO"
  INCLUDE "header.inc"

  WEB
    METADATA
      "ows_title"    "reistijdenauto"
      "ows_abstract" "Reistijden per auto omgeving Amsterdam"
      "wms_extent"          "100000 450000 150000 500000"
    END
  END

  #=============================================================================
  # LAYERS
  #=============================================================================

  LAYER
    NAME            "reistijdenauto"
    INCLUDE         "connection_reistijdenauto.inc"
    DATA            "mline FROM public.dataset_wegstuk USING srid=28992 USING UNIQUE id"
    TYPE            LINE
    MINSCALEDENOM   100
    MAXSCALEDENOM   400001
    TEMPLATE        "fooOnlyForWMSGetFeatureInfo.html"
    PROJECTION
      "init=epsg:28992"
    END

    METADATA
      "ows_title"           "reistijdenauto"
      "ows_group_title"     "reistijdenauto"
      "ows_abstract"        "Reistijden per auto regio Amsterdam"
      "gml_featureid"       "ID"
      "gml_include_items"   "all"
      "gml_types"           "auto"
    END

```

### (4) Run the services
From your project root:
```sh
docker-compose up
```
You will now have a locally running Mapserver, that serves your data. The
missing data sets (for which the Mapserver is configured) are ignored as long
as you do not try to access them.
The WMS URL for the example project (``reistijdenauto``) running locally is:
```
http://127.0.0.1:8070/maps/reistijdenauto?
```
Add a WMS layer to QGIS and use the URL mentioned above to view the WMS
web services running on your computer.


## For reference: the example project ``reistijdenauto``

The travel times by car service (aptly called ``reistijdenauto``), provides
a relatively simple example. It comprises of a small Django application whose
database is also used as a data source by the Amsterdam Datapunt Mapserver.

https://github.com/Amsterdam/reistijdenauto

Clone this project and follow the instructions in the README to get a
locally running Mapserver and Django application. The only changes that
were needed to add the ``reistijdenauto`` map layer were as described
above in the section about adding a new map layer.

[1]: https://github.com/Amsterdam/mapserver "Github project for Datapunt Amsterdam mapserver Docker container"
[2]: https://data.amsterdam.nl/ "Amsterdam Data en Informatie portal"
[3]: http://www.mapserver.org/ "Mapserver open source web mapping server"
[4]: http://www.mapserver.org/mapfile/ "Mapfile documentation"
[5]: https://docs.djangoproject.com/en/1.11/ref/contrib/gis/ "The GeoDjango geographic Web framework"
[6]: http://postgis.net/ "PostGIS spatial extension for PostgreSQL"
[7]: https://en.wikipedia.org/wiki/Web_Map_Service "Wikipedia: Web Wap Service (WMS)"
[8]: https://en.wikipedia.org/wiki/Web_Feature_Service "Wikipedia: Web Feature Service (WFS)"
[9]: http://qgis.org/en/site/ "QGIS homepage"
