CREATE SCHEMA IF NOT EXISTS extensions;

-- Move postgis to the schema extensions, to match the refdb,
-- then add it to the search_path so that MapServer can find its functions.
-- See https://postgis.net/documentation/tips/tip-move-postgis-schema/.

UPDATE
    pg_extension
SET
    extrelocatable = true
WHERE
    extname = 'postgis';

ALTER EXTENSION postgis SET SCHEMA extensions;

ALTER EXTENSION postgis UPDATE TO "3.2.3next";

ALTER EXTENSION postgis UPDATE TO "3.2.3";

-- Change search path for postgres user, permanently.
ALTER USER postgres SET SEARCH_PATH TO public, extensions, "$user";
