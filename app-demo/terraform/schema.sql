-- ========================================================
-- SCHEMA SQL Generato (post prog. concettuale e logica).
-- ========================================================

-- Tabella USERS
-- Rappresenta gli utenti del sistema (registrati via Cognito)
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(50) PRIMARY KEY, -- ID generato dal Backend o Cognito
    cognito_uuid VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabella PROPERTIES
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

-- Tabella ROOMS
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

-- Tabella MEDIA
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

-- Tabelle AMENITIES (Cataloghi)
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

-- Tabelle DI COLLEGAMENTO (Many-to-Many)

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
-- INDICI PER MIGLIORARE PERFORMANCE SEARCH
-- ========================================================

--- Gli indici B-tree sono indici che si basano su una struttura ad albero bilanciato (B-tree).
--- Sono ottimali per operazioni di ricerca, inserimento, cancellazione e ordinamento.
--- La complessità delle operazioni è logaritmica (O(log n)), rendendoli efficienti anche per grandi quantità di dati.

--- Gli indici GIN (Generalized Inverted Index) sono progettati per gestire dati complessi come array, JSONB e testo.
--- Sono particolarmente utili per ricerche che coinvolgono operatori di similarità, come le ricerche full-text e le ricerche con wildcard.
--- La complessità delle operazioni può variare, ma sono ottimizzati per velocizzare ricerche specifiche su grandi dataset.

-- Indice B-tree su 'status' della tabella properties
-- Tipo: B-tree (default)
-- Cosa fa: permette di filtrare rapidamente tutte le proprietà in base allo status (es. 'PUBLISHED')
-- Come si usa: viene utilizzato automaticamente nelle query con WHERE status = '...'
-- Cosa migliora: evita full table scan quando cerchiamo solo proprietà pubblicate
CREATE INDEX idx_properties_status ON properties(status);

-- Abilita l'estensione trigram per Postgres
-- Tipo: estensione Postgres
-- Cosa fa: permette di creare indici trigram (GIN) su colonne di testo
-- Come si usa: necessario prima di creare indici trigram su city e name
-- Cosa migliora: rende le ricerche con ILIKE '%term%' molto più veloci
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Indice trigram GIN sulla colonna 'city' della tabella properties
-- Tipo: GIN (trigram)
-- Cosa fa: velocizza le ricerche parziali case-insensitive su city, incluse query ILIKE '%...%'
-- Come si usa: Postgres utilizza automaticamente l'indice durante le query ILIKE
-- Cosa migliora: search per città veloce anche con molti record
CREATE INDEX idx_properties_city_trgm ON properties USING gin (city gin_trgm_ops);

-- Indice trigram GIN sulla colonna 'name' della tabella properties
-- Tipo: GIN (trigram)
-- Cosa fa: velocizza le ricerche parziali case-insensitive su name della proprietà
-- Come si usa: Postgres utilizza automaticamente l'indice durante le query ILIKE
-- Cosa migliora: search per nome hotel veloce anche con tanti record
CREATE INDEX idx_properties_name_trgm ON properties USING gin (name gin_trgm_ops);

-- Indice B-tree su 'property_id' della tabella rooms
-- Tipo: B-tree
-- Cosa fa: permette di recuperare rapidamente tutte le stanze di una proprietà specifica
-- Come si usa: viene utilizzato automaticamente nelle query con WHERE property_id = ANY(...)
-- Cosa migliora: evita full scan della tabella rooms quando recuperiamo stanze di più hotel
CREATE INDEX idx_rooms_property_id ON rooms(property_id);

-- Indice B-tree su 'property_id' della tabella media
-- Tipo: B-tree
-- Cosa fa: permette di recuperare rapidamente tutti i media collegati a una proprietà
-- Come si usa: utilizzato nelle query WHERE property_id = ANY(...)
-- Cosa migliora: evita full scan della tabella media quando carichiamo le foto/asset di più hotel
CREATE INDEX idx_media_property_id ON media(property_id);

-- Indice B-tree su 'property_id' della tabella property_amenities_link
-- Tipo: B-tree
-- Cosa fa: velocizza il recupero delle amenities associate a una proprietà
-- Come si usa: utilizzato nelle query JOIN property_amenities_link l ON l.property_id = ...
-- Cosa migliora: evita full scan della tabella link quando recuperiamo amenities di più hotel
CREATE INDEX idx_prop_amenities_link_pid ON property_amenities_link(property_id);

