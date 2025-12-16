// src/lib/api/property.ts
import { BaseApi } from './base';
import type { PropertyData } from '../types';

class PropertyApi extends BaseApi {

    // Corrisponde a: +createProperty(data: PropertyData)
    async createProperty(data: PropertyData): Promise<PropertyData> {
        console.log("🏨 [PropertyAPI] Creating:", data);
        // Simuliamo la risposta del server con l'ID assegnato
        return { ...data, id: Math.floor(Math.random() * 1000) };
        // return this.request<PropertyData>('/properties', 'POST', data);
    }

    // Corrisponde a: +getOwnerProperties(ownerId: int)
    async getOwnerProperties(ownerId: number): Promise<PropertyData[]> {
        console.log(`🏨 [PropertyAPI] Fetching properties for owner ${ownerId}`);
        return []; // Mock vuoto per ora
    }

    // Corrisponde a: +publishProperty(id: int)
    async publishProperty(id: number): Promise<void> {
        console.log(`🏨 [PropertyAPI] Publishing property ${id}`);
        // return this.request<void>(`/properties/${id}/publish`, 'POST');
    }
}

export const propertyApi = new PropertyApi();