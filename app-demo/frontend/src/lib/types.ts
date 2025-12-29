// ==========================================
// CONDIVISI (Enums)
// ==========================================
export type PropertyStatus = 'DRAFT' | 'PUBLISHED' | 'INACTIVE';
export type RoomType = 'SINGLE' | 'DOUBLE' | 'SUITE';
export type MediaType = 'image/png' | 'image/jpeg' | 'video/mp4'; 
export type UserRole = 'GUEST' | 'OWNER' | 'ADMIN';

// ==========================================
// MEDIA (Immagini/Video)
// ==========================================

// INPUT: Payload per caricare un file
export interface MediaUpload {
    fileName: string;     
    fileType: MediaType;
    base64Data: string; 
    description?: string;
}

// OUTPUT: Oggetto visualizzato nel carosello (Match JSON Backend)
export interface MediaData {
    id: string;
    file_name: string;    // Nel JSON è snake_case
    file_type: string;    // Nel JSON è snake_case ("image/png")
    storage_path: string; 
    description?: string | null; // Il backend può mandare null
}

// ==========================================
// AMENITIES (Servizi)
// ==========================================

// Interfaccia Base
interface BaseAmenity {
    id: string;
    name: string;
    category: string;
    icon?: string; // Se lo gestisci nel frontend mapping
    
    description?: string | null;       // Descrizione generica (dal catalogo)
    custom_description?: string | null;// Descrizione specifica (es. "Fibra 1GB")
}

// OUTPUT: Distinzione semantica
export interface PropertyAmenity extends BaseAmenity {}
export interface RoomAmenity extends BaseAmenity {}

export interface NewAmenityInput {
    name: string;
    category: string;
    description?: string;
}

export interface AmenityLinkInput {
    id: string;
    custom_description?: string;
}

// ==========================================
// ROOMS
// ==========================================

// INPUT: Creazione/Modifica Stanza
export interface RoomInput {
    type: RoomType;
    description?: string;
    price: number;
    capacity: number;
    
    // Collegamento ID esistenti
    amenities: AmenityLinkInput[];    
    // Se il backend supporta new_amenities nel payload principale
    new_amenities?: NewAmenityInput[]; 
    
    media_ids?: string[];
}

// OUTPUT: Visualizzazione Stanza
export interface RoomData {
    id: string;
    type: RoomType;    
    description?: string | null;
    price: number;
    capacity: number;
    
    amenities: RoomAmenity[];  
    
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
    
    amenities: AmenityLinkInput[];
    media_ids?: string[];
}

// OUTPUT: Scheda completa per la UI
export interface PropertyData {
    id: string;
    name: string;
    address: string;
    city: string;
    country: string;
    description?: string | null;
    status: PropertyStatus; 
    
    owner: {
        id: string;
        name: string;
        email: string;
    };       
    
    amenities: PropertyAmenity[]; 
    rooms: RoomData[];            
    media: MediaData[];           
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