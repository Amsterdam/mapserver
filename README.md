# City Data map


MapServer configuratie voor City Data.


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
    
    docker-compose build
    docker-compose run -p "8383:80" -v /tmp/srv/lufo:/srv/lufo map

Bij dit laatste commando moet de directory /tmp/srv/lufo local bestaan. Om luchtfotos te gebruiken moet deze
directory luchtfotos bevatten of een symlink zijn naar luchtfotos.

Note : In de docker-compose.yml staat volumes: - /srv/lufo:/srv/lufo. In Docker op MacOSX kan dit verschil problemen met opstarten geven)

De Postgres database is te bereiken op tcp://localhost:5403

De laatste versie van de database kan opgehaald worden met:

	docker-compose exec database update-db.sh nap <your-username>
	docker-compose exec database update-db.sh milieuthemas <your-username>
	docker-compose exec database update-db.sh bag <your-username>
	docker-compose exec database update-db.sh handelsregister <your-username>
	docker-compose exec database update-db.sh monumenten <your-username>
	docker-compose exec database update-db.sh overlastgebieden <your-username>

	
	
De maps zijn te benaderen vanuit QGis: maak een WMS connectie met de url <http://localhost:8383/maps/YOURMAPFILE>
b.v. http://localhost:8383:/maps/monumenten

## DEBUG Mapserver
Voeg de volgende files toe aan de file `header.inc` en start de docker opnieuw

        CONFIG   "MS_ERRORFILE" "/tmp/ms_error.txt"
        DEBUG    5
        
        docker-compose build map && docker-compose run -p "8383:80" -v /tmp/srv/lufo:/srv/lufo map
 
 Na het opvragen van een map, zal dan de logging te zien zijn via:
 
        docker exec -it `docker-compose ps -q  map` bash -c 'tail -f /tmp/ms_error.txt'

 Het private docker image kan worden gebouwd met :

        docker-compose -f docker-compose-private.yml build map && docker-compose run -p "8383:80" -v /tmp/srv/lufo:/srv/lufo map

WMS services
------------

| Set    | URL                                                                                                            |
| ------ | ---------------------------------------------------------------------------------------------------------------|
| BAG    | /maps/bag&service=wms&request=getcapabilities      |
| WKPB   | /maps/wkpb&service=wms&request=getcapabilities     |
| BRK    | /maps/brk&service=wms&request=getcapabilities      |
| GBKA   | /maps/gbka&service=wms&request=getcapabilities     |
| KBKA10 | /maps/kbka10&service=wms&request=getcapabilities   |
| KBKA50 | /maps/kbka50&service=wms&request=getcapabilities   |
| NAP    | /maps/nap&service=wms&request=getcapabilities      |
| VLGH   | /maps/**externeveiligheid**&service=wms&request=getcapabilities                                |
| GBIEDN | /maps/**gebieden**.map&service=wms&request=getcapabilities                                         |


WFS services
------------

| Set    | URL                                                                                                          |
| ------ | ------------------------------------------------------------------------------------------------------------ |
| BAG    | maps/bag&service=wfs&request=getcapabilities    |
| WKPB   | maps/wkpb&service=wfs&request=getcapabilities   |
| BRK    | maps/brk&service=wfs&request=getcapabilities    |
| NAP    | maps/nap&service=wfs&request=getcapabilities    |


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
