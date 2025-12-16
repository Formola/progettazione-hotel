import { browser } from '$app/environment';

class AuthState {
    // Inizializziamo leggendo da sessionStorage se siamo nel browser
    // Questo permette di "ricordare" l'utente anche se preme Invio sulla barra URL
    user = $state<any>(
        browser && sessionStorage.getItem('mock_auth_user') 
            ? JSON.parse(sessionStorage.getItem('mock_auth_user')!) 
            : null
    );
    
    isAuthenticated = $derived(this.user !== null);

    login(userData: any) {
        this.user = userData;
        if (browser) {
            // Salviamo temporaneamente per gestire il refresh della pagina
            sessionStorage.setItem('mock_auth_user', JSON.stringify(userData));
        }
        console.log("Auth State Updated:", this.user);
    }

    logout() {
        this.user = null;
        if (browser) {
            sessionStorage.removeItem('mock_auth_user');
        }
    }
}

export const auth = new AuthState();