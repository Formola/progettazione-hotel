import { 
    CognitoIdentityProviderClient, 
    InitiateAuthCommand, 
    SignUpCommand 
} from "@aws-sdk/client-cognito-identity-provider";
import type { IAuthProvider, AuthResponse } from './IAuthProvider';
import type { UserData } from '$lib/types';
import {config} from "$lib/config";

export class AWSCognitoAuthProvider implements IAuthProvider {
    private client: CognitoIdentityProviderClient;
    private clientId: string;

    constructor() {
        const isLocal = true; 
        const region = config.aws.region;
        const endpoint = config.aws.cognitoEndpoint;
        this.clientId = config.cognito.clientId;
        
        this.client = new CognitoIdentityProviderClient({
            region: "us-east-1",
            endpoint: isLocal ? "http://localhost:4566" : undefined,
        });
    }

    async login(email: string, password: string): Promise<AuthResponse> {
        const command = new InitiateAuthCommand({
            AuthFlow: "USER_PASSWORD_AUTH",
            ClientId: this.clientId,
            AuthParameters: {
                USERNAME: email,
                PASSWORD: password,
            },
        });

        const response = await this.client.send(command);
        return this.mapResponse(response, email);
    }

    // Logica di Refresh Token
    async refreshSession(refreshToken: string): Promise<AuthResponse> {
        console.log("🔄 [Cognito] Refreshing token...");
        const command = new InitiateAuthCommand({
            AuthFlow: "REFRESH_TOKEN_AUTH",
            ClientId: this.clientId,
            AuthParameters: {
                REFRESH_TOKEN: refreshToken,
            },
        });

        const response = await this.client.send(command);
        // Nota: Cognito nel refresh potrebbe NON ridarti un nuovo Refresh Token 
        // se quello vecchio è ancora valido, ma con la Rotation attiva di solito lo fa.
        return this.mapResponse(response);
    }

    async signup(user: UserData, password: string): Promise<AuthResponse> {
        const command = new SignUpCommand({
            ClientId: this.clientId,
            Username: user.email,
            Password: password,
            UserAttributes: [{ Name: "email", Value: user.email }]
        });
        await this.client.send(command);
        return { user, accessToken: "" }; // Signup non logga automaticamente di solito
    }

    async logout(): Promise<void> {
        return Promise.resolve();
    }

    // Helper per mappare la risposta di Cognito
    private mapResponse(response: any, emailFallback?: string): AuthResponse {
        const result = response.AuthenticationResult;
        if (!result) throw new Error("No auth result");

        // Decodifica basica (in prod si usano librerie JWT per leggere i claims)
        return {
            user: {
                id: 1, // Mock ID per ora
                email: emailFallback || "user@refreshed.com", 
                name: "Owner",
                role: 'OWNER'
            },
            accessToken: result.AccessToken,
            idToken: result.IdToken,
            refreshToken: result.RefreshToken // Importante: potrebbe essere null nel refresh
        };
    }
}