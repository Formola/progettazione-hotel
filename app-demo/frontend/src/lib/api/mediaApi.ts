import { apiClient } from './client';
import type { MediaInput, MediaData } from '../types';

class MediaApi {

    /**
     * Carica un file media collegandolo a una Property O a una Room.
     * Endpoint: POST /api/media/
     */
    async uploadMedia(data: MediaInput): Promise<MediaData> {
        const response = await apiClient.post<MediaData>('/api/media/', data);
        return response.data;
    }

    /**
     * Elimina un media per ID.
     * Endpoint: DELETE /api/media/{media_id}
     */
    async deleteMedia(mediaId: string): Promise<void> {
        await apiClient.delete<void>(`/api/media/${mediaId}`);
    }

    /**
     * Ottiene i dettagli di un media.
     * Endpoint: GET /api/media/{media_id}
     */
    async getMediaById(mediaId: string): Promise<MediaData> {
        const response = await apiClient.get<MediaData>(`/api/media/${mediaId}`);
        return response.data;
    }

    /**
     * Lista tutti i media di una proprietà specifica.
     * Endpoint: GET /api/media/property/{property_id}
     */
    async getMediaByProperty(propertyId: string): Promise<MediaData[]> {
        const response = await apiClient.get<MediaData[]>(`/api/media/property/${propertyId}`);
        return response.data;
    }

    /**
     * Lista tutti i media di una stanza specifica.
     * Endpoint: GET /api/media/room/{room_id}
     */
    async getMediaByRoom(roomId: string): Promise<MediaData[]> {
        const response = await apiClient.get<MediaData[]>(`/api/media/room/${roomId}`);
        return response.data;
    }

    // --- HELPER UTILITY ---

    /**
     * Converte un oggetto File (HTML input) in stringa Base64 pulita.
     * Rimuove l'intestazione "data:image/png;base64," per compatibilità con Python base64 decode.
     */
    fileToBase64(file: File): Promise<string> {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onload = () => {
                const result = reader.result as string;
                // Prende solo la parte dopo la virgola (i dati raw)
                const base64Raw = result.split(',')[1];
                resolve(base64Raw);
            };
            reader.onerror = error => reject(error);
        });
    }
}

export const mediaApi = new MediaApi();