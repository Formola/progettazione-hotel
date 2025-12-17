import type { UserData } from '$lib/types';

export interface AuthResponse {
    user: UserData;
    accessToken: string;
    idToken: string;      // Fondamentale: contiene i claim dell'utente
    refreshToken?: string; // Opzionale perché nel refresh a volte manca
}

export interface IAuthProvider {
    login(email: string, password: string): Promise<AuthResponse>;
    signup(user: UserData, password: string): Promise<AuthResponse>;
    refreshSession(refreshToken: string): Promise<AuthResponse>; 
    logout(): Promise<void>;
}

// metodo per il refresh del token, useremo approccio localstorage + refresh token dato che
// gestiamo i token manualmente nel frontend statico.
// L'approccio più sicuro per il nostro caso d'uso sarebbe usare HttpOnly cookies, ma
// non possiamo farlo con un frontend statico puro.
// Quindi, la soluzione migliore è usare localstorage + refresh token, cosi da minimizzare
// il rischio di XSS (non memorizziamo l'access token direttamente).