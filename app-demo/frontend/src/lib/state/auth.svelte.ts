import { authApi } from '$lib/api/authApi';
import type { UserData } from '$lib/types';

class AuthState {
    // STATO REATTIVO
    // All'avvio, chiediamo all'API se c'è già un utente salvato (nel localStorage)
    // Così al refresh della pagina l'utente resta loggato visivamente
    user = $state<UserData | null>(authApi.getCurrentUser());
    
    // STATO DERIVATO
    // Calcolato automaticamente: true se user esiste
    isAuthenticated = $derived(this.user !== null);
    
    // Helper per controllare i ruoli (opzionale ma utile)
    isOwner = $derived(this.user?.role === 'OWNER');

    // AZIONI
    async login(email: string, password: string) {
        try {
            // Chiamiamo l'API reale (Cognito)
            const userData = await authApi.login(email, password);
            
            // AGGIORNIAMO LO STATO REATTIVO
            // Svelte rileverà questo cambio e aggiornerà la UI
            this.user = userData;

            console.log("Login state updated", userData);
            
            return userData;
        } catch (err) {
            console.error("Login state update failed", err);
            throw err;
        }
    }

    async signup(user: UserData, password: string) {
        // Il signup di solito non logga subito, ma se lo facesse:
        const newUser = await authApi.signup(user, password);
        // Non settiamo this.user qui perché di solito serve conferma email o login esplicito
        return newUser;
    }

    async logout() {
        // Pulizia Backend/LocalStorage
        await authApi.logout();
        
        // Pulizia UI
        this.user = null;
    }

    syncState() {
        this.user = authApi.getCurrentUser();
    }
}

// Esportiamo l'istanza globale
export const auth = new AuthState();