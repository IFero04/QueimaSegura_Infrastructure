-- Create the database
CREATE DATABASE queimadas;

-- Connect to the new database
\c queimadas;

-- Create a user for API access
CREATE USER api WITH PASSWORD 'api';

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Add status column to fires table
CREATE OR REPLACE FUNCTION calculate_fire_status(date DATE) RETURNS TEXT AS $$
BEGIN
    RETURN CASE
        WHEN date > CURRENT_DATE THEN 'Scheduled'
        WHEN date = CURRENT_DATE THEN 'Ongoing'
        ELSE 'Completed'
    END;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Create the 'users' table
CREATE TABLE public.users (
    id              UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    session_id      UUID,
    full_name       VARCHAR(255) NOT NULL,
    nif             VARCHAR(9) NOT NULL UNIQUE,
    email           VARCHAR(255) NOT NULL UNIQUE,
    password        VARCHAR(32) NOT NULL,
    avatar          VARCHAR(255),
    type            INT NOT NULL DEFAULT 0
);

-- Create the 'fires' table
CREATE TABLE public.fires (
    id              UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    date            DATE NOT NULL,
    location        VARCHAR(22),
    observations    TEXT,
    type_id         INT NOT NULL,
    reason_id       INT NOT NULL,
    zip_code_id     INT NOT NULL REFERENCES public.zip_codes(id),
    user_id         UUID NOT NULL REFERENCES public.users(id),
    status          TEXT GENERATED ALWAYS AS (calculate_fire_status(date)) STORED
);

CREATE TABLE public.permissions (
    id                  UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    fire_id             UUID NOT NULL REFERENCES public.fires(id),
    icn_permited        BOOLEAN NOT NULL DEFAULT TRUE,
    icn_reason          TEXT,
    icn_user_id         UUID REFERENCES public.users(id),
    gestor_permited     BOOLEAN NOT NULL DEFAULT TRUE,
    gestor_reason       TEXT,
    gestor_user_id      UUID REFERENCES public.users(id),
);

-- Create the 'types' table
CREATE TABLE public.types (
    id SERIAL PRIMARY KEY,
    name_pt VARCHAR(255) NOT NULL,
    name_en VARCHAR(255) NOT NULL
);
INSERT INTO public.types (name_pt, name_en) VALUES 
    ('Queima', 'Burning'), 
    ('Queimada', 'Controlled Burning');

-- Create the 'reasons' table
CREATE TABLE public.reasons (
    id SERIAL PRIMARY KEY,
    name_pt VARCHAR(255) NOT NULL,
    name_en VARCHAR(255) NOT NULL
);
INSERT INTO public.reasons (name_pt, name_en) VALUES 
    ('Queima Fitossanitária', 'Phytosanitary Burning'),
    ('Gestão de sobrantes agrícolas', 'Agricultural Surplus Management'),
    ('Gestão de sobrantes florestais', 'Forestry Surplus Management'),
    ('Gestão de matos', 'Brush Management'),
    ('Outro', 'Other');

-- Create the 'districts' table
CREATE TABLE public.districts (
    id INT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

-- Create the 'counties' table
CREATE TABLE public.counties (
    id SERIAL PRIMARY KEY,
    code INT NOT NULL,
    district_id INT REFERENCES public.districts(id) NOT NULL,
    name TEXT NOT NULL UNIQUE,
    UNIQUE (code, district_id)
);

-- Create the 'zip_codes' table
CREATE TABLE public.zip_codes (
    id SERIAL PRIMARY KEY,
    location_code INT NOT NULL,
    location_name TEXT NOT NULL,
    ART_code INT,
    ART_name TEXT,
    tronco TEXT,
    client TEXT,
    zip_code VARCHAR(8) NOT NULL,
    zip_name TEXT NOT NULL,
    county_id INT NOT NULL REFERENCES public.counties(id)
);

-- Create the 'restrictions' table
CREATE TABLE public.restrictions (
    id              UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    start_date      DATE NOT NULL,
    end_date        DATE NOT NULL,
    district_id     INT NOT NULL REFERENCES public.districts(id)
);

-- Grant permissions to the 'api' user
GRANT SELECT, INSERT, UPDATE ON TABLE public.users TO api;
GRANT SELECT, INSERT, UPDATE ON TABLE public.fires TO api;
GRANT SELECT ON TABLE public.types TO api;
GRANT SELECT ON TABLE public.reasons TO api;
GRANT SELECT ON TABLE public.districts TO api;
GRANT SELECT ON TABLE public.counties TO api;
GRANT SELECT ON TABLE public.zip_codes TO api;
GRANT SELECT, INSERT, UPDATE ON TABLE public.restrictions TO api;
