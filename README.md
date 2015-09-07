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
<http://192.168.99.100:8989/cgi-bin/mapserv?map=/srv/mapserver/wkpb.map&service=wfs&request=getcapabilities> .