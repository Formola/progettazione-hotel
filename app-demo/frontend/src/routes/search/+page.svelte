<script lang="ts">
    import { page } from '$app/state';
    import { goto } from '$app/navigation'; // Serve per cambiare ricerca
    import { searchApi } from '$lib/api/search';
    import type { PropertyData } from '$lib/types';
    import PropertyCard from '$lib/components/PropertyCard.svelte';

    let properties = $state<PropertyData[]>([]);
    let isLoading = $state(true);
    let error = $state<string | null>(null);

    let locationQuery = $derived(page.url.searchParams.get('location') || "");

    // Input della Search Bar locale
    // Lo inizializziamo con il valore dell'URL
    let searchInput = $state(page.url.searchParams.get('location') || "");

    // Se l'URL cambia (es. tasto Indietro), aggiorniamo anche la barra di input
    $effect(() => {
        searchInput = locationQuery;
    });

    // Funzione per Nuova Ricerca
    async function handleNewSearch() {
        // Ricarica la pagina con il nuovo parametro.
        // Questo farà scattare l'effetto di fetch
        await goto(`/search?location=${encodeURIComponent(searchInput)}`);
    }

    // Fetch Dati
    $effect(() => {
        const fetchData = async () => {
            isLoading = true;
            error = null;
            try {
                properties = await searchApi.searchProperties({ 
                    location: locationQuery 
                });
            } catch (err) {
                console.error(err);
                error = "Failed to load properties.";
            } finally {
                isLoading = false;
            }
        };
        fetchData();
    });
</script>

<section class="section has-background-light" style="min-height: 100vh;">
    <div class="container">
        
    <div class="columns is-centered mb-6">
        <div class="column is-two-thirds-tablet is-half-desktop">
            <div class="search-wrapper">
                <div class="field has-addons">
                    <div class="control is-expanded has-icons-left">
                        <input 
                            class="input is-large custom-search-input" 
                            type="text" 
                            placeholder="Where to next?"
                            bind:value={searchInput}
                            onkeydown={(e) => e.key === 'Enter' && handleNewSearch()}
                        >
                        <span class="icon is-medium is-left has-text-primary">
                            <span class="is-size-4">🔍</span>
                        </span>
                    </div>
                    <div class="control">
                        <button 
                            class="button is-primary is-large px-6 custom-search-button"
                            onclick={handleNewSearch}
                        >
                            <strong>Search</strong>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>

        <div class="mb-5 ml-2">
            <h1 class="title is-4 has-text-grey-darker">
                {#if locationQuery}
                    Stays in <span class="has-text-primary">"{locationQuery}"</span>
                {:else}
                    All Properties
                {/if}
            </h1>
            <p class="subtitle is-6 has-text-grey">
                {#if !isLoading}
                    Found {properties.length} results
                {:else}
                    Searching...
                {/if}
            </p>
        </div>

        {#if isLoading}
            <div class="has-text-centered py-6">
                <button class="button is-loading is-white is-large is-outlined is-borderless">Loading</button>
            </div>
        {:else if error}
            <div class="notification is-danger is-light">
                {error}
            </div>
        {:else if properties.length === 0}
             <div class="notification is-warning is-light">
                No properties found in "{locationQuery}". Try searching for something else.
            </div>
        {:else}
            <div class="columns is-multiline">
                {#each properties as property (property.id)}
                    <div class="column is-one-third-desktop is-half-tablet">
                        <PropertyCard {property} />
                    </div>
                {/each}
            </div>
        {/if}

    </div>
</section>


<style>
    /* Wrapper per creare l'effetto card sollevata */
    .search-wrapper {
        background: white;
        border-radius: 50px;
        padding: 5px;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
        transition: box-shadow 0.3s ease, transform 0.3s ease;
    }

    .search-wrapper:focus-within {
        box-shadow: 0 12px 25px rgba(0, 0, 0, 0.12);
        transform: translateY(-2px);
    }

    /* Rimuoviamo il bordo standard di Bulma per un look più "flat" */
    .custom-search-input {
        border: none !important;
        box-shadow: none !important;
        border-radius: 50px 0 0 50px !important;
        padding-left: 3.5rem !important;
        background: transparent;
        color: black;
    }

    .custom-search-button {
        border-radius: 50px !important;
        margin: 2px; /* Piccolo distacco dal bordo del wrapper */
        height: calc(100% - 4px);
    }

    /* Effetto hover sull'icona se vuoi */
    .has-icons-left .icon {
        pointer-events: none;
        transition: color 0.3s ease;
    }
</style>