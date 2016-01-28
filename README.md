Atlas map
=========

MapServer configuratie voor Atlas. 


Development 
-----------

* Installeer MapServer 6.1
* Kopieer connection-example.map naar connection.map en geef de juiste credentials op
* Ontwikkel met http://localhost/cgi-bin/mapserv?map=/srv/mapserver/atlas.map


Development met Docker
----------------------

Installeer:

* [docker](https://docs.docker.com/index.html)
* [docker-compose](https://docs.docker.com/compose/install/)

Kopieer `connection-example.map` naar `connection.map` en geef de juiste credentials op.

Draai

    cd atlas/git/atlas_map
	$ docker-compose up -d


WMS services
------------
BAG:    http://192.168.99.100:8989/cgi-bin/mapserv?map=/srv/mapserver/bag.map&service=wms&request=getcapabilities
WKPB:   http://192.168.99.100:8989/cgi-bin/mapserv?map=/srv/mapserver/wkpb.map&service=wms&request=getcapabilities
LKI:    http://192.168.99.100:8989/cgi-bin/mapserv?map=/srv/mapserver/lki.map&service=wms&request=getcapabilities
GBKA:   http://192.168.99.100:8989/cgi-bin/mapserv?map=/srv/mapserver/gbka.map&service=wms&request=getcapabilities
KBKA10: http://192.168.99.100:8989/cgi-bin/mapserv?map=/srv/mapserver/kbka10.map&service=wms&request=getcapabilities
KBKA50: http://192.168.99.100:8989/cgi-bin/mapserv?map=/srv/mapserver/kbka50.map&service=wms&request=getcapabilities
NAP:    http://192.168.99.100:8989/cgi-bin/mapserv?map=/srv/mapserver/nap.map&service=wms&request=getcapabilities
GBD:    


WFS services
------------
BAG:  http://192.168.99.100:8989/cgi-bin/mapserv?map=/srv/mapserver/bag.map&service=wfs&request=getcapabilities
WKPB: http://192.168.99.100:8989/cgi-bin/mapserv?map=/srv/mapserver/wkpb.map&service=wfs&request=getcapabilities
LKI:  http://192.168.99.100:8989/cgi-bin/mapserv?map=/srv/mapserver/lki.map&service=wfs&request=getcapabilities
NAP:  http://192.168.99.100:8989/cgi-bin/mapserv?map=/srv/mapserver/nap.map&service=wfs&request=getcapabilities
GBD:


TMS services
------------
Topo
Lufo
LKI kot



Test
---- 
bijvoorbeeld de kaartserver in bag.map:

* wms capabilities:   < http://192.168.99.100:8989/cgi-bin/mapserv?map=/srv/mapserver/bag.map&service=wms&request=getcapabilities >
* kaart opvragen :    < http://192.168.99.100:8989/cgi-bin/mapserv?map=/srv/mapserver/bag.map&service=wms&request=getmap&version=1.3.0&layers=ligplaats&width=500&height=500&crs=epsg:28992&bbox=122000,487000,122250,487250&format=image/png >
* wfs capabilities:   < http://192.168.99.100:8989/cgi-bin/mapserv?map=/srv/mapserver/bag.map&service=wfs&request=getcapabilities >
* 1 feature opvragen: < http://192.168.99.100:8989/cgi-bin/mapserv?map=/srv/mapserver/bag.map&service=wfs&version=1.1.0&request=getfeature&typename=ligplaats&maxfeatures=1 >
