-- Migration 001 : table des tentatives de connexion.
--
-- Elle permet de limiter le nombre d'essais infructueux sur un meme
-- identifiant depuis une meme adresse IP.

CREATE TABLE IF NOT EXISTS login_attempts (
    id SERIAL PRIMARY KEY,
    username VARCHAR(191) NOT NULL,
    ip_address VARCHAR(45) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_login_attempts ON login_attempts(username, ip_address, created_at);
