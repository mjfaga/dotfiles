-- Step 1: Create the postgres_fdw extension if not already created
CREATE EXTENSION IF NOT EXISTS postgres_fdw;
CREATE EXTENSION IF NOT EXISTS citext;

-- Step 2: Create foreign servers for each database
CREATE SERVER atlas_server
  FOREIGN DATA WRAPPER postgres_fdw
  OPTIONS (host 'localhost', port '5432', dbname 'atlas_rails_development');

CREATE SERVER auth_server
  FOREIGN DATA WRAPPER postgres_fdw
  OPTIONS (host 'localhost', port '5432', dbname 'auth_atlas_rails_development');

CREATE SERVER multiverse_server
  FOREIGN DATA WRAPPER postgres_fdw
  OPTIONS (host 'localhost', port '5432', dbname 'multiverse_development');

CREATE SERVER solid_cache_server
  FOREIGN DATA WRAPPER postgres_fdw
  OPTIONS (host 'localhost', port '5432', dbname 'solid_cache_development');

-- Step 3: Create user mappings (assuming current user)
CREATE USER MAPPING FOR postgres
  SERVER atlas_server
  OPTIONS (user 'postgres');

CREATE USER MAPPING FOR postgres
  SERVER auth_server
  OPTIONS (user 'postgres');

CREATE USER MAPPING FOR postgres
  SERVER multiverse_server
  OPTIONS (user 'postgres');

CREATE USER MAPPING FOR postgres
  SERVER solid_cache_server
  OPTIONS (user 'postgres');

-- Step 4: Create destination schemas
CREATE SCHEMA IF NOT EXISTS atlas;
CREATE SCHEMA IF NOT EXISTS auth;
CREATE SCHEMA IF NOT EXISTS multiverse;
CREATE SCHEMA IF NOT EXISTS solid_cache;
CREATE SCHEMA IF NOT EXISTS multiverse_editable;
CREATE SCHEMA IF NOT EXISTS risingwave;

-- Step 5: Create helper function to import enum types
CREATE OR REPLACE FUNCTION import_enum_types(server_name text) RETURNS void AS $$
DECLARE
  foreign_pg_type_sql text;
  foreign_pg_enum_sql text;
  foreign_pg_namespace_sql text;
  enum_type record;
  enum_values text;
  create_cmd text;
BEGIN
  -- Create temporary foreign tables for PostgreSQL catalog
  foreign_pg_type_sql := format('
    CREATE FOREIGN TABLE temp_pg_type (
      oid oid,
      typname name,
      typnamespace oid,
      typowner oid,
      typlen smallint,
      typbyval boolean,
      typtype "char",
      typcategory "char",
      typisdefined boolean,
      typdelim "char",
      typrelid oid,
      typelem oid,
      typarray oid
    ) SERVER %I
    OPTIONS (schema_name ''pg_catalog'', table_name ''pg_type'');
  ', server_name);

  foreign_pg_enum_sql := format('
    CREATE FOREIGN TABLE temp_pg_enum (
      oid oid,
      enumtypid oid,
      enumsortorder real,
      enumlabel name
    ) SERVER %I
    OPTIONS (schema_name ''pg_catalog'', table_name ''pg_enum'');
  ', server_name);

  foreign_pg_namespace_sql := format('
    CREATE FOREIGN TABLE temp_pg_namespace (
      oid oid,
      nspname name
    ) SERVER %I
    OPTIONS (schema_name ''pg_catalog'', table_name ''pg_namespace'');
  ', server_name);

  EXECUTE foreign_pg_type_sql;
  EXECUTE foreign_pg_enum_sql;
  EXECUTE foreign_pg_namespace_sql;

  -- Loop through each enum type
  FOR enum_type IN
    SELECT t.typname, n.nspname
    FROM temp_pg_type t
    JOIN temp_pg_namespace n ON t.typnamespace = n.oid
    WHERE t.typtype = 'e' -- 'e' is for enum types
      AND n.nspname NOT IN ('pg_catalog', 'information_schema')
  LOOP
    -- Get the enum values as a comma-separated string
    EXECUTE format('
      SELECT string_agg(quote_literal(enumlabel), '', '' ORDER BY enumsortorder)
      FROM temp_pg_enum
      WHERE enumtypid = (
        SELECT oid FROM temp_pg_type
        WHERE typname = %L
          AND typnamespace = (
            SELECT oid FROM temp_pg_namespace
            WHERE nspname = %L
          )
      );
    ', enum_type.typname, enum_type.nspname) INTO enum_values;

    -- Prepare CREATE TYPE statement
    create_cmd := format('CREATE TYPE %I.%I AS ENUM (%s);',
                         enum_type.nspname, enum_type.typname, enum_values);

    -- Check if type already exists
    IF NOT EXISTS (
      SELECT 1 FROM pg_type t
      JOIN pg_namespace n ON t.typnamespace = n.oid
      WHERE t.typname = enum_type.typname AND n.nspname = enum_type.nspname
    ) THEN
      -- Create the enum type
      EXECUTE create_cmd;
      RAISE NOTICE 'Created enum type: %.%', enum_type.nspname, enum_type.typname;
    ELSE
      RAISE NOTICE 'Enum type %.% already exists', enum_type.nspname, enum_type.typname;
    END IF;
  END LOOP;

  -- Clean up temporary foreign tables
  DROP FOREIGN TABLE temp_pg_type;
  DROP FOREIGN TABLE temp_pg_enum;
  DROP FOREIGN TABLE temp_pg_namespace;
END;
$$ LANGUAGE plpgsql;

-- Step 6: Import enum types for each database
SELECT import_enum_types('atlas_server');
SELECT import_enum_types('auth_server');
SELECT import_enum_types('multiverse_server');
SELECT import_enum_types('solid_cache_server');

-- Step 7: Import foreign schemas
-- Atlas
IMPORT FOREIGN SCHEMA public
  FROM SERVER atlas_server
  INTO atlas;

-- Auth
IMPORT FOREIGN SCHEMA public
  FROM SERVER auth_server
  INTO auth;

-- Multiverse (public schema)
IMPORT FOREIGN SCHEMA public
  FROM SERVER multiverse_server
  INTO multiverse;

-- Multiverse (editable schema)
IMPORT FOREIGN SCHEMA editable
  FROM SERVER multiverse_server
  INTO multiverse_editable;

-- Multiverse (risingwave schema)
IMPORT FOREIGN SCHEMA risingwave
  FROM SERVER multiverse_server
  INTO risingwave;

-- Solid Cache
IMPORT FOREIGN SCHEMA public
  FROM SERVER solid_cache_server
  INTO solid_cache;

-- Step 8: Verify the imports (optional)
SELECT schemaname, tablename
FROM pg_tables
WHERE schemaname IN ('atlas', 'auth', 'multiverse', 'multiverse_editable', 'risingwave', 'solid_cache')
ORDER BY schemaname, tablename;
