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
    base64Data?: string; 
    url?: string;
}

export interface AmenityData {
    id?: number;
    name: string;
    description?: string;
    isIncluded?: boolean; 
}

export interface RoomData {
    id?: number;
    type: RoomType;
    price: number;
    capacity: number;
    amenities?: string[]; 
}

export interface PropertyData {
    id?: number; 
    ownerId: number;
    name: string;
    address: string;
    description: string;
    status: PropertyStatus;
    rooms: RoomData[];
    mainImage?: string; 
    amenities?: AmenityData[];
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
}