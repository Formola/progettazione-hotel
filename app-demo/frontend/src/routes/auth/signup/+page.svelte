<script lang="ts">
    import { goto } from '$app/navigation';
    import { auth } from '$lib/auth.svelte';

    let email = $state("");
    let password = $state("");
    let isLoading = $state(false);
    let errorMessage = $state("");

    $effect(() => {
        if (auth.isAuthenticated) goto('/owner/dashboard');
    });

    async function handleSignup() {
        isLoading = true;
        errorMessage = "";
        try {
            // Simulated registration
            await new Promise(r => setTimeout(r, 1000));
            await goto('/auth/login?signup_success=true');
        } catch (err) {
            errorMessage = "Registration failed. Please try again.";
        } finally {
            isLoading = false;
        }
    }
</script>

<div class="auth-page">
    <div class="auth-card">
        <h2 class="auth-title">Create Owner Account</h2>
        
        {#if errorMessage}
            <div class="auth-error">{errorMessage}</div>
        {/if}

        <div class="auth-field">
            <label for="email">Email Address</label>
            <input 
                id="email"
                type="email" 
                bind:value={email} 
                placeholder="e.g. alex@provider.com" 
                class="auth-input"
            />
        </div>

        <div class="auth-field">
            <label for="password">Password</label>
            <input 
                id="password"
                type="password" 
                bind:value={password} 
                placeholder="Minimum 8 characters" 
                class="auth-input"
            />
        </div>

        <button 
            class="auth-button" 
            onclick={handleSignup}
            disabled={isLoading || !email || password.length < 8}
            class:is-loading={isLoading}
        >
            Join as Owner
        </button>
        
        <p class="auth-switch">
            Already have an account? 
            <a href="/auth/login">Log in here</a>
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

    .auth-error {
        background: rgba(245, 101, 101, 0.1);
        color: #feb2b2;
        padding: 0.75rem;
        border-radius: 8px;
        font-size: 0.85rem;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(245, 101, 101, 0.2);
    }
</style>