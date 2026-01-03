<script lang="ts">
    import { goto } from '$app/navigation';
    // IMPORTO LA TUA NUOVA API
    import { authApi } from '$lib/api/authApi';
    import type { UserData } from '$lib/types';

    let email = $state("");
    let password = $state("");
    let name = $state("");
    let isLoading = $state(false);
    let errorMessage = $state("");

    // Auth Guard
    $effect(() => {
        // Controlliamo se siamo già loggati
        if (authApi.isAuthenticated()) goto('/owner/dashboard');
    });

    async function handleSignup() {
        isLoading = true;
        errorMessage = "";
        
        // Creiamo l'oggetto utente
        const userData: UserData = {
            email: email,
            id: "", // Lo imposteremo dopo la registrazione
            role: "" // Lo imposteremo lato Cognito Gruppi
        };

        try {
            console.log("🚀 Calling real Cognito Signup...");
            
            await authApi.signup(userData, password);
            
            console.log("✅ Signup successful!");
            // Redirect al login con messaggio
            await goto('/auth/login?signup_success=true');

        } catch (err: any) {
            console.error("❌ Signup Error:", err);
            // Mostriamo l'errore reale che arriva da Cognito/LocalStack
            errorMessage = err.message || "Registration failed.";
        } finally {
            isLoading = false;
        }
    }

    // Funzione di validazione locale che rispecchia le regole Cognito
    function isPasswordValid(p: string) {
        const hasUpperCase = /[A-Z]/.test(p);
        const hasLowerCase = /[a-z]/.test(p);
        const hasNumbers = /\d/.test(p);
        const hasLength = p.length >= 8;
        return hasUpperCase && hasLowerCase && hasNumbers && hasLength;
    }

    // Stato derivato per disabilitare il bottone
    let canSubmit = $derived(
        !isLoading && 
        email.length > 0 && 
        isPasswordValid(password)
    );
</script>

<div class="auth-page">
    <div class="auth-card">
        <h2 class="auth-title">Create Owner Account</h2>
        
        {#if errorMessage}
            <div class="auth-error">
                {errorMessage}
            </div>
        {/if}

        <div class="auth-field">
            <label for="email">Email Address</label>
            <input 
                id="email"
                type="email" 
                bind:value={email} 
                placeholder="e.g. alex@provider.com" 
                class="auth-input block w-full border border-gray-300 rounded p-2"
            />
        </div>

        <div class="auth-field mt-4">
            <label for="password">Password</label>
            <input 
                id="password"
                type="password" 
                bind:value={password} 
                placeholder="Min 8 chars, 1 Upper, 1 Number" 
                class="auth-input block w-full border border-gray-300 rounded p-2"
                class:border-red-500={password.length > 0 && !isPasswordValid(password)}
            />
            {#if password.length > 0 && !isPasswordValid(password)}
                <p class="text-xs text-red-500 mt-1">
                    Must verify: 8 chars, 1 Uppercase, 1 Number.
                </p>
            {/if}
        </div>

        <button 
            class="auth-button mt-6 w-full bg-blue-600 text-white p-2 rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed" 
            onclick={handleSignup}
            disabled={!canSubmit} 
        >
            {isLoading ? 'Registering...' : 'Join as Owner'}
        </button>
        
        <p class="auth-switch mt-4 text-center text-sm">
            Already have an account? 
            <a href="/auth/login" class="text-blue-600 underline">Log in here</a>
        </p>
    </div>
</div>

<style>
    .auth-page {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 90vh;
        background-color: #ffffff;
    }

    .auth-card {
        background: #121417; /* Dark elegant theme from your request */
        padding: 3.5rem 2.5rem;
        border-radius: 24px;
        width: 100%;
        max-width: 440px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        color: white;
    }

    .auth-error {
        background: rgba(245, 101, 101, 0.15);
        color: #feb2b2;
        border-color: rgba(245, 101, 101, 0.3);
    }

    .auth-title {
        font-size: 2rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 2.5rem;
        letter-spacing: -0.5px;
    }

    .auth-field {
        margin-bottom: 1.5rem;
    }

    .auth-field label {
        display: block;
        font-weight: 600;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
        color: #94a3b8;
    }

    .auth-input {
        width: 100%;
        background: #1e2126;
        border: 1px solid #2d3139;
        color: white;
        padding: 1rem;
        border-radius: 12px;
        font-size: 1rem;
        transition: all 0.2s;
    }

    .auth-input:focus {
        outline: none;
        border-color: #38a169;
        box-shadow: 0 0 0 3px rgba(56, 161, 105, 0.2);
    }

    .auth-button {
        width: 100%;
        background: #38a169;
        color: white;
        border: none;
        padding: 1.1rem;
        border-radius: 50px;
        font-size: 1.1rem;
        font-weight: 700;
        cursor: pointer;
        margin-top: 1rem;
        transition: transform 0.2s, background 0.2s;
    }

    .auth-button:hover:not(:disabled) {
        background: #2f855a;
        transform: translateY(-2px);
    }

    .auth-button:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    .auth-switch {
        text-align: center;
        margin-top: 2rem;
        font-size: 0.9rem;
        color: #94a3b8;
    }

    .auth-switch a {
        color: #48bb78;
        font-weight: 700;
        text-decoration: none;
        margin-left: 0.3rem;
    }


</style>