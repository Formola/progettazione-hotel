import type { AuthResponse, IAuthProvider } from './IAuthProvider';
import type { UserData } from '$lib/types';

export class AuthService {
    private provider: IAuthProvider;
    
    // Chiavi per il LocalStorage
    private keys = {
        ACCESS_TOKEN: 'app_access_token',
        ID_TOKEN: 'app_id_token',
        REFRESH_TOKEN: 'app_refresh_token',
        USER: 'app_user_data'
    };

    constructor(provider: IAuthProvider) {
        this.provider = provider;
    }

    // Login e Salvataggio
    async login(email: string, password: string): Promise<UserData> {
        const response = await this.provider.login(email, password);
        console.log("Login response:", response);
        this.saveSession(response);
        return response.user;
    }

    // Signup
    async signup(user: UserData, password: string): Promise<UserData> {
        // Deleghiamo al provider (Cognito)
        const response = await this.provider.signup(user, password);
        console.log(response.user);
        return response.user;
    }

    // Lettura Access Token
    getAccessToken(): string | null {
        if (typeof localStorage === 'undefined') return null;
        return localStorage.getItem(this.keys.ACCESS_TOKEN);
    }

    getUser(): UserData | null {
        if (typeof localStorage === 'undefined') return null;
        const u = localStorage.getItem(this.keys.USER);
        return u ? JSON.parse(u) : null;
    }

    // Refresh Logic
    // Questo metodo verrà chiamato dal Timer o Interceptor
    async refreshTokenOrLogout(): Promise<string | null> {
        if (typeof localStorage === 'undefined') return null;
        
        const refreshToken = localStorage.getItem(this.keys.REFRESH_TOKEN);
        if (!refreshToken) {
            await this.logout();
            return null;
        }

        try {
            // Chiede a Cognito i nuovi token
            const response = await this.provider.refreshSession(refreshToken);
            
            // Aggiorna il LocalStorage con i nuovi token (Rotation)
            // Se Cognito non manda un nuovo refresh token, teniamo quello vecchio
            if (!response.refreshToken) {
                response.refreshToken = refreshToken; 
            }
            
            this.saveSession(response);
            console.log("Sessione aggiornata con successo");
            return response.accessToken;

        } catch (error) {
            console.error("Refresh fallito (token scaduto o revocato), logout forzato.");
            await this.logout();
            return null;
        }
    }

    // Logout
    async logout(): Promise<void> {
        await this.provider.logout();
        if (typeof localStorage !== 'undefined') {
            // Rimuove TUTTO dal localStorage
            Object.values(this.keys).forEach(key => localStorage.removeItem(key));
        }
    }

    // Helper privato per salvare tutto in un colpo solo
    private saveSession(response: AuthResponse) {

        if (typeof localStorage === 'undefined') return;

        // Salviamo i token grezzi (servono per le chiamate API)
        if (response.accessToken) localStorage.setItem(this.keys.ACCESS_TOKEN, response.accessToken);
        if (response.idToken) localStorage.setItem(this.keys.ID_TOKEN, response.idToken);
        if (response.refreshToken) localStorage.setItem(this.keys.REFRESH_TOKEN, response.refreshToken);
        
        if (response.user) localStorage.setItem(this.keys.USER, JSON.stringify(response.user));
    }
}