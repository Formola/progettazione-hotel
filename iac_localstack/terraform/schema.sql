-- ========================================================
-- SCHEMA SQL Generato (post prog. concettuale e logica).
-- ========================================================

-- 1. Tabella USERS
-- Rappresenta gli utenti del sistema (registrati via Cognito)
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(50) PRIMARY KEY, -- ID generato dal Backend o Cognito
    cognito_uuid VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Tabella PROPERTIES
-- Le strutture alberghiere/immobili
CREATE TABLE IF NOT EXISTS properties (
    id VARCHAR(50) PRIMARY KEY,
    owner_id VARCHAR(50) NOT NULL,
    name VARCHAR(150) NOT NULL,
    address VARCHAR(255),
    city VARCHAR(100),
    country VARCHAR(100),
    description TEXT,
    status VARCHAR(20) DEFAULT 'DRAFT', -- Es: DRAFT, PUBLISHED, INACTIVE
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Vincolo Chiave Esterna
    CONSTRAINT fk_property_owner 
        FOREIGN KEY (owner_id) 
        REFERENCES users(id) 
        ON DELETE CASCADE
);

-- 3. Tabella ROOMS
-- Le stanze appartenenti a una proprietà
CREATE TABLE IF NOT EXISTS rooms (
    id VARCHAR(50) PRIMARY KEY,
    property_id VARCHAR(50) NOT NULL,
    type VARCHAR(50), -- Es: Singola, Doppia, Suite
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    capacity INTEGER,
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Vincolo Chiave Esterna
    CONSTRAINT fk_room_property 
        FOREIGN KEY (property_id) 
        REFERENCES properties(id) 
        ON DELETE CASCADE
);

-- 4. Tabella MEDIA
-- Gestione foto e file (collegati a proprietà o stanze)
CREATE TABLE IF NOT EXISTS media (
    id VARCHAR(50) PRIMARY KEY,
    property_id VARCHAR(50), -- Nullable: può riferirsi solo alla proprietà
    room_id VARCHAR(50),     -- Nullable: può riferirsi a una stanza specifica
    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(50),
    storage_path VARCHAR(255) NOT NULL, -- Percorso su S3
    description TEXT,
    inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Vincoli Chiavi Esterne
    CONSTRAINT fk_media_property FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE,
    CONSTRAINT fk_media_room FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE
);

-- 5. Tabelle AMENITIES (Cataloghi)
-- Servizi della proprietà (es. Wifi, Piscina)
CREATE TABLE IF NOT EXISTS property_amenities (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    category VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Servizi della stanza (es. Asciugacapelli, TV)
CREATE TABLE IF NOT EXISTS room_amenities (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    category VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. Tabelle DI COLLEGAMENTO (Many-to-Many)

-- Link Proprietà <-> Servizi
CREATE TABLE IF NOT EXISTS property_amenities_link (
    property_id VARCHAR(50) NOT NULL,
    amenity_id VARCHAR(50) NOT NULL,
    added_by VARCHAR(50), -- Opzionale: chi ha aggiunto il servizio (admin/owner)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (property_id, amenity_id), -- Chiave composta
    CONSTRAINT fk_link_prop_id FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE,
    CONSTRAINT fk_link_prop_amenity FOREIGN KEY (amenity_id) REFERENCES property_amenities(id) ON DELETE CASCADE
);

-- Link Stanze <-> Servizi
CREATE TABLE IF NOT EXISTS room_amenities_link (
    room_id VARCHAR(50) NOT NULL,
    amenity_id VARCHAR(50) NOT NULL,
    added_by VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (room_id, amenity_id), -- Chiave composta
    CONSTRAINT fk_link_room_id FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE,
    CONSTRAINT fk_link_room_amenity FOREIGN KEY (amenity_id) REFERENCES room_amenities(id) ON DELETE CASCADE
);


-- ========================================================
-- SEED DATA
-- ========================================================

-- Creiamo un utente
INSERT INTO users (id, cognito_uuid, name, email) 
VALUES ('user_01', 'cog_12345', 'Mario Rossi', 'mario@example.com')
ON CONFLICT (id) DO NOTHING;

-- Creiamo una proprietà dell'utente
INSERT INTO properties (id, owner_id, name, address, city, country, status)
VALUES ('prop_01', 'user_01', 'Hotel Bella Vista', 'Via Roma 1', 'Roma', 'Italy', 'PUBLISHED')
ON CONFLICT (id) DO NOTHING;

-- Creiamo due stanze per la proprietà
INSERT INTO rooms (id, property_id, type, price, capacity)
VALUES 
('room_101', 'prop_01', 'Doppia', 120.00, 2),
('room_102', 'prop_01', 'Suite', 250.00, 4)
ON CONFLICT (id) DO NOTHING;

-- Creiamo un servizio (Wifi) e colleghiamolo
INSERT INTO property_amenities (id, name, category) VALUES ('am_wifi', 'Free WiFi', 'General')
ON CONFLICT (id) DO NOTHING;

INSERT INTO property_amenities_link (property_id, amenity_id) VALUES ('prop_01', 'am_wifi')
ON CONFLICT (property_id, amenity_id) DO NOTHING;