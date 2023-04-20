# Data en Informatie map


MapServer configuratie voor Data en Informatie.


# Development stappen

* Build de mapserver docker.
* Download eventueel de database met de geoviews.
* controleer eerste de geo data met qgis door direct met postgres te werken
* configureer de mapfile om het de juiste database en data te werken
* Ontwikkel met http://localhost/map/YOURMAPFILENAME

Deze mapserver is te gebruiken als WMS of WFS mapserver met behulp van een programma als QGis en
niet vanuit een webbrowser. In de webbrowser geven de URL links foutmeldingen.

## Prerequisites:

* [docker](https://docs.docker.com/index.html)
* [docker-compose](https://docs.docker.com/compose/install/)

## Start mapserver in de docker

Note : In de docker-compose.yml staat volumes: - /tmp/srv/lufo:/srv/lufo. In Docker op MacOSX kan dit verschil problemen met opstarten geven)
Voor locale ontwikkeling maak aan de volgende directories: /tmp/srv/lufo en /tmp/srv/infrarood 
Om luchtfotos te gebruiken moet deze directories luchtfotos/infrarood bevatten of een symlink zijn naar luchtfotos/infrarood.
    
    docker-compose build
    docker-compose run -p "8383:80" -v /tmp/srv/lufo:/mnt/lufo -v /tmp/srv/infrarood/:/mnt/infrarood map



De Postgres database is te bereiken op tcp://localhost:5403

De laatste versie van de database kan opgehaald worden met:

    datasets="nap milieuthemas bag_v11 handelsregister monumenten overlastgebieden
        dataselectie various_small_datasets afvalcontainers dataservices"

    mkdir tmpdata
    for dataset in $datasets; do
        (cd tmpdata && curl -O https://admin.data.amsterdam.nl/postgres/${dataset}_latest.gz)
        docker cp tmpdata/${dataset}_latest.gz mapserver_database_1:/tmp
        docker-compose exec database update-db.sh $dataset
    done


De maps zijn te benaderen vanuit QGis: maak een WMS connectie met de url <http://localhost:8383/maps/YOURMAPFILE>
b.v. http://localhost:8383/maps/monumenten

## DEBUG Mapserver
Voeg de volgende files toe aan de file `header.inc` en start de docker opnieuw

```
        CONFIG   "MS_ERRORFILE" "/tmp/ms_error.txt"
        DEBUG    5

        docker-compose build map && docker-compose run -p "8383:80" map
```

 Na het opvragen van een map, zal dan de logging te zien zijn via:
 
        docker exec -it `docker-compose ps -q  map` bash -c 'tail -f /tmp/ms_error.txt'

De private docker image kan worden gebouwd met :

        docker-compose -f docker-compose-private.yml up -d database 
        docker-compose -f docker-compose-private.yml build map 
        docker-compose -f docker-compose-private.yml run -p "8383:80" map

De private maps kunnen met http://localhost:8383/maps/<map-name>?service=wfs&request=getcapabilities gevraagd worden

WMS services
------------

| Set     | URL                                                                                            |
| ------- | -----------------------------------------------------------------------------------------------|
| BAG     | /maps/bag&service=wms&request=getcapabilities                                                  |
| BRK     | /maps/brk&service=wms&request=getcapabilities                                                  |
| GBKA    | /maps/gbka&service=wms&request=getcapabilities                                                 |
| KBKA10  | /maps/kbka10&service=wms&request=getcapabilities                                               |
| KBKA50  | /maps/kbka50&service=wms&request=getcapabilities                                               |
| NAP     | /maps/nap&service=wms&request=getcapabilities                                                  |
| VLGH    | /maps/**externeveiligheid**&service=wms&request=getcapabilities                                |
| GBIEDN  | /maps/**gebieden**.map&service=wms&request=getcapabilities                                     |
| EIGENDM | /maps/eigendommen&service=wms&request=getcapabilities                                          |
| blackspots | /maps/blackspots&service=wms&request=getcapabilities                                          |


WFS services
------------

| Set    | URL                                                                  |
| ------ | ---------------------------------------------------------------------|
| BAG    | maps/bag&service=wfs&request=getcapabilities                         |
| BRK    | maps/brk&service=wfs&request=getcapabilities                         |
| NAP    | maps/nap&service=wfs&request=getcapabilities                         |
| blackspots | maps/blackspots&service=wfs&request=getcapabilities              |


TMS services
------------
Topo
Lufo
LKI kot



Test
----

Bijvoorbeeld de kaartserver in bag.map:

* wms capabilities:   <http://192.168.99.100:8989/cgi-bin/mapserv?map=/srv/mapserver/bag.map&service=wms&request=getcapabilities>
* kaart opvragen :    <http://192.168.99.100:8989/cgi-bin/mapserv?map=/srv/mapserver/bag.map&service=wms&request=getmap&version=1.3.0&layers=ligplaats&width=500&height=500&crs=epsg:28992&bbox=122000,487000,122250,487250&format=image/png>
* wfs capabilities:   <http://192.168.99.100:8989/cgi-bin/mapserv?map=/srv/mapserver/bag.map&service=wfs&request=getcapabilities>
* 1 feature opvragen: <http://192.168.99.100:8989/cgi-bin/mapserv?map=/srv/mapserver/bag.map&service=wfs&version=1.1.0&request=getfeature&typename=ligplaats&maxfeatures=1>

Monumenten
* wms kaart:
http://localhost:8989/maps/monumenten&SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&BBOX=119160,485473,124004,489948&CRS=EPSG:28992&WIDTH=1217&HEIGHT=1217&LAYERS=monument_coordinaten&STYLES=&FORMAT=image/png&DPI=72&MAP_RESOLUTION=72&FORMAT_OPTIONS=dpi:72&TRANSPARENT=false
http://localhost:8989/maps/monumenten&SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&BBOX=119160,485473,124004,489948&CRS=EPSG:28992&WIDTH=1217&HEIGHT=1217&LAYERS=monument_geometrie&STYLES=&FORMAT=image/png&DPI=72&MAP_RESOLUTION=72&FORMAT_OPTIONS=dpi:72&TRANSPARENT=false

Tiles generator for background in data.amsterdam.nl
----
Currently in Jenkis there are several jobs available that generate the tiles (.png's) for RD (normal,light and ZW). These tiles are generated based on data in the basiskaart database. Depending on the needed detail level (for instance level 9), they will used the schema KBK10 or KBK50. If there is a table selection error, like a table is missing, then the tiles generation cannot be completed with succes. The generator process will finish but the tiles will show a white space. Instead of a picture of the map. One way of debugging if that is the case, is to retreive a tile based upon the BBOX (as specified below). If there is an issue, it will be displayed as an error in the image itself (at top):

https://{URL_OF_MAPSERVER}/cgi-bin/mapserv?map=/srv/mapserver/topografie.map&SERVICE=WMS&VERSION=1.1.0&REQUEST=GetMap&BBOX=94100,464250,170000,514160&SRS=EPSG:28992&WIDTH=884&HEIGHT=884&LAYERS=basiskaart&STYLES=&FORMAT=image/png&DPI=96&MAP_RESOLUTION=6&FORMAT_OPTIONS=dpi:96&TRANSPARENT=TRUE
