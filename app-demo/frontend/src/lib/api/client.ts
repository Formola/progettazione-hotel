import axios from 'axios';
import { config } from '$lib/config';
import { authApi } from './auth';

// Crea l'istanza base
export const apiClient = axios.create({
    baseURL: config.api.baseUrl, // http://localhost:8000 or API Gateway Endpoint
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
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;
            try {
                const newToken = await authApi.refreshSession();
                if (newToken) {
                    originalRequest.headers['Authorization'] = `Bearer ${newToken}`;
                    return apiClient(originalRequest);
                }
            } catch (refreshError) {
                console.error("❌ Sessione scaduta o LocalStack resettato.");
                await authApi.logout();
                
                // Lanciamo un errore specifico che la UI può riconoscere
                return Promise.reject({
                    status: 401,
                    message: "Session expired. Please log in again.",
                    forceLogin: true
                });
            }
        }
        return Promise.reject(error);
    }
);