-- Indice B-tree su 'room_id' della tabella room_amenities_link
-- Tipo: B-tree
-- Cosa fa: velocizza il recupero delle amenities associate a una stanza
-- Come si usa: utilizzato nelle query JOIN room_amenities_link l ON l.room_id = ...
-- Cosa migliora: evita full scan della tabella link quando recuperiamo amenities di più stanze
CREATE INDEX idx_room_amenities_link_rid ON room_amenities_link(room_id);



-- ========================================================
-- SEED: UTENTE + 10 HOTEL CON STANZE E AMENITIES
-- ========================================================

-- Creiamo un utente
INSERT INTO users (id, cognito_uuid, name, email) 
VALUES ('user_01', 'cog_12345', 'Mario Rossi', 'mario@example.com')
ON CONFLICT (id) DO NOTHING;

-- Amenities property (predefinite)
INSERT INTO property_amenities (id, name, category) VALUES
('am_wifi', 'Free WiFi', 'Generale'),
('am_pool', 'Piscina', 'Generale'),
('am_parking', 'Parcheggio', 'Generale')
ON CONFLICT (id) DO NOTHING;

-- Amenities room
INSERT INTO room_amenities (id, name, category) VALUES
('ra_tv', 'TV', 'Comfort'),
('ra_hairdryer', 'Asciugacapelli', 'Comfort'),
('ra_minibar', 'Minibar', 'Comfort')
ON CONFLICT (id) DO NOTHING;

-- Creazione
INSERT INTO properties (id, owner_id, name, address, city, country, status)
VALUES
('prop_01', 'user_01', 'Dragonfly Inn', '123 Main St', 'Stars Hollow', 'USA', 'PUBLISHED'),
('prop_02', 'user_01', 'Bates Motel', '12 Highway 90', 'Fairvale', 'USA', 'PUBLISHED'),     
('prop_03', 'user_01', 'Overlook Hotel', 'Room 237 Rd', 'Sidewinder', 'USA', 'PUBLISHED'),   
('prop_04', 'user_01', 'Continental Hotel', '1 Assassin St', 'New York', 'USA', 'PUBLISHED'), 
('prop_05', 'user_01', 'Hotel California', '42 Sunset Blvd', 'Los Angeles', 'USA', 'PUBLISHED'),
('prop_06', 'user_01', 'Grand Budapest', '1 Zubrowka Ln', 'Zubrowka', 'Fictional', 'PUBLISHED'),
('prop_07', 'user_01', 'The Great Northern', '500 Twin Peaks Rd', 'Twin Peaks', 'USA', 'PUBLISHED'), 
('prop_08', 'user_01', 'Beverly Hills Hotel', '9641 Sunset Blvd', 'Los Angeles', 'USA', 'PUBLISHED'), 
('prop_09', 'user_01', 'Raddison Blue', '10 Central St', 'Paris', 'France', 'PUBLISHED'), 
('prop_10', 'user_01', 'Plaza Hotel', '768 5th Ave', 'New York', 'USA', 'PUBLISHED')
ON CONFLICT (id) DO NOTHING;

-- Collegamento amenities property (tutti hotel: Wifi + Pool)
INSERT INTO property_amenities_link (property_id, amenity_id) VALUES
('prop_01','am_wifi'),('prop_01','am_pool'),
('prop_02','am_wifi'),('prop_02','am_pool'),
('prop_03','am_wifi'),('prop_03','am_pool'),
('prop_04','am_wifi'),('prop_04','am_pool'),
('prop_05','am_wifi'),('prop_05','am_pool'),
('prop_06','am_wifi'),('prop_06','am_pool'),
('prop_07','am_wifi'),('prop_07','am_pool'),
('prop_08','am_wifi'),('prop_08','am_pool'),
('prop_09','am_wifi'),('prop_09','am_pool'),
('prop_10','am_wifi'),('prop_10','am_pool')
ON CONFLICT (property_id, amenity_id) DO NOTHING;

-- Stanze per ogni hotel (1–3 stanze diverse)
INSERT INTO rooms (id, property_id, type, price, capacity)
VALUES
('room_01_1','prop_01','Singola',100.00,1),
('room_01_2','prop_01','Doppia',150.00,2),
('room_01_3','prop_01','Suite',250.00,4),

('room_02_1','prop_02','Doppia',130.00,2),
('room_02_2','prop_02','Suite',220.00,3),

('room_03_1','prop_03','Singola',90.00,1),
('room_03_2','prop_03','Doppia',140.00,2),

('room_04_1','prop_04','Suite',200.00,3),

('room_05_1','prop_05','Singola',120.00,1),
('room_05_2','prop_05','Doppia',170.00,2),

