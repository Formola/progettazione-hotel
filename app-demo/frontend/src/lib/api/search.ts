// src/lib/api/search.ts
import { BaseApi } from './base';
import type { PropertyData, SearchCriteria } from '../types';

class SearchApi extends BaseApi {
    async searchProperties(criteria: SearchCriteria): Promise<PropertyData[]> {
        // Costruiamo la query string per FastAPI
        const query = criteria.location ? `?location=${encodeURIComponent(criteria.location)}` : '';
        return this.request<PropertyData[]>(`/api/search/${query}`);
    }

    async getPropertyById(id: string): Promise<PropertyData> {
        // Nota: Qui servirà un endpoint backend /api/properties/{id} 
        return this.request<PropertyData>(`/api/properties/${id}`);
    }
}

export const searchApi = new SearchApi();