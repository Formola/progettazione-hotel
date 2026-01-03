// src/lib/api/auth.ts
import { AWSCognitoAuthProvider } from '../auth/AWSCognitoAuthProvider';
import { AuthService } from '../auth/AuthService';
import type { UserData } from '../types';

class AuthApi {
    private service: AuthService;

    constructor() {
        // Dependency Injection interna
        const provider = new AWSCognitoAuthProvider();
        this.service = new AuthService(provider);
    }


    async login(email: string, password: string): Promise<UserData> {
        console.log("[AuthAPI] Login...");
        return await this.service.login(email, password);
    }

    async signup(user: UserData, password: string): Promise<UserData> {
        console.log("[AuthAPI] Signup...");
        return await this.service.signup(user, password);
    }

    async logout(): Promise<void> {
        console.log("[AuthAPI] Logout...");
        return await this.service.logout();
    }

    getCurrentUser(): UserData | null {
        return this.service.getUser();
    }

    getAccessToken(): string | null {
        return this.service.getAccessToken();
    }

    async refreshSession(): Promise<string | null> {
        return await this.service.refreshTokenOrLogout();
    }

    isAuthenticated(): boolean {
        return !!this.getAccessToken();
    }
}

// Esportiamo un'istanza singola (Singleton) da usare in tutta l'app
export const authApi = new AuthApi();