import axios from 'axios';
import { config } from '$lib/config';
import { authApi } from './auth';

// Crea l'istanza base
export const apiClient = axios.create({
    baseURL: config.api.baseUrl, // http://localhost:8000
    headers: {
        'Content-Type': 'application/json'
    }
});

// REQUEST INTERCEPTOR (Inietta il Token)
// Prima di ogni chiamata, controlla se abbiamo un token e lo appiccica
apiClient.interceptors.request.use(
    (config) => {
        const token = authApi.getAccessToken();
        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// RESPONSE INTERCEPTOR (Gestisce il 401 e il Refresh)
apiClient.interceptors.response.use(
    (response) => response, // Se va tutto bene, ritorna la risposta
    async (error) => {
        const originalRequest = error.config;

        // Se l'errore è 401 E non abbiamo già provato a fare refresh (evita loop infiniti)
        if (error.response?.status === 401 && !originalRequest._retry) {
            console.warn("🔄 [Axios] 401 rilevato. Refreshing token...");
            originalRequest._retry = true; // Segna che ci stiamo provando

            try {
                // Tenta il refresh
                const newToken = await authApi.refreshSession();

                if (newToken) {
                    console.log("✅ [Axios] Refresh OK. Riprovo richiesta.");
                    // Aggiorna l'header della richiesta fallita con il nuovo token
                    originalRequest.headers['Authorization'] = `Bearer ${newToken}`;
                    
                    // Riprova la chiamata originale con Axios
                    return apiClient(originalRequest);
                }
            } catch (refreshError) {
                console.error("❌ [Axios] Refresh fallito. Logout.");
                authApi.logout(); // Opzionale: forza logout
                window.location.href = '/auth/login'; // Opzionale: redirect brutale
            }
        }

        // Se non era un 401 o il refresh è fallito, lancia l'errore al chiamante
        return Promise.reject(error);
    }
);