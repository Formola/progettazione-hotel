// src/lib/api/auth.ts
import { BaseApi } from './base';
import type { UserData } from '../types';

class AuthApi extends BaseApi {
    
    // Corrisponde a: +login(email, password)
    async login(email: string, password: string): Promise<UserData> {
        console.log("🔐 [AuthAPI] Login attempt:", email);
        return {
            id: 1,
            email: email,
            name: "Mario Owner",
            role: 'OWNER',
            token: "fake-jwt-token"
        };
    }

    // Corrisponde a: +signup(userData, password)
    async signup(user: UserData, password: string): Promise<UserData> {
        console.log("🔐 [AuthAPI] Signup:", user);
        return user;
    }
}

export const authApi = new AuthApi();