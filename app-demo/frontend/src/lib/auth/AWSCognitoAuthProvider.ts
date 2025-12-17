import { 
    AdminConfirmSignUpCommand,
    CognitoIdentityProviderClient, 
    InitiateAuthCommand, 
    AdminAddUserToGroupCommand,
    SignUpCommand 
} from "@aws-sdk/client-cognito-identity-provider";
import type { IAuthProvider, AuthResponse } from './IAuthProvider';
import type { UserData } from '$lib/types';
import {config} from "$lib/config";
import {parseJwt} from "$lib/utils/jtw";

export class AWSCognitoAuthProvider implements IAuthProvider {
    private client: CognitoIdentityProviderClient;
    private clientId: string;
    private userPoolId: string;

    constructor() {
        const region = config.aws.region;
        const endpoint = config.aws.cognitoEndpoint;
        this.clientId = config.cognito.clientId;
        this.userPoolId = config.cognito.userPoolId;
        
        this.client = new CognitoIdentityProviderClient({
            region: region,
            endpoint: endpoint, 
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

        return this.mapResponse(response);
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
        // REGISTRAZIONE NORMALE (Diventa UNCONFIRMED)
        const command = new SignUpCommand({
            ClientId: this.clientId,
            Username: user.email,
            Password: password,
            UserAttributes: [{ Name: "email", Value: user.email }]
        });
        await this.client.send(command);

        // ⚡ IL TRUCCO PER LOCALSTACK ⚡
        // Creiamo un client "al volo" con le credenziali di LocalStack
        // per agire da Amministratore direttamente dal browser.
        
        // NOTA, questo funziona SOLO su LocalStack perché usa credenziali fittizie.
        // Su AWS reale, questa chiamata fallirebbe per mancanza di permessi.

        // non è buona norma fare cosi, ci vorrebbe una lambda trigger pre-signed up!!
        // lo facciamo solo per semplicità in questo demo app.
        try {
            console.log("⚡ [LocalStack] Auto-confirming user from Frontend...");
            
            const adminClient = new CognitoIdentityProviderClient({
                region: config.aws.region,
                endpoint: config.aws.cognitoEndpoint,
                credentials: {
                    accessKeyId: "test",     // Credenziali di default LocalStack
                    secretAccessKey: "test"  // Credenziali di default LocalStack
                }
            });

            const confirmCommand = new AdminConfirmSignUpCommand({
                UserPoolId: this.userPoolId,
                Username: user.email
            });

            await adminClient.send(confirmCommand);
            console.log("✅ User confirmed via Frontend Admin Call!");

            const addGroupCommand = new AdminAddUserToGroupCommand({
                UserPoolId: this.userPoolId,
                Username: user.email,
                GroupName: "OWNERS" 
            });

            await adminClient.send(addGroupCommand);
            console.log("✅ User added to OWNERS group!");

        } catch (e) {
            console.error("⚠️ Failed to auto-confirm (Is this real AWS? This only works on LocalStack)", e);
        }

        // set user.role
        user.role = "OWNER";

        return { user, accessToken: "", idToken: "" }; // Non facciamo login automatico dopo il signup
    }

    async logout(): Promise<void> {
        return Promise.resolve();
    }
    // Helper per mappare la risposta di Cognito
    
    private mapResponse(response: any): AuthResponse {
        const result = response.AuthenticationResult;
        
        if (!result || !result.IdToken) {
            throw new Error("Cognito non ha restituito l'IdToken necessario.");
        }

        // Decodifichiamo il Token
        const claims = parseJwt(result.IdToken);

        if (!claims) {
            throw new Error("Impossibile leggere i dati utente dal token.");
        }

        // RECUPERO DINAMICO DEL RUOLO 🚀
        // Cognito restituisce i gruppi come array di stringhe nel campo 'cognito:groups'
        // Esempio: ["OWNERS", "TESTERS"] oppure undefined se nessun gruppo
        const groups: string[] = claims['cognito:groups'] || [];
        
        let role = 'USER'; // Default (se non ha gruppi speciali)

        if (groups.includes('OWNERS')) {
            role = 'OWNER';
        }

        console.log(`🔍 Ruolo rilevato dal Token: ${role} (Gruppi: ${groups})`);

        // Costruiamo l'utente
        const realUser: UserData = {
            id: claims.sub,
            email: claims.email,
            role: role
        };

        return {
            user: realUser,
            accessToken: result.AccessToken,
            idToken: result.IdToken,
            refreshToken: result.RefreshToken
        };
    }
}