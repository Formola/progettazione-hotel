<script lang="ts">
    import favicon from '$lib/assets/favicon.svg';
    import 'bulma/css/bulma.css';
    import { auth } from '$lib/auth.svelte';
    import { goto } from '$app/navigation';
    import { page } from '$app/state';
	import {onMount} from 'svelte';
	import {authApi} from '$lib/api/authApi';

    let { children } = $props();

    // Logica per capire dove si trova l'utente
    let isOwnerPage = $derived(page.url.pathname.startsWith('/owner'));
    let isAuthPage = $derived(page.url.pathname.startsWith('/auth'));
    let isSearchPage = $derived(page.url.pathname === '/search'); 

    async function handleOwnerClick() {
        if (auth.isAuthenticated) {
            await goto('/owner/dashboard');
        } else {
            await goto('/auth/signup');
        }
    }

    let isMenuOpen = $state(false);
    function toggleMenu() { isMenuOpen = !isMenuOpen; }

    const keys = {
        ACCESS_TOKEN: 'app_access_token',
        ID_TOKEN: 'app_id_token',
        REFRESH_TOKEN: 'app_refresh_token',
        USER: 'app_user_data'
    };

onMount(() => {
        const handleStorageChange = async (event: StorageEvent) => {
            // Caso 1: Clear All (event.key è null)
            // Caso 2: Rimozione di una chiave specifica tra quelle monitorate
            const isTargetKey = event.key === keys.ACCESS_TOKEN || 
                               event.key === keys.ID_TOKEN || 
                               event.key === keys.REFRESH_TOKEN || 
                               event.key === keys.USER;

            if (event.key === null || (isTargetKey && !event.newValue)) {
                console.warn("⚠️ Sessione rimossa dal browser. Logout in corso...");
                
                // Pulisci lo stato locale e reindirizza
                await authApi.logout();
                await goto('/auth/login');
            }
        };

        window.addEventListener('storage', handleStorageChange);

        return () => window.removeEventListener('storage', handleStorageChange);
    });
</script>

<svelte:head>
    <link rel="icon" href={favicon} />
    <title>HotelManager Demo</title>
</svelte:head>

<nav class="navbar is-white has-shadow" aria-label="main navigation">
    <div class="container">
        <div class="navbar-brand">
            <a class="navbar-item" href="/">
                <span class="is-size-3 mr-2">🏨</span>
                <span class="has-text-weight-bold has-text-grey-darker is-size-5">HotelManager</span>
            </a>

            <button
				type="button"
				class="navbar-burger"
				aria-label="menu"
				aria-expanded={isMenuOpen}
				class:is-active={isMenuOpen}
				onclick={toggleMenu}
				onkeydown={(e) => e.key === 'Enter' && toggleMenu()}
			>
				<span aria-hidden="true"></span>
				<span aria-hidden="true"></span>
				<span aria-hidden="true"></span>
				<span aria-hidden="true"></span>
			</button>
        </div>

        <div class="navbar-menu" class:is-active={isMenuOpen}>
            <div class="navbar-end">
                <a class="navbar-item" href="/">Home</a>

                {#if !auth.isAuthenticated}
                    <div class="navbar-item">
                        <button class="button is-dark is-outlined" onclick={handleOwnerClick}>
                            <strong>Start hosting your Property</strong>
                        </button>
                    </div>
                {:else}
                    {#if !isOwnerPage}
                        <a class="navbar-item has-text-primary has-text-weight-bold" href="/owner/dashboard">
                            Go to Dashboard
                        </a>
                    {/if}

                    {#if !isSearchPage}
                        <a class="navbar-item has-text-primary has-text-weight-bold" href="/search">
                            Search
                        </a>
                    {/if}

                    <!-- <div class="navbar-item">
                        <button class="button is-light is-small" onclick={() => { auth.logout(); goto('/'); }}>
                            Logout
                        </button>
                    </div> -->
                {/if}
            </div>
        </div>
    </div>
</nav>

<style>
    :global(html, body) {
        background-color: #ffffff; /* Forza il bianco ovunque */
        margin: 0;
        padding: 0;
        min-height: 100vh;
        display: flex;
        flex-direction: column;
    }
</style>

{@render children()}