('room_06_1','prop_06','Doppia',160.00,2),
('room_06_2','prop_06','Suite',280.00,4),

('room_07_1','prop_07','Singola',95.00,1),
('room_07_2','prop_07','Doppia',155.00,2),
('room_07_3','prop_07','Suite',260.00,3),

('room_08_1','prop_08','Doppia',180.00,2),

('room_09_1','prop_09','Singola',80.00,1),
('room_09_2','prop_09','Doppia',130.00,2),

('room_10_1','prop_10','Suite',300.00,4)
ON CONFLICT (id) DO NOTHING;

-- Collegamento amenities room (TV + Hairdryer)
INSERT INTO room_amenities_link (room_id, amenity_id) VALUES
('room_01_1','ra_tv'),('room_01_1','ra_hairdryer'),
('room_01_2','ra_tv'),('room_01_2','ra_hairdryer'),
('room_01_3','ra_tv'),('room_01_3','ra_hairdryer'),

('room_02_1','ra_tv'),('room_02_1','ra_hairdryer'),
('room_02_2','ra_tv'),('room_02_2','ra_hairdryer'),

('room_03_1','ra_tv'),('room_03_1','ra_hairdryer'),
('room_03_2','ra_tv'),('room_03_2','ra_hairdryer'),

('room_04_1','ra_tv'),('room_04_1','ra_hairdryer'),

('room_05_1','ra_tv'),('room_05_1','ra_hairdryer'),
('room_05_2','ra_tv'),('room_05_2','ra_hairdryer'),

('room_06_1','ra_tv'),('room_06_1','ra_hairdryer'),
('room_06_2','ra_tv'),('room_06_2','ra_hairdryer'),

('room_07_1','ra_tv'),('room_07_1','ra_hairdryer'),
('room_07_2','ra_tv'),('room_07_2','ra_hairdryer'),
('room_07_3','ra_tv'),('room_07_3','ra_hairdryer'),

('room_08_1','ra_tv'),('room_08_1','ra_hairdryer'),

('room_09_1','ra_tv'),('room_09_1','ra_hairdryer'),
('room_09_2','ra_tv'),('room_09_2','ra_hairdryer'),

('room_10_1','ra_tv'),('room_10_1','ra_hairdryer')
ON CONFLICT (room_id, amenity_id) DO NOTHING;


INSERT INTO media (id, property_id, room_id, file_name, file_type, storage_path)
VALUES
('media_01','prop_01',NULL,'front.png','image/png','http://localstack:4566/my-app-media-assets-local/prop01/front.png'),
('media_02','prop_02',NULL,'front.png','image/png','http://localstack:4566/my-app-media-assets-local/prop02/front.png'),
('media_03','prop_03',NULL,'front.png','image/png','http://localstack:4566/my-app-media-assets-local/prop03/front.png'),
('media_04','prop_03',NULL,'interior.png','image/png','http://localstack:4566/my-app-media-assets-local/prop03/interior.png'),
('media_05','prop_03',NULL,'hall.png','image/png','http://localstack:4566/my-app-media-assets-local/prop03/hall.png'),
('media_06','prop_04',NULL,'front.png','image/png','http://localstack:4566/my-app-media-assets-local/prop04/front.png'),
('media_07','prop_05',NULL,'front.png','image/png','http://localstack:4566/my-app-media-assets-local/prop05/front.png'),
('media_08','prop_06',NULL,'front.png','image/png','http://localstack:4566/my-app-media-assets-local/prop06/front.png'),
('media_09','prop_07',NULL,'front.png','image/png','http://localstack:4566/my-app-media-assets-local/prop07/front.png'),
('media_10','prop_07',NULL,'hall.png','image/png','http://localstack:4566/my-app-media-assets-local/prop07/hall.png'),
('media_11','prop_08',NULL,'front.png','image/png','http://localstack:4566/my-app-media-assets-local/prop08/front.png'),
('media_12','prop_08',NULL,'hall.png','image/png','http://localstack:4566/my-app-media-assets-local/prop08/hall.png'),
('media_13','prop_09',NULL,'front.png','image/png','http://localstack:4566/my-app-media-assets-local/prop09/front.png'),
('media_14','prop_09',NULL,'pool.png','image/png','http://localstack:4566/my-app-media-assets-local/prop09/pool.png'),
('media_15','prop_10',NULL,'front.png','image/png','http://localstack:4566/my-app-media-assets-local/prop10/front.png'),
('media_16','prop_10',NULL,'hall.png','image/png','http://localstack:4566/my-app-media-assets-local/prop10/hall.png')
ON CONFLICT (id) DO NOTHING;