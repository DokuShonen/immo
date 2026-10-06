-- Création des tables
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('client', 'bailleur', 'agent', 'manager')),
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100),
    raison_sociale VARCHAR(255),
    telephone VARCHAR(20),
    adresse TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE properties (
    id SERIAL PRIMARY KEY,
    bailleur_id INTEGER REFERENCES users(id),
    agent_id INTEGER REFERENCES users(id),
    titre VARCHAR(255) NOT NULL,
    type_bien VARCHAR(50) NOT NULL,
    usage_possible VARCHAR(50) NOT NULL,
    transaction_type VARCHAR(20) NOT NULL CHECK (transaction_type IN ('vente', 'location')),
    situation_geo VARCHAR(255) NOT NULL,
    taille INTEGER,
    prix DECIMAL(15,2) NOT NULL,
    description TEXT NOT NULL,
    is_featured BOOLEAN DEFAULT FALSE,
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE property_images (
    id SERIAL PRIMARY KEY,
    property_id INTEGER REFERENCES properties(id) ON DELETE CASCADE,
    image_path VARCHAR(500) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE favorites (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES users(id),
    property_id INTEGER REFERENCES properties(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(client_id, property_id)
);

CREATE TABLE appointments (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES users(id),
    property_id INTEGER REFERENCES properties(id),
    agent_id INTEGER REFERENCES users(id),
    date_rdv TIMESTAMP NOT NULL,
    type_rdv VARCHAR(20) NOT NULL CHECK (type_rdv IN ('visite', 'transaction')),
    notes TEXT,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'cancelled', 'completed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE client_assignments (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES users(id),
    agent_id INTEGER REFERENCES users(id),
    assigned_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Index pour performance
CREATE INDEX idx_properties_type ON properties(type_bien);
CREATE INDEX idx_properties_transaction ON properties(transaction_type);
CREATE INDEX idx_properties_price ON properties(prix);
CREATE INDEX idx_appointments_date ON appointments(date_rdv);
CREATE INDEX idx_favorites_client ON favorites(client_id);

-- Le hash pour 'password' est : $2b$12$Ea.mJ5iWJt3L8E0R5uR41u3lY8Fq.r5.i.hGz2Q/qP6uS4/T4p7Kq
-- NOTE: Ce hash a été généré avec la fonction auth_manager.hash_password('password')

INSERT INTO users (username, email, password_hash, role, nom, prenom, is_active) VALUES
('admin', 'admin@immo.com', '$2b$12$Ea.mJ5iWJt3L8E0R5uR41u3lY8Fq.r5.i.hGz2Q/qP6uS4/T4p7Kq', 'manager', 'Admin', 'Istrateur', TRUE),
('agent1', 'agent1@immo.com', '$2b$12$Ea.mJ5iWJt3L8E0R5uR41u3lY8Fq.r5.i.hGz2Q/qP6uS4/T4p7Kq', 'agent', 'Dupont', 'Jean', TRUE),
('bailleur1', 'bailleur1@immo.com', '$2b$12$Ea.mJ5iWJt3L8E0R5uR41u3lY8Fq.r5.i.hGz2Q/qP6uS4/T4p7Kq', 'bailleur', 'Martin', 'Sophie', TRUE),
('client1', 'client1@immo.com', '$2b$12$Ea.mJ5iWJt3L8E0R5uR41u3lY8Fq.r5.i.hGz2Q/qP6uS4/T4p7Kq', 'client', 'Durand', 'Paul', TRUE);

-- Script pour ajouter 5 propriétés de test.
-- Assurez-vous que les utilisateurs avec id=2 (agent) et id=3 (bailleur) existent.

INSERT INTO properties (bailleur_id, agent_id, titre, type_bien, usage_possible, transaction_type, situation_geo, taille, prix, description, is_featured) VALUES
(
    3, -- bailleur_id (bailleur1)
    2, -- agent_id (agent1)
    'Superbe Appartement T3 Lumineux - Centre-ville',
    'Appartement',
    'Résidentiel',
    'vente',
    'Paris 15ème',
    75,
    680000.00,
    'Magnifique appartement de 3 pièces entièrement rénové, situé au 4ème étage avec ascenseur. Comprend un grand salon avec balcon, deux chambres, une cuisine équipée et une salle de bain moderne. Très lumineux et sans vis-à-vis.',
    TRUE -- is_featured (Mise en avant)
),
(
    3, -- bailleur_id (bailleur1)
    2, -- agent_id (agent1)
    'Maison Familiale avec Jardin - Quartier Calme',
    'Maison',
    'Résidentiel',
    'location',
    'Versailles, Rive Droite',
    150,
    2500.00,
    'Charmante maison de 150m² sur un terrain de 400m². Elle se compose d''un double séjour donnant sur le jardin, 4 chambres à l''étage, 2 salles de bain. Idéal pour une famille. Proche des écoles et des transports.',
    FALSE
),
(
    3,
    2,
    'Plateau de Bureaux Modernes et Modulables',
    'Bureau',
    'Commercial',
    'location',
    'Lyon, La Part-Dieu',
    250,
    6000.00,
    'Espace de bureaux neuf et climatisé, situé dans un immeuble d''affaires de standing. Le plateau est livré en open space, facilement aménageable. Salles de réunion partagées et service d''accueil inclus.',
    FALSE
),
(
    3,
    2,
    'Local Commercial Emplacement N°1',
    'Commercial',
    'Commercial',
    'vente',
    'Bordeaux, Rue Sainte-Catherine',
    90,
    450000.00,
    'Opportunité rare ! Fonds de commerce à vendre sur l''artère la plus passante de Bordeaux. Excellente visibilité, vitrine de 8 mètres. Parfait pour une enseigne de prêt-à-porter ou de restauration rapide.',
    TRUE -- is_featured (Mise en avant)
),
(
    3,
    2,
    'Studio Meublé Proche Université',
    'Appartement',
    'Résidentiel',
    'location',
    'Toulouse, Rangueil',
    25,
    550.00,
    'Studio fonctionnel et entièrement meublé, idéal pour un étudiant. Kitchenette équipée, pièce de vie lumineuse, salle d''eau. À 5 minutes à pied du campus universitaire et du métro.',
    FALSE
);