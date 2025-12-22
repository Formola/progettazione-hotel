// ==========================================
// CONDIVISI (Enums)
// ==========================================
export type PropertyStatus = 'DRAFT' | 'PUBLISHED' | 'INACTIVE';
export type RoomType = 'SINGLE' | 'DOUBLE' | 'SUITE';
export type MediaType = 'image/png' | 'video/mp4';
export type UserRole = 'GUEST' | 'OWNER' | 'ADMIN';

// ==========================================
// MEDIA (Immagini/Video)
// ==========================================

// INPUT: Payload per caricare un file (POST /api/media)
// Questo si usa sia per property/{id}/media che per rooms/{id}/media
export interface MediaUpload {
    fileName: string;
    fileType: MediaType;
    base64Data: string; 
    description?: string;
}

// OUTPUT: Oggetto visualizzato nel carosello
export interface MediaData {
    id: string;
    file_name?: string;
    file_type?: MediaType;
    storage_path: string; // URL diretto (come restituito da Python)
    description?: string;

}


// ==========================================
// AMENITIES (Servizi)
// ==========================================

// Interfaccia Base (non esportata, serve solo per non ripetere codice)
interface BaseAmenity {
    id: string;
    name: string;
    category: string;
    icon?: string;
}

// OUTPUT: Distinzione semantica
// (Utile per Type Safety: non puoi passare una RoomAmenity dove serve una PropertyAmenity)
// In futuro potrebbero avere campi diversi
export interface PropertyAmenity extends BaseAmenity {}
export interface RoomAmenity extends BaseAmenity {}

// ==========================================
// ROOMS
// ==========================================

// INPUT: Creazione/Modifica Stanza
export interface RoomInput {
    type: RoomType;
    description?: string;
    price: number;
    capacity: number;
    
    // L'Owner seleziona ID dalla lista "Room Amenities"
    amenity_ids: string[]; 
}

// OUTPUT: Visualizzazione Stanza
export interface RoomData extends Omit<RoomInput, 'amenity_ids'> {
    id: string;
    
    // Qui ricevi gli oggetti specifici per la stanza
    amenities: RoomAmenity[];  
    
    // Ogni stanza ha le sue foto specifiche
    media: MediaData[];        
}

// ==========================================
// PROPERTIES
// ==========================================

// INPUT: Creazione/Modifica Proprietà
export interface PropertyInput {
    name: string;
    address: string;
    city: string;
    country: string;
    description: string;
    
    // L'Owner seleziona ID dalla lista "Property Amenities"
    amenity_ids: string[]; 
}

// OUTPUT: Scheda completa per la UI
export interface PropertyData extends Omit<PropertyInput, 'amenity_ids'> {
    id: string;
    status: PropertyStatus; 
    owner: {
        id: string;
        name: string;
        email: string;
    };       
    
    // Liste popolate
    amenities: PropertyAmenity[]; // Solo servizi generali della casa
    rooms: RoomData[];            // Lista delle stanze
    media: MediaData[];           // Foto generali della casa (facciata, piscina)
}

// ==========================================
// USER & SEARCH
// ==========================================

export interface UserData {
    id: string;
    email: string;
    role: string;    
}

export interface SearchCriteria {
    location?: string;
    minPrice?: number;
    maxPrice?: number;
    checkIn?: Date;
    checkOut?: Date;
    guests?: number;
}