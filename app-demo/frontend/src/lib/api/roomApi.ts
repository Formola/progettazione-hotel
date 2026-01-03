import { apiClient } from './client';
import type { RoomData, RoomInput, NewAmenityInput, RoomAmenity } from '../types';

class RoomApi {

    /**
     * Ottiene dettagli stanza.
     * GET /api/rooms/{room_id}
     */
    async getRoomDetails(roomId: string): Promise<RoomData> {
        const response = await apiClient.get<RoomData>(`/api/rooms/${roomId}`);
        return response.data;
    }

    /**
     * Aggiorna stanza (prezzo, tipo, desc...).
     * PUT /api/rooms/{room_id}
     */
    async updateRoom(roomId: string, data: RoomInput): Promise<RoomData> {
        const response = await apiClient.put<RoomData>(`/api/rooms/${roomId}`, data);
        return response.data;
    }

    /**
     * Elimina stanza.
     * DELETE /api/rooms/{room_id}
     */
    async deleteRoom(roomId: string): Promise<void> {
        await apiClient.delete<void>(`/api/rooms/${roomId}`);
    }

    /**
     * Aggiunge una nuova amenity (o linka esistente se gestito dal backend) alla stanza.
     * POST /api/rooms/{room_id}/amenities
     */
    async addAmenityToRoom(roomId: string, data: NewAmenityInput): Promise<RoomData> {
        const response = await apiClient.post<RoomData>(`/api/rooms/${roomId}/amenities`, data);
        return response.data;
    }

    /**
     * Rimuove amenity dalla stanza.
     * DELETE /api/rooms/{room_id}/amenities/{amenity_id}
     */
    async removeAmenityFromRoom(roomId: string, amenityId: string): Promise<RoomData> {
        const response = await apiClient.delete<RoomData>(`/api/rooms/${roomId}/amenities/${amenityId}`);
        return response.data;
    }

    // sono le global room amenities, quelle comuni non definite custom da user.
    async getAmenityCatalog(): Promise<RoomAmenity[]> {
        // Chiama GET /api/amenities/room
        const response = await apiClient.get<RoomAmenity[]>('/api/amenities/room');
        return response.data;
    }
}

export const roomApi = new RoomApi();