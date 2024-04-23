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
    permissions     VARCHAR(255)
);

-- Create the 'fires' table
CREATE TABLE public.fires (
    id              UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    type            VARCHAR(40) NOT NULL,
    date            DATE NOT NULL,
    reason          TEXT NOT NULL,
    location        VARCHAR(16) NOT NULL,
    state           VARCHAR(50) NOT NULL,
    status          VARCHAR(25) NOT NULL,
    user_id         UUID NOT NULL REFERENCES public.users(id)
);

-- Grant permissions to the 'api' user
GRANT SELECT, INSERT, UPDATE ON TABLE public.users TO api;
GRANT SELECT, INSERT, UPDATE ON TABLE public.fires TO api;
