// ==========================================
// FRONTEND DTOs
// ==========================================

export type PropertyStatus = 'DRAFT' | 'PUBLISHED' | 'INACTIVE';
export type RoomType = 'SINGLE' | 'DOUBLE' | 'SUITE';
export type MediaType = 'IMAGE' | 'VIDEO';
export type UserRole = 'GUEST' | 'OWNER' | 'ADMIN';


export interface MediaData {
    id?: number; 
    fileName: string;
    fileType: MediaType;
    url?: string;
}

export interface IAmenity {
    getName(): string;
    getCategory(): string;
}

export interface PropertyAmenityData extends IAmenity {
    name: string;
    category: string; // Es. "General", "Kitchen"
}

export interface RoomAmenityData extends IAmenity {
    name: string;
    category: string; // Es. "Bathroom", "Entertainment"
}


export interface RoomData {
    id: string;
    type: string;
    description: string | null;
    price: number;
    capacity: number;
    amenities: RoomAmenityData[];
    media: MediaData[];
}

export interface PropertyData {
    id: string;
    name: string;
    address: string;
    city: string;
    country: string;
    description: string | null;
    status: string;
    owner_id: string;
    rooms: RoomData[];
    amenities: PropertyAmenityData[];
    media: MediaData[];
}


export interface UserData {
    id?: number;
    name: string;
    email: string;
    password?: string;
    token?: string;
    role: UserRole;
}

export interface SearchCriteria {
    location?: string;
    minPrice?: number;
    maxPrice?: number;
    checkIn?: Date;
    checkOut?: Date;
    guests?: number;
    
}