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
    custom_description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (property_id, amenity_id), -- Chiave composta
    CONSTRAINT fk_link_prop_id FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE,
    CONSTRAINT fk_link_prop_amenity FOREIGN KEY (amenity_id) REFERENCES property_amenities(id) ON DELETE CASCADE
);

-- Link Stanze <-> Servizi
CREATE TABLE IF NOT EXISTS room_amenities_link (
    room_id VARCHAR(50) NOT NULL,
    amenity_id VARCHAR(50) NOT NULL,
    custom_description TEXT,
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
-- SEED: UTENTE + 10 HOTEL CON STANZE E AMENITIES COMPLETE
-- ========================================================

INSERT INTO users (id, cognito_uuid, name, email) 
VALUES ('user_01', 'cog_12345', 'Jack Torrance', 'jacktorrance@shining.com')
ON CONFLICT (id) DO NOTHING;

-- ==========================================
-- PROPERTY AMENITIES (10 essenziali)
-- ==========================================

INSERT INTO property_amenities (id, name, category, description) VALUES
('pa_wifi', 'Free WiFi', 'Generale', 'High-speed wireless internet access throughout the property'),
('pa_pool', 'Pool', 'Generale', 'Outdoor or indoor swimming pool available for guests'),
('pa_parking', 'Parking', 'Generale', 'Free parking facilities on-site or nearby'),
('pa_gym', 'Gym', 'Fitness & Wellness', 'Fully equipped fitness center with modern equipment'),
('pa_spa', 'Spa & Wellness', 'Fitness & Wellness', 'Spa facilities including massage and wellness treatments'),
('pa_restaurant', 'Restaurant', 'Ristorazione', 'On-site restaurant serving breakfast, lunch, and dinner'),
('pa_bar', 'Bar', 'Ristorazione', 'Bar or lounge area serving drinks and light snacks'),
('pa_beach', 'Beach Access', 'Outdoor', 'Direct beach access or beach shuttle service'),
('pa_pets', 'Pet-Friendly', 'Servizi', 'Pets are welcome with additional fees'),
('pa_reception24', 'Reception 24h', 'Servizi', '24-hour front desk service and concierge')
ON CONFLICT (id) DO NOTHING;

-- ==========================================
-- ROOM AMENITIES (6 essenziali)
-- ==========================================

INSERT INTO room_amenities (id, name, category, description) VALUES
('ra_ac', 'Air Conditioning', 'Comfort', 'Individual climate control in each room'),
('ra_tv', 'Satellite TV', 'Entertainment', 'Flat-screen TV with satellite or cable channels'),
('ra_hairdryer', 'Hairdryer', 'Bathroom', 'Hairdryer available in the bathroom'),
('ra_minibar', 'Minibar', 'Comfort', 'Mini refrigerator stocked with beverages and snacks'),
('ra_safe', 'Safe', 'Security', 'In-room safe for valuables'),
('ra_balcony', 'Balcony/View', 'View & Space', 'Private balcony or room with scenic view')
ON CONFLICT (id) DO NOTHING;

-- ==========================================
-- PROPERTIES (10 Hotel)
-- ==========================================

INSERT INTO properties (id, owner_id, name, address, city, country, status, description)
VALUES
('prop_01', 'user_01', 'Dragonfly Inn', '123 Main St', 'Stars Hollow', 'USA', 'PUBLISHED', 'A cozy inn with a rustic charm. Gilmore Girls fans welcome!'),
('prop_02', 'user_01', 'Bates Motel', '12 Highway 90', 'Fairvale', 'USA', 'PUBLISHED', 'A quaint motel with a mysterious past. Psycho fans welcome!'),     
('prop_03', 'user_01', 'Overlook Hotel', 'Room 237 Rd', 'Sidewinder', 'USA', 'PUBLISHED', 'A grand hotel with a haunting history. The Shining fans welcome!'),   
('prop_04', 'user_01', 'Continental Hotel', '1 Assassin St', 'New York', 'USA', 'PUBLISHED', 'A luxurious hotel catering to elite guests. John Wick fans welcome!'), 
('prop_05', 'user_01', 'Hotel California', '42 Sunset Blvd', 'Los Angeles', 'USA', 'PUBLISHED', 'You can check out any time you like, but you can never leave. Eagles fans welcome!'),
('prop_06', 'user_01', 'Grand Budapest', '1 Zubrowka Ln', 'Zubrowka', 'Fictional', 'PUBLISHED', 'A legendary hotel in a fictional European country. Wes Anderson fans welcome!'),
('prop_07', 'user_01', 'The Great Northern', '500 Twin Peaks Rd', 'Twin Peaks', 'USA', 'PUBLISHED', 'A cozy mountain lodge with a mysterious atmosphere. Twin Peaks fans welcome!'), 
('prop_08', 'user_01', 'Beverly Hills Hotel', '9641 Sunset Blvd', 'Los Angeles', 'USA', 'PUBLISHED', 'A glamorous hotel known for its celebrity guests. A place to see and be seen.'), 
('prop_09', 'user_01', 'Radisson Blue', '10 Central St', 'Paris', 'France', 'PUBLISHED', 'A stylish hotel in the heart of Paris. Experience luxury and comfort.'), 
('prop_10', 'user_01', 'Plaza Hotel', '768 5th Ave', 'New York', 'USA', 'PUBLISHED', 'An iconic hotel located in the heart of New York City. Experience elegance and sophistication.')
ON CONFLICT (id) DO NOTHING;

-- ==========================================
-- COLLEGAMENTO PROPERTY AMENITIES
-- ==========================================

-- prop_01: Dragonfly Inn (Cozy inn) → WiFi, Parking, Restaurant, Reception
INSERT INTO property_amenities_link (property_id, amenity_id, custom_description) VALUES
('prop_01', 'pa_wifi', 'High speed fiber optic everywhere'),
('prop_01', 'pa_parking', 'Free vallet parking'),
('prop_01', 'pa_restaurant', 'Gourmet on-site restaurant'),
('prop_01', 'pa_reception24', '24/7 front desk service')
ON CONFLICT (property_id, amenity_id) DO NOTHING;

-- prop_02: Bates Motel (Budget motel) → WiFi, Parking
INSERT INTO property_amenities_link (property_id, amenity_id, custom_description) VALUES
('prop_02', 'pa_wifi', 'Basic free WiFi in rooms'),
('prop_02', 'pa_parking', 'Free parking available')
ON CONFLICT (property_id, amenity_id) DO NOTHING;

-- prop_03: Overlook Hotel (Grand hotel) → WiFi, Pool, Gym, Restaurant, Bar, Reception
INSERT INTO property_amenities_link (property_id, amenity_id, custom_description) VALUES
('prop_03', 'pa_wifi', 'High-speed WiFi throughout the hotel'),
('prop_03', 'pa_pool', 'Indoor heated pool available year-round'),
('prop_03', 'pa_gym', 'Fully equipped fitness center'),
('prop_03', 'pa_restaurant', 'Fine dining restaurant with local cuisine'),
('prop_03', 'pa_bar', 'Cozy bar with a wide selection of drinks'),
('prop_03', 'pa_reception24', '24/7 front desk service')
ON CONFLICT (property_id, amenity_id) DO NOTHING;

-- prop_04: Continental Hotel (Luxury) → ALL amenities except Beach
INSERT INTO property_amenities_link (property_id, amenity_id, custom_description) VALUES
('prop_04', 'pa_wifi', 'Ultra-fast premium WiFi'),
('prop_04', 'pa_pool', 'Indoor heated pool available year-round'),
('prop_04', 'pa_parking', 'Valet parking service'),
('prop_04', 'pa_gym', 'State-of-the-art fitness center'),
('prop_04', 'pa_spa', 'Full-service spa and wellness center'),
('prop_04', 'pa_restaurant', 'Gourmet dining with international cuisine'),
('prop_04', 'pa_bar', 'Elegant bar with premium selection'),
('prop_04', 'pa_pets', 'Pet-friendly accommodations'),
('prop_04', 'pa_reception24', '24/7 front desk service')
ON CONFLICT (property_id, amenity_id) DO NOTHING;

-- prop_05: Hotel California → WiFi, Pool, Bar, Parking
INSERT INTO property_amenities_link (property_id, amenity_id, custom_description) VALUES
('prop_05', 'pa_wifi', 'Reliable WiFi for all guests'),
('prop_05', 'pa_pool', 'Outdoor pool with sun loungers'),
('prop_05', 'pa_bar', 'Casual bar with live music'),
('prop_05', 'pa_parking', 'Ample free parking space')
ON CONFLICT (property_id, amenity_id) DO NOTHING;

-- prop_06: Grand Budapest (Elegant) → WiFi, Restaurant, Bar, Reception, Spa
INSERT INTO property_amenities_link (property_id, amenity_id, custom_description) VALUES
('prop_06', 'pa_wifi', 'High-speed WiFi throughout the hotel'),
('prop_06', 'pa_restaurant', 'Fine dining restaurant with local cuisine'),
('prop_06', 'pa_bar', 'Cozy bar with a wide selection of drinks'),
('prop_06', 'pa_reception24', '24/7 front desk service'),
('prop_06', 'pa_spa', 'Full-service spa and wellness center')
ON CONFLICT (property_id, amenity_id) DO NOTHING;

-- prop_07: The Great Northern (Mountain lodge) → WiFi, Restaurant, Bar, Parking
INSERT INTO property_amenities_link (property_id, amenity_id, custom_description) VALUES
('prop_07', 'pa_wifi', 'Reliable WiFi for all guests'),
('prop_07', 'pa_restaurant', 'Cozy mountain lodge restaurant'),
('prop_07', 'pa_bar', 'Rustic bar with local brews'),
('prop_07', 'pa_parking', 'Free parking available')
ON CONFLICT (property_id, amenity_id) DO NOTHING;

-- prop_08: Beverly Hills Hotel (Glamorous) → ALL amenities except Beach
INSERT INTO property_amenities_link (property_id, amenity_id, custom_description) VALUES
('prop_08', 'pa_wifi', 'Beverly Hills premium WiFi'),
('prop_08', 'pa_pool', 'Luxurious outdoor pool with cabanas'),
('prop_08', 'pa_parking', 'Valet parking service'),
('prop_08', 'pa_gym', 'State-of-the-art fitness center'),
('prop_08', 'pa_spa', 'Full-service spa and wellness center'),
('prop_08', 'pa_restaurant', 'Gourmet dining with international cuisine'),
('prop_08', 'pa_bar', 'Elegant bar with premium selection'),
('prop_08', 'pa_pets', 'Pet-friendly accommodations'),
('prop_08', 'pa_reception24', '24/7 front desk service')
ON CONFLICT (property_id, amenity_id) DO NOTHING;

-- prop_09: Radisson Blue Paris (Modern) → WiFi, Gym, Restaurant, Bar, Reception
INSERT INTO property_amenities_link (property_id, amenity_id, custom_description) VALUES
('prop_09', 'pa_wifi', 'High-speed WiFi throughout the hotel'),
('prop_09', 'pa_gym', 'State-of-the-art fitness center'),
('prop_09', 'pa_restaurant', 'Modern restaurant with diverse menu'),
('prop_09', 'pa_bar', 'Trendy bar with craft cocktails'),
('prop_09', 'pa_reception24', '24/7 front desk service')
ON CONFLICT (property_id, amenity_id) DO NOTHING;

-- prop_10: Plaza Hotel (Iconic luxury) → ALL amenities except Beach and Pets
INSERT INTO property_amenities_link (property_id, amenity_id, custom_description) VALUES
('prop_10', 'pa_wifi', 'High-speed WiFi throughout the hotel'),
('prop_10', 'pa_pool', 'Luxurious outdoor pool with cabanas'),
('prop_10', 'pa_parking', 'Valet parking service'),
('prop_10', 'pa_gym', 'State-of-the-art fitness center'),
('prop_10', 'pa_spa', 'Full-service spa and wellness center'),
('prop_10', 'pa_restaurant', 'Gourmet dining with international cuisine'),
('prop_10', 'pa_bar', 'Elegant bar with premium selection'),
('prop_10', 'pa_reception24', '24/7 front desk service')
ON CONFLICT (property_id, amenity_id) DO NOTHING;

-- ==========================================
-- ROOMS (Stanze per ogni hotel)
-- ==========================================

INSERT INTO rooms (id, property_id, type, price, capacity, description)
VALUES
-- Dragonfly Inn (3 stanze)
('room_01_1','prop_01','SINGLE',100.00,1, 'Cozy single room with all basic amenities.'),
('room_01_2','prop_01','DOUBLE',150.00,2, 'Comfortable double room with modern facilities.'),
('room_01_3','prop_01','SUITE',250.00,4, 'Spacious suite with premium amenities.'),

-- Bates Motel (2 stanze)
('room_02_1','prop_02','DOUBLE',130.00,2, 'Comfortable double room with modern facilities.'),
('room_02_2','prop_02','SUITE',220.00,3, 'Spacious suite with premium amenities.'),

-- Overlook Hotel (2 stanze)
('room_03_1','prop_03','SINGLE',90.00,1, 'Cozy single room with all basic amenities.'),
('room_03_2','prop_03','DOUBLE',140.00,2, 'Comfortable double room with modern facilities.'),

-- Continental Hotel (1 suite luxury)
('room_04_1','prop_04','SUITE',200.00,3, 'Spacious suite with premium amenities.'),

-- Hotel California (2 stanze)
('room_05_1','prop_05','SINGLE',120.00,1, 'Cozy single room with all basic amenities.'),
('room_05_2','prop_05','DOUBLE',170.00,2, 'Comfortable double room with modern facilities.'),
-- Grand Budapest (2 stanze)
('room_06_1','prop_06','DOUBLE',160.00,2, 'Comfortable double room with modern facilities.'),
('room_06_2','prop_06','SUITE',280.00,4, 'Spacious suite with premium amenities.'),

-- The Great Northern (3 stanze)
('room_07_1','prop_07','SINGLE',95.00,1, 'Cozy single room with all basic amenities.'),
('room_07_2','prop_07','DOUBLE',155.00,2, 'Comfortable double room with modern facilities.'),
('room_07_3','prop_07','SUITE',260.00,3, 'Spacious suite with premium amenities.'),

-- Beverly Hills Hotel (1 doppia)
('room_08_1','prop_08','DOUBLE',180.00,2, 'Comfortable double room with modern facilities.'),
-- Radisson Blue (2 stanze)
('room_09_1','prop_09','SINGLE',80.00,1, 'Cozy single room with all basic amenities.'),
('room_09_2','prop_09','DOUBLE',130.00,2, 'Comfortable double room with modern facilities.'),

-- Plaza Hotel (1 suite luxury)
('room_10_1','prop_10','SUITE',300.00,4, 'Spacious suite with premium amenities.')
ON CONFLICT (id) DO NOTHING;

-- ==========================================
-- COLLEGAMENTO ROOM AMENITIES
-- ==========================================

-- Stanze SINGOLE → Base amenities (AC, TV, Hairdryer)
-- custom description is specific for the room of that amenity for that room in that hotel
-- differs from basic description in room_amenities table
INSERT INTO room_amenities_link (room_id, amenity_id, custom_description) VALUES
('room_01_1', 'ra_ac', 'This room has a modern air conditioning system.'),
('room_01_1', 'ra_tv', 'Flat-screen TV with cable channels.'),
('room_01_1', 'ra_hairdryer', 'In-room hairdryer for your convenience.'),

('room_03_1', 'ra_ac', 'New air conditioning unit installed.'),
('room_03_1', 'ra_tv', '42-inch flat-screen TV with satellite channels.'),
('room_03_1', 'ra_hairdryer', 'Special hairdryer with multiple settings.'),

('room_05_1', 'ra_ac', 'Quiet air conditioning for a restful sleep.'),
('room_05_1', 'ra_tv', 'Smart TV with streaming apps available.'),
('room_05_1', 'ra_hairdryer', 'Compact hairdryer for easy use.'),


('room_07_1', 'ra_ac', 'Energy-efficient air conditioning system.'),
('room_07_1', 'ra_tv', 'Television with local and international channels.'),
('room_07_1', 'ra_hairdryer', 'Hairdryer with multiple heat settings.'),

('room_09_1', 'ra_ac', 'Standard air conditioning unit.'),
('room_09_1', 'ra_tv', 'Basic television with cable channels.'),
('room_09_1', 'ra_hairdryer', 'Compact hairdryer for guest use.')
ON CONFLICT (room_id, amenity_id) DO NOTHING;

-- Stanze DOPPIE → Base + Minibar
INSERT INTO room_amenities_link (room_id, amenity_id, custom_description) VALUES
('room_01_2', 'ra_ac', 'Air conditioning individually adjustable for double room comfort'),
('room_01_2', 'ra_tv', '32-inch flat-screen TV with international channels'),
('room_01_2', 'ra_hairdryer', 'Wall-mounted hairdryer suitable for daily use'),
('room_01_2', 'ra_minibar', 'Minibar stocked with soft drinks and snacks'),

('room_02_1', 'ra_ac', 'Silent air conditioning system ideal for couples'),
('room_02_1', 'ra_tv', 'Smart TV with streaming services enabled'),
('room_02_1', 'ra_hairdryer', 'Compact hairdryer with medium airflow'),
('room_02_1', 'ra_minibar', 'Minibar including water, juices and beer'),

('room_03_2', 'ra_ac', 'Climate control system with night mode'),
('room_03_2', 'ra_tv', 'LED TV positioned opposite the bed'),
('room_03_2', 'ra_hairdryer', 'Hairdryer available in the private bathroom'),
('room_03_2', 'ra_minibar', 'Minibar with complimentary bottled water'),

('room_05_2', 'ra_ac', 'Independent air conditioning with digital thermostat'),
('room_05_2', 'ra_tv', 'Cable TV with movie and sports channels'),
('room_05_2', 'ra_hairdryer', 'High-power hairdryer for long hair'),
('room_05_2', 'ra_minibar', 'Minibar refreshed daily'),

('room_06_1', 'ra_ac', 'Energy-efficient air conditioning unit'),
('room_06_1', 'ra_tv', 'Flat-screen TV mounted on the wall'),
('room_06_1', 'ra_hairdryer', 'Bathroom hairdryer with safety switch'),
('room_06_1', 'ra_minibar', 'Minibar with selection of local beverages'),

('room_07_2', 'ra_ac', 'Adjustable air conditioning for optimal temperature'),
('room_07_2', 'ra_tv', 'Smart TV with HDMI connectivity'),
('room_07_2', 'ra_hairdryer', 'Hairdryer with concentrator nozzle'),
('room_07_2', 'ra_minibar', 'Minibar including premium snacks'),

('room_08_1', 'ra_ac', 'Quiet air conditioning suitable for light sleepers'),
('room_08_1', 'ra_tv', 'TV with satellite channels'),
('room_08_1', 'ra_hairdryer', 'Compact hairdryer provided'),
('room_08_1', 'ra_minibar', 'Minibar with complimentary refreshments'),

('room_09_2', 'ra_ac', 'Air conditioning with eco mode'),
('room_09_2', 'ra_tv', 'Flat-screen TV with multilingual channels'),
('room_09_2', 'ra_hairdryer', 'Hairdryer available in ensuite bathroom'),
('room_09_2', 'ra_minibar', 'Minibar suitable for short stays')
ON CONFLICT (room_id, amenity_id) DO NOTHING;


-- Stanze SUITE → ALL amenities
INSERT INTO room_amenities_link (room_id, amenity_id, custom_description) VALUES
('room_01_3', 'ra_ac', 'Premium air conditioning with separate living area control'),
('room_01_3', 'ra_tv', '55-inch Smart TV in living area'),
('room_01_3', 'ra_hairdryer', 'Professional hairdryer with multiple heat settings'),
('room_01_3', 'ra_minibar', 'Fully stocked minibar with premium drinks'),
('room_01_3', 'ra_safe', 'Electronic safe suitable for laptops'),
('room_01_3', 'ra_balcony', 'Private balcony with panoramic city view'),

('room_02_2', 'ra_ac', 'Advanced climate control system for suite'),
('room_02_2', 'ra_tv', 'Large Smart TV with surround sound'),
('room_02_2', 'ra_hairdryer', 'High-end hairdryer with diffuser'),
('room_02_2', 'ra_minibar', 'Minibar with champagne selection'),
('room_02_2', 'ra_safe', 'Digital safe with personal code'),
('room_02_2', 'ra_balcony', 'Spacious balcony with outdoor seating'),

('room_04_1', 'ra_ac', 'Luxury air conditioning with zone regulation'),
('room_04_1', 'ra_tv', 'Smart TV available in both bedroom and lounge'),
('room_04_1', 'ra_hairdryer', 'Premium bathroom hairdryer'),
('room_04_1', 'ra_minibar', 'Minibar replenished daily with gourmet items'),
('room_04_1', 'ra_safe', 'Secure safe integrated into wardrobe'),
('room_04_1', 'ra_balcony', 'Balcony overlooking the garden'),

('room_06_2', 'ra_ac', 'Silent air conditioning system with smart sensors'),
('room_06_2', 'ra_tv', 'Ultra HD Smart TV with streaming platforms'),
('room_06_2', 'ra_hairdryer', 'Salon-grade hairdryer'),
('room_06_2', 'ra_minibar', 'Exclusive minibar with premium spirits'),
('room_06_2', 'ra_safe', 'Spacious electronic safe'),
('room_06_2', 'ra_balcony', 'Private balcony with lounge chairs'),

('room_07_3', 'ra_ac', 'High-performance air conditioning for large suite'),
('room_07_3', 'ra_tv', 'Dual Smart TVs in bedroom and living room'),
('room_07_3', 'ra_hairdryer', 'Professional hairdryer with ionic technology'),
('room_07_3', 'ra_minibar', 'Luxury minibar with curated selections'),
('room_07_3', 'ra_safe', 'In-room safe with biometric lock'),
('room_07_3', 'ra_balcony', 'Corner balcony with extended view'),

('room_10_1', 'ra_ac', 'Top-tier climate system with personalized presets'),
('room_10_1', 'ra_tv', 'Cinema-size Smart TV'),
('room_10_1', 'ra_hairdryer', 'Designer hairdryer with premium finish'),
('room_10_1', 'ra_minibar', 'Minibar featuring local artisan products'),
('room_10_1', 'ra_safe', 'Extra-large digital safe'),
('room_10_1', 'ra_balcony', 'Exclusive terrace with city skyline view')
ON CONFLICT (room_id, amenity_id) DO NOTHING;


-- ==========================================
-- MEDIA (property e qualche di seed)
-- ==========================================

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