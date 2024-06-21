-- Create the database
CREATE DATABASE queimadas;

-- Connect to the new database
\c queimadas;

-- Create a user for API access
CREATE USER api WITH PASSWORD 'api';

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Add status column to fires table
CREATE OR REPLACE FUNCTION calculate_fire_status(fire_date DATE) RETURNS TEXT AS $$
BEGIN
    RETURN CASE
        WHEN fire_date > CURRENT_DATE THEN 'Scheduled'
        WHEN fire_date = CURRENT_DATE THEN 'Ongoing'
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
    type            INT NOT NULL DEFAULT 0,
    active          BOOLEAN NOT NULL DEFAULT TRUE,
    deleted         BOOLEAN NOT NULL DEFAULT FALSE
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

CREATE TABLE public.controller(
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

INSERT INTO public.controller(name) VALUES ('Kanguru');

-- Create the 'districts' table
CREATE TABLE public.districts (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

-- Create the 'counties' table
CREATE TABLE public.counties (
    id SERIAL PRIMARY KEY,
    code INT NOT NULL,
    district_id INT NOT NULL REFERENCES public.districts(id),
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

-- Create the 'fires' table
CREATE TABLE public.fires (
    id              UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    date            DATE NOT NULL,
    location        VARCHAR(255),
    observations    TEXT,
    type_id         INT NOT NULL REFERENCES public.types(id),
    reason_id       INT NOT NULL REFERENCES public.reasons(id),
    zip_code_id     INT NOT NULL REFERENCES public.zip_codes(id),
    user_id         UUID NOT NULL REFERENCES public.users(id),
    status          TEXT GENERATED ALWAYS AS (calculate_fire_status(date)) STORED,
    cancelled       BOOLEAN NOT NULL DEFAULT FALSE
);

-- Create the 'permissions' table
CREATE TABLE public.permissions (
    id                  UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    fire_id             UUID NOT NULL REFERENCES public.fires(id),
    icnf_permited       BOOLEAN NOT NULL DEFAULT FALSE,
    icnf_reason         TEXT,
    icnf_number         TEXT,
    icnf_name           TEXT,
    gestor_permited     BOOLEAN NOT NULL DEFAULT FALSE,
    gestor_reason       TEXT,
    gestor_user_id      UUID REFERENCES public.users(id)
);


-- Grant permissions to the 'api' user
GRANT SELECT, INSERT, UPDATE ON public.users TO api;
GRANT SELECT, INSERT, UPDATE ON public.fires TO api;
GRANT SELECT, INSERT, UPDATE ON public.permissions TO api;
GRANT SELECT ON public.types TO api;
GRANT SELECT ON public.reasons TO api;
GRANT SELECT ON public.controller TO api;
GRANT SELECT ON public.districts TO api;
GRANT SELECT ON public.counties TO api;
GRANT SELECT ON public.zip_codes TO api;
GRANT SELECT, INSERT, UPDATE ON public.restrictions TO api;


INSERT INTO public.users(full_name, email, password, nif, type)
VALUES ('adm', 'adm@adm.adm', '210cf7aa5e2682c9c9d4511f88fe2789', 'adm', 2);
