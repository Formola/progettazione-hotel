// src/lib/config.ts
import { env } from '$env/dynamic/public'; // importa variabili d'ambiente a runtime

export const config = {
    aws: {
        region: env.PUBLIC_AWS_REGION || 'us-east-1',
        cognitoEndpoint: env.PUBLIC_COGNITO_ENDPOINT || 'http://localhost:4566',
    },
    cognito: {
        userPoolId: env.PUBLIC_COGNITO_USER_POOL_ID,
        clientId: env.PUBLIC_COGNITO_CLIENT_ID,
        issuerUrl: env.PUBLIC_COGNITO_ISSUER_URL
    },
    api: {
        baseUrl: env.PUBLIC_API_GATEWAY_ENDPOINT
        // altri endpoint per lambda ecc possono essere aggiunti qui
    }
};

console.log("⚙️ App Config Loaded:", config);