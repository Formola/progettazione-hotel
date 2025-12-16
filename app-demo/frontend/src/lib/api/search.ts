// src/lib/api/search.ts
import { BaseApi } from './base';
import type { PropertyData, SearchCriteria } from '../types';

class SearchApi extends BaseApi {
    
    async searchProperties(criteria: SearchCriteria): Promise<PropertyData[]> {
        console.log("🔍 [SearchAPI] Searching with:", criteria);
        
        return [
            {
                id: 1,
                ownerId: 99,
                name: "Grand Hotel UML",
                address: "Via Architecture 101",
                description: "Perfettamente strutturato.",
                status: 'PUBLISHED',
                rooms: [{ type: 'SUITE', price: 200, capacity: 2 }],
                mainImage: "https://placehold.co/800x600/orange/white?text=UML+Hotel"
            },
            {
                id: 2,
                ownerId: 50,
                name: "Resort SvelteKit",
                address: "Frontend Beach",
                description: "Veloce e reattivo.",
                status: 'PUBLISHED',
                rooms: [{ type: 'DOUBLE', price: 120, capacity: 2 }],
                mainImage: "https://placehold.co/800x600/blue/white?text=Svelte+Resort"
            }
        ];
    }

    async getPropertyById(id: number): Promise<PropertyData> {
        console.log(`🔍 [SearchAPI] Fetching details for ID: ${id}`);
        return {
            id: id,
            ownerId: 99,
            name: "Grand Hotel UML",
            address: "Via Architecture 101",
            description: "Dettaglio completo della property...",
            status: 'PUBLISHED',
            rooms: [
                { type: 'SINGLE', price: 80, capacity: 1, amenities: ['Wifi', 'TV'] },
                { type: 'DOUBLE', price: 150, capacity: 2, amenities: ['Wifi', 'TV', 'Balcony'] }
            ],
            mainImage: "https://placehold.co/1920x600/orange/white?text=Detail+View",
            amenities: [{ name: "Wifi" }, { name: "Pool" }, { name: "Parking" }]
        };
    }
}

export const searchApi = new SearchApi();