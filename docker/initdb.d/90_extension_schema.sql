CREATE SCHEMA IF NOT EXISTS extensions;

-- Move postgis to the schema extensions, to match the refdb,
-- then add it to the search_path so that MapServer can find its functions.
-- See https://postgis.net/documentation/tips/tip-move-postgis-schema/ for
-- an explanation of this elaborate dance.
--
-- XXX This hack no longer works with PostGIS 3.4; the UPDATE TO statements
-- fail. Moving to another schema without those results in a broken extension.
UPDATE pg_extension SET
    extrelocatable = true
WHERE
    extname = 'postgis';

ALTER EXTENSION postgis SET SCHEMA extensions;

ALTER EXTENSION postgis UPDATE TO "2.5.5next";

ALTER EXTENSION postgis UPDATE TO "2.5.5";

-- Change search path for postgres user, permanently.
ALTER USER postgres SET SEARCH_PATH TO public, extensions, "$user";
