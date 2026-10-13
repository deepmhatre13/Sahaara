-- ============================================================================
-- Sahaara — local PostgreSQL bootstrap
--
-- Creates the `eldercare` role and `eldercare` database on the shared
-- PostgreSQL 17 instance that already hosts other local projects.
--
-- Run from the backend directory:
--   & 'C:\Program Files\PostgreSQL\17\bin\psql.exe' -U postgres `
--       -h 127.0.0.1 -p 5432 -d postgres -w -f scripts\init_db.sql
--
-- NOTE: use host 127.0.0.1 (IPv4), NOT `localhost`. On Windows `localhost`
-- resolves to ::1 (IPv6) first, and pg_hba.conf grants `trust` only for
-- 127.0.0.1/32 while ::1/128 requires scram-sha-256.
--
-- Both statements are idempotent and safe to re-run.
-- ============================================================================

-- 1) Role ---------------------------------------------------------------------
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'eldercare') THEN
        CREATE ROLE eldercare LOGIN PASSWORD 'eldercare';
        RAISE NOTICE 'Created role: eldercare';
    ELSE
        RAISE NOTICE 'Role already exists: eldercare';
    END IF;
END
$$;

-- 2) Database ----------------------------------------------------------------
-- CREATE DATABASE cannot run inside a transaction block or a DO block, so we
-- use \gexec: it builds the statement only when the database is missing.
SELECT 'CREATE DATABASE eldercare OWNER eldercare'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'eldercare')
\gexec
