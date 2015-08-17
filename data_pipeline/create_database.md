##Instructions for Creating a PostgreSQL Database for San Francisco Neighborhood Blocks

1. Brew install <b>PostGIS</b> :

 `brew install postgis`
  
  This library allows you to load .shp files and then export GeoJSON strings.


2. Whever you initialize a database, you have to give it post gis capabilities:
 ```sql
CREATE DATABASE <dbname>;
\q
psql <dbname>
CREATE EXTENSION POSTGIS 
```

3. Place shape files downloaded from the cenusus into PostgreSQL  This will create a table if one doesn't exist already. 
 
    `ogr2ogr -f "PostgreSQL" PG:"dbname= <dbname> user=<your psql username>" "<path to shapefile>/<shape file>" -nlt PROMOTE_TO_MULTI -nln <table name> -append`

    `ogr2ogr -f "PostgreSQL" PG:"dbname= zipfiantwitter user=clwilloughby" "/Users/clwilloughby/Documents/root/repos/mapping/data/tl_2014_06_tabblock10/" -nlt PROMOTE_TO_MULTI -nln sf_neighb -append`
    
    I had difficulties with instillation, and had to uninstall brew, then reinstall with:  
  
    ` brew install gdal --with-postgresql`