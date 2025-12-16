// src/lib/api/search.ts
import { BaseApi } from './base';
import type { PropertyData, SearchCriteria } from '../types';

class SearchApi extends BaseApi {
    
    async searchProperties(criteria: SearchCriteria): Promise<PropertyData[]> {
        console.log("🔍 [SearchAPI] Searching with:", criteria);
        
        // MOCK DATA
        return [
            {
                id: 1,
                ownerId: 99,
                name: "Grand Hotel UML",
                address: "Via Architecture 101",
                description: "Perfettamente strutturato.",
                status: 'PUBLISHED',
                rooms: [{ type: 'SUITE', price: 200, capacity: 2 }],
                mainImage: "https://via.placeholder.com/800x600?text=UML+Hotel"
            },
            {
                id: 2,
                ownerId: 50,
                name: "Resort SvelteKit",
                address: "Frontend Beach",
                description: "Veloce e reattivo.",
                status: 'PUBLISHED',
                rooms: [{ type: 'DOUBLE', price: 120, capacity: 2 }],
                mainImage: "https://via.placeholder.com/800x600?text=Svelte+Resort"
            }
        ];
        // return this.request<PropertyData[]>(`/search?...`);
    }

    // Corrisponde a: +getPropertyById(id: int)
    async getPropertyById(id: number): Promise<PropertyData> {
        console.log(`🔍 [SearchAPI] Fetching details for ID: ${id}`);
        return {
            id: id,
            ownerId: 99,
            name: "Grand Hotel UML",
            address: "Via Architecture 101",
            description: "Dettaglio completo della property...",
            status: 'PUBLISHED',
            rooms: [],
            mainImage: "https://via.placeholder.com/800x600?text=Detail+View"
        };
    }
}

export const searchApi = new SearchApi();