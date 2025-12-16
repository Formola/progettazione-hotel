<script lang="ts">
    import { goto } from '$app/navigation';
    import { auth } from '$lib/auth.svelte';
    import { page } from '$app/state';

    let email = $state("");
    let password = $state("");
    let isLoading = $state(false);
    let errorMessage = $state("");

    // Runa per gestire il messaggio di successo se arriviamo dal Signup
    let signupSuccess = $derived(page.url.searchParams.get('signup_success') === 'true');

    // Auth Guard: se già loggato, vai in Dashboard
    $effect(() => {
        console.log("Login Page Auth Guard:", auth.isAuthenticated);
        if (auth.isAuthenticated) goto('/owner/dashboard');
    });

    async function handleLogin() {
        if (!email || !password) {
            errorMessage = "Please enter both email and password.";
            return;
        }

        isLoading = true;
        errorMessage = "";
        try {
            // Simulazione login
            await new Promise(r => setTimeout(r, 800));
            auth.login({ email, role: 'OWNER' });
            await goto('/owner/dashboard');
        } catch (err) {
            errorMessage = "Invalid email or password.";
        } finally {
            isLoading = false;
        }
    }
</script>

<div class="auth-page">
    <div class="auth-card">
        <h2 class="auth-title">Welcome Back! Login to your account</h2>

        {#if signupSuccess}
            <div class="auth-status success">Account created! Please log in.</div>
        {/if}
        
        {#if errorMessage}
            <div class="auth-status error">{errorMessage}</div>
        {/if}

        <div class="auth-field">
            <label for="login-email">Email Address</label>
            <input 
                id="login-email" 
                type="email" 
                bind:value={email} 
                placeholder="Enter your email"
                class="custom-input" 
            />
        </div>

        <div class="auth-field">
            <label for="login-password">Password</label>
            <input 
                id="login-password" 
                type="password" 
                bind:value={password} 
                placeholder="Enter your password"
                class="custom-input" 
                onkeydown={(e) => e.key === 'Enter' && handleLogin()}
            />
        </div>

        <button 
            class="custom-button" 
            onclick={handleLogin} 
            disabled={isLoading}
        >
            {#if isLoading}
                Logging in...
            {:else}
                Log In
            {/if}
        </button>
        
        <p class="auth-switch">
            Don't have an account? 
            <a href="/auth/signup">Sign up now</a>
        </p>
    </div>
</div>

<style>
    /* Reset locale per evitare interferenze con Bulma */
    .auth-page {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 90vh;
        background-color: #ffffff; /* Sfondo chiaro come richiesto */
    }

    .auth-card {
        background: #121417; /* Sfondo scuro elegante */
        padding: 3.5rem 2.5rem;
        border-radius: 24px;
        width: 100%;
        max-width: 440px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.2);
        color: white;
    }

    .auth-title {
        font-size: 2.2rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 2.5rem;
        letter-spacing: -1px;
        color: white;
    }

    .auth-field {
        margin-bottom: 1.5rem;
    }

    .auth-field label {
        display: block;
        font-weight: 600;
        font-size: 0.85rem;
        margin-bottom: 0.6rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .custom-input {
        width: 100%;
        background: #1e2126;
        border: 2px solid #2d3139;
        color: white;
        padding: 1rem;
        border-radius: 12px;
        font-size: 1rem;
        transition: all 0.2s ease;
    }

    .custom-input:focus {
        outline: none;
        border-color: #38a169; /* Verde Cognito */
        background: #23272e;
    }

    .custom-button {
        width: 100%;
        background: #38a169;
        color: white;
        border: none;
        padding: 1.1rem;
        border-radius: 50px;
        font-size: 1.1rem;
        font-weight: 700;
        cursor: pointer;
        margin-top: 1.5rem;
        transition: all 0.2s ease;
    }

    .custom-button:hover:not(:disabled) {
        background: #2f855a;
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(56, 161, 105, 0.3);
    }

    .custom-button:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }

    /* Messaggi di Stato */
    .auth-status {
        padding: 0.8rem;
        border-radius: 10px;
        font-size: 0.9rem;
        margin-bottom: 1.5rem;
        text-align: center;
        border: 1px solid;
    }

    .auth-status.success {
        background: rgba(72, 187, 120, 0.15);
        color: #9ae6b4;
        border-color: rgba(72, 187, 120, 0.3);
    }

    .auth-status.error {
        background: rgba(245, 101, 101, 0.15);
        color: #feb2b2;
        border-color: rgba(245, 101, 101, 0.3);
    }

    .auth-switch {
        text-align: center;
        margin-top: 2rem;
        font-size: 0.95rem;
        color: #94a3b8;
    }

    .auth-switch a {
        color: #48bb78;
        font-weight: 700;
        text-decoration: none;
        margin-left: 0.4rem;
    }

    .auth-switch a:hover {
        text-decoration: underline;
    }
</style>