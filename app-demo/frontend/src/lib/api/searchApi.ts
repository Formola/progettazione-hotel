// src/lib/api/search.ts
import type { PropertyData, SearchCriteria } from '../types';
import {apiClient} from './client';

class SearchApi {
    async searchProperties(criteria: SearchCriteria): Promise<PropertyData[]> {
        const query = criteria.location ? `?location=${encodeURIComponent(criteria.location)}` : '';
        // Usiamo axios (apiClient)
        const response = await apiClient.get<PropertyData[]>(`/api/search/${query}`);
        return response.data;
    }

    async getPropertyById(id: string): Promise<PropertyData> {
        const response = await apiClient.get<PropertyData>(`/api/properties/${id}`);
        return response.data;
    }
}

export const searchApi = new SearchApi();