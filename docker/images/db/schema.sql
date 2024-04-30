-- Create the database
CREATE DATABASE queimadas;

-- Connect to the new database
\c queimadas;

-- Create a user for API access
CREATE USER api WITH PASSWORD 'api';

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

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
);

-- Create the 'fires' table
CREATE TABLE public.fires (
    id              UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    date            DATE NOT NULL,
    location        VARCHAR(22) NOT NULL,
    observations    TEXT,
    type_id         INT NOT NULL,
    reason_id       INT NOT NULL,
    district_id     INT NOT NULL,
    user_id         UUID NOT NULL REFERENCES public.users(id)
);

-- Add status column to fires table
CREATE FUNCTION calculate_fire_status(date DATE) RETURNS TEXT AS $$
BEGIN
    RETURN CASE
        WHEN date > CURRENT_DATE THEN 'Marcado'
        WHEN date = CURRENT_DATE THEN 'Em Andamento'
        ELSE 'Realizado'
    END;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

ALTER TABLE public.fires 
ADD COLUMN status TEXT GENERATED ALWAYS AS (calculate_fire_status(date)) STORED;

-- Create the 'types' table
CREATE TABLE public.types (
    id SERIAL PRIMARY KEY,
    name_pt VARCHAR(255) NOT NULL,
    name_en VARCHAR(255) NOT NULL
);
ALTER TABLE public.fires ADD CONSTRAINT fk_type_id FOREIGN KEY (type_id) REFERENCES public.types(id);
INSERT INTO public.types (name_pt, name_en) VALUES ('Queima', 'Burning'), ('Queimada', 'Extended Burning');

-- Create the 'reasons' table
CREATE TABLE public.reasons (
    id SERIAL PRIMARY KEY,
    name_pt VARCHAR(255) NOT NULL,
    name_en VARCHAR(255) NOT NULL
);
ALTER TABLE public.fires ADD CONSTRAINT fk_reason_id FOREIGN KEY (reason_id) REFERENCES public.reasons(id);
INSERT INTO public.reasons (name_pt, name_en) 
VALUES 
    ('Queima Fitossanitária', 'Phytosanitary Burning'),
    ('Gestão de sobrantes agrícolas', 'Agricultural Surplus Management'),
    ('Gestão de sobrantes florestais', 'Forestry Surplus Management'),
    ('Gestão de matos', 'Brush Management'),
    ('Outro', 'Other');

-- Create the 'districts' table
CREATE TABLE public.districts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);
ALTER TABLE public.fires ADD CONSTRAINT fk_district_id FOREIGN KEY (district_id) REFERENCES public.districts(id);

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
GRANT SELECT, INSERT, UPDATE ON TABLE public.restrictions TO api;
