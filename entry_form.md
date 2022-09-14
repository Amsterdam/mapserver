# Map request form

## Introduction

This is a submission form used to request new maps or modify existing ones.

The services that can be requested through this form are:

- a WMS API served from `https://map.data.amsterdam.nl/maps`
- a frontend served from `https://data.amsterdam.nl/data/geozoek/?legenda=true` (Dataverkenner)

**Note that if your data is present in the reference database, the following services become available automagically:**  

- geosearch, a tool for geo-querying accross multiple datasets, served from `https://api.data.amsterdam.nl/geosearch/`  
  * you can verify this by checking whether the dataset is included in `https://api.data.amsterdam.nl/geosearch/catalogus/`
- a WFS API, served from `https://api.data.amsterdam.nl/v1/wfs/<dataset_name>/`

Some parts of this form are optional.  
If you don't need an option or you don't understand exactly what it means, you can leave it blank.

### Prerequisites:  

- The map data that must be described in [amsterdam-schema](https://github.com/Amsterdam/amsterdam-schema) and present in the reference database.
- This form must be filled out in English.

This form is written with a broad set of applicants in mind. If you have remarks for improvement, please let us know.

## 1 Clients and functionality
<br>

- Email contact person
- Name of map
  > *This can be an existing map, in which case the layers will be added*
- The map must be included in `data.amsterdam.nl` y/n
- Attribute information is exposed when clicking the geometry y/n
- Will the map be included in any other existing frontend? If yes, please fill out the URL and if possible, the team that maintains it.
- If possible, who are the expected clients?
  > *E.g. Data analysts using QGIS or ArcGIS, Users on `data.amsterdam.nl`*

## 2 Map
<br>

- id of the map
  > *the WMS service for the map will become available under the URL `https://map.data.amsterdam.nl/maps/<mapname>/`*

- OPTION user friendly name of the map

    *Defaults to the id*

## 3 Layers

### 3.1 Naming

- User-friendly name of the layer
  > *If you re-use layer names in different groups, it is advisable to include some prefix in the name*  
  > *to distinguish the identically named layers from each other.*  
  > *For example, if we have layer X in group A and B, the names can become "A - X" and "B - X"*  

- OPTION Group name of the layer:
  > *layers belonging to group X can be requested together by issuing: `https://map.data.amsterdam.nl/maps/<mapname>/?layers=X`)*

- OPTION id of the layer
  > *this will be used in the URL parameters: `https://map.data.amsterdam.nl/maps/<mapname>/?layers=<layerid>`)*  
  > *layer ids must be unique. If you re-use layer names in different groups, the id will automatically become "\<groupname\>_\<layerid\>"*

- OPTION User friendly description of the layer

### 3.2 Data

#### 3.2.1 Database

- id of the `amsterdam-schema` table that will provides the geometries
- OPTION id of the `amsterdam-schema` field that contains the geometry
  > *if this is blank, we will assume there is only 1 such field*
- OPTION id of the `amsterdam-schema` field that should be filtered on and value of the filter
  > *Fill this out if you want the layer to display only part of the data in the table*  
  > *Example: id = "thema" and value  = "milieu"*
- OPTION id of the `amsterdam-schema` field that will be used to categorize the data
  > *Fill this out if you want the layer to split data into groups that are displayed differently*  
  > *If this is filled out, there should be a category for each possible value and optionally a "rest" category*  
  > *If this is not filled out, there should be 1 category*  
- OPTION enumeration of the values of the map-categories to display
  > *These should be the values as they appear in the map*  
  > *For example: thema can be "A" or "B" or "Onbekend"*

#### 3.2.2 Categorization

- For each map-category under 3.2.1
  > *There is always at least 1 category*
- Color of the line, point or polygon to display

  + If the layer displays point geometries:
    - the symbol to use (defaults to a circle in the given color)
      >*For custom symbols, an svg should be attached to the form*
  + If there is a categorization field:
    - User friendly name of the category
    - OPTION Value(s) of the categorization field that belong to this category
      > *These should be the values as they appear in the database*  
      > *If this is left blank, it will serve as the "anything else" category*  
      > *For example:*
              >> *if thema is "A1" or "A2" in database, display as category "A" in the map*  
              >> *if thema is "B" in database, display as category "B" in the map*  
              >> *if thema is anything else, display as "Onbekend" in the map*  

### 3.3 Output

- OPTION display type of the data. Possible values are "point", "line", "polygon".
  > *If this is not filled out, the type of the geometry is assumed to be the output type.*  
  > *Additionally, sometimes the given type is not possible.  
  > For example, a point geometry can not be displayed as a polygon but a polygon geometry can be displayed as a point (using the centroid for example)*  
- OPTION projection given as EPSG identifier
  > *Defaults to the projection of the geometry in the database*
    *Example: "EPSG:28992"*
- OPTION map extent (improves performance if known beforehand)
  > *A bounding box that is guaranteed to contain all the geometries given as:*  
  > *"minx,miny,maxx,maxy" (Note that for EPSG:4326 x=lon and y=lat)*  
  > *Defaults to the extent of the data in the database*  

## 4 Authorization

For WFS, we use the authorization present on the amsterdam schema.
This is not the case for WMS, which is only protected by a VPN network, which is functionally equivalent to scope=FP/MDW

# Notes to self

- always make layer classes filterable with a custom parameter so that both layers and classes are toggleable
- we dont want to bother applicants with max/min zoom denominators, symbol scaling and aggregation. These things are at the discretion of the devs depending on the size, density and type of data.
- TODO: Clearly translate this to how it will look in QGIS and Dataverkenner with screenshots.

</form>