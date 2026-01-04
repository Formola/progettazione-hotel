import type { PropertyAmenity, PropertyData, PropertyInput, RoomData, RoomInput, SearchCriteria } from '../types';
import {apiClient} from './client';

class PropertyApi {
    
    async createProperty(data: PropertyInput): Promise<PropertyData> {
        const response = await apiClient.post<PropertyData>('/api/properties/', data);
        return response.data;
    }

    async getMyProperties(): Promise<PropertyData[]> {
        const response = await apiClient.get<PropertyData[]>('/api/properties/mine');
        return response.data;
    }

    async getPropertyById(id: string): Promise<PropertyData> {
        const response = await apiClient.get<PropertyData>(`/api/properties/${id}`);
        return response.data;
    }

    async updateProperty(id: string, data: PropertyInput): Promise<PropertyData> {
        const response = await apiClient.put<PropertyData>(`/api/properties/${id}`, data);
        return response.data;
    }

    async deleteProperty(id: string): Promise<void> {
        await apiClient.delete<void>(`/api/properties/${id}`);
    }

    async publishProperty(id: string): Promise<PropertyData> {
        const response = await apiClient.post<PropertyData>(`/api/properties/${id}/publish`);
        return response.data;
    }

    async unpublishProperty(id: string): Promise<PropertyData> {
        const response = await apiClient.post<PropertyData>(`/api/properties/${id}/unpublish`);
        return response.data;
    }

    async archiveProperty(id: string): Promise<PropertyData> {
        const response = await apiClient.post<PropertyData>(`/api/properties/${id}/archive`);
        return response.data;
    }

    async getRoomsForProperty(propertyId: string): Promise<RoomData[]> {
        const response = await apiClient.get<RoomData[]>(`/api/properties/${propertyId}/rooms`);
        return response.data;
    }

    async addRoomToProperty(propertyId: string, data: RoomInput): Promise<RoomData> {
        const response = await apiClient.post<RoomData>(`/api/properties/${propertyId}/rooms`, data);
        return response.data;
    }

    async getAmenityCatalog(): Promise<PropertyAmenity[]> {
        // Chiama GET /api/amenities/property
        const response = await apiClient.get<PropertyAmenity[]>('/api/amenities/property');
        return response.data;
    }
}

export const propertyApi = new PropertyApi();