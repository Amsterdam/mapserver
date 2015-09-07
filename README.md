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

	$ docker-compose up -d

Test
---- 
bijvoorbeeld de kaartserver in wkpb.map: 
* capabilities: <http://192.168.99.100:8989/cgi-bin/mapserv?map=/srv/mapserver/wkpb.map&service=wfs&request=getcapabilities> .
* 1 feature opvragen: <http://192.168.99.100:8989/cgi-bin/mapserv?map=/srv/mapserver/bag.map&service=wfs&version=1.1.0&request=getfeature&typename=ligplaats&maxfeatures=1>