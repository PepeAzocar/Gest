-- Run this once, as the postgres superuser, to create the app role and database.
-- Example: psql -U postgres -f scripts/init_db.sql

CREATE ROLE gest_app WITH LOGIN PASSWORD 'OYyYeFXb5jNVke5BgRltpj32f-Zsz51U';
CREATE DATABASE gest OWNER gest_app;
GRANT ALL PRIVILEGES ON DATABASE gest TO gest_app;
