<script lang="ts">
    import { onDestroy } from 'svelte';
    import { goto } from '$app/navigation';
    import type { PropertyData } from '$lib/types'; 
    import { selectedProperty } from '$lib/stores/selection';

    // Usiamo lo State di Svelte 5
    let property = $state<PropertyData | null>(null);

    // Recupero dati dallo store
    const unsubscribe = selectedProperty.subscribe(value => {
        property = value;
    });

    // Debug: ispeziona l'oggetto PropertyData completo
    $inspect(property);

    onDestroy(unsubscribe);

    let currentImageIndex = $state(0);
    
    // Gestione Immagini: Adattata al tipo 'Media'
    let displayImages = $derived.by(() => {
        if (property?.media && property.media.length > 0) {
            return property.media.map(
                m => m.storage_path || `https://placehold.co/1200x500?text=${encodeURIComponent(m.description || 'View')}`
            );
        }
        return [
            "https://placehold.co/1200x500/ffffff/000000?text=Main+Property+Photo",
            "https://placehold.co/1200x500/ffffff/000000?text=Internal+Room+View"
        ];
    });


    function nextImage() { currentImageIndex = (currentImageIndex + 1) % displayImages.length; }
    function prevImage() { currentImageIndex = (currentImageIndex - 1 + displayImages.length) % displayImages.length; }
</script>

<nav class="has-background-white border-bottom py-3 is-sticky">
    <div class="container is-max-desktop px-3">
        <button class="button is-ghost has-text-black p-0" onclick={() => history.back()}>
            <span class="icon">←</span> <span class="has-text-weight-bold">Back to results</span>
        </button>
    </div>
</nav>

{#if !property}
    <main class="section has-background-white-bis" style="min-height: 100vh;">
        <div class="container is-max-desktop has-text-centered">
            <div class="box shadow-soft">
                <h2 class="title is-4">Property not found in memory.</h2>
                <button class="button is-primary is-rounded" onclick={() => goto('/search')}>Back to Search</button>
            </div>
        </div>
    </main>
{:else}
    <main class="section has-background-white-bis" style="min-height: 100vh;">
        <div class="container is-max-desktop">
            
            <div class="mb-5">
                <h1 class="title is-2 has-text-black has-text-weight-bold mb-2">{property.name}</h1>
                <p class="subtitle is-5 has-text-grey-darker">
                    <span class="icon">📍</span> {property.address}, {property.city} ({property.country})
                </p>
                {#if property.status === 'DRAFT'}
                    <span class="tag is-warning">Draft</span>
                {/if}
            </div>

            <div class="box p-0 is-overflow-hidden shadow-soft mb-6 carousel-container">
                <img src={displayImages[currentImageIndex]} 
                     class="carousel-img" 
                     alt={property.name} />
                
                {#if displayImages.length > 1}
                    <button class="carousel-btn prev" onclick={prevImage}>❮</button>
                    <button class="carousel-btn next" onclick={nextImage}>❯</button>
                    
                    <div class="image-counter">
                        <span class="tag is-dark">{currentImageIndex + 1} / {displayImages.length}</span>
                    </div>
                {/if}
            </div>

            <div class="columns is-variable is-8">
                <div class="column is-8">
                    
                    <section class="box p-5 shadow-soft mb-6">
                        <h3 class="title is-4 has-text-black mb-4">About this place</h3>
                        <p class="is-size-5 has-text-grey-darker" style="line-height: 1.7;">
                            {property.description || `Welcome to ${property.name}.`}
                        </p>
                    </section>

                    {#if property.amenities && property.amenities.length > 0}
                    <section class="box p-5 shadow-soft mb-6">
                        <h3 class="title is-4 has-text-black mb-5">What this place offers</h3>
                        <div class="columns is-multiline is-mobile">
                            {#each property.amenities as amenity}
                                <div class="column is-6-tablet is-12-mobile mb-2">
                                    <div class="is-flex is-align-items-center">
                                        <span class="icon has-text-success mr-3">
                                            ✅
                                        </span>
                                        <div>
                                            <p class="has-text-weight-bold has-text-black mb-0">
                                                {amenity.name}
                                            </p>
                                            <p class="is-size-7 has-text-grey">
                                                {amenity.category}
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            {/each}
                        </div>
                    </section>
                    {/if}

                    <section>
                        <h3 class="title is-4 has-text-black mb-5">Available Rooms</h3>
                        {#if property.rooms && property.rooms.length > 0}
                            {#each property.rooms as room}
                                <div class="box p-5 shadow-soft mb-4">
                                    <div class="level is-mobile mb-3">
                                        <div class="level-left">
                                            <div>
                                                <h4 class="title is-5 has-text-black mb-1">
                                                    {room.type} </h4>
                                                <p class="is-size-6 has-text-grey-darker">Max {room.capacity} guests</p>
                                            </div>
                                        </div>
                                        <div class="level-right has-text-right">
                                            <div>
                                                <p class="title is-4 has-text-black mb-0">€{room.price}</p>
                                                <p class="is-size-7 has-text-grey">per night</p>
                                            </div>
                                        </div>
                                    </div>

                                    {#if room.description}
                                        <p class="mb-4 has-text-grey-dark">{room.description}</p>
                                    {/if}

                                    {#if room.amenities && room.amenities.length > 0}
                                        <div class="tags mb-5">
                                            {#each room.amenities as amenity}
                                                <span class="tag is-dark is-rounded border-grey">
                                                    {amenity.name}
                                                </span>
                                            {/each}
                                        </div>
                                    {/if}

                                    <button class="button is-primary is-fullwidth is-rounded has-text-weight-bold">
                                        Book Now
                                    </button>
                                </div>
                            {/each}
                        {:else}
                            <p class="has-text-grey">No rooms listed yet.</p>
                        {/if}
                    </section>
                </div>

                <div class="column is-4">
                    <div class="sticky-sidebar">
                        <div class="box p-5 shadow-soft">
                            <p class="heading has-text-grey-darker has-text-weight-bold mb-4">Property Manager</p>
                            <div class="is-flex is-align-items-center mb-5">
                            <div class="owner-avatar mr-3">
                                {property.owner?.name ? property.owner.name.charAt(0).toUpperCase() : '?'}
                            </div>
                            <div style="overflow: hidden;">
                                <p class="has-text-weight-bold has-text-black is-size-7" style="white-space: nowrap; text-overflow: ellipsis; overflow: hidden;">
                                    {property.owner?.name}
                                </p>
                                <p class="is-size-7 has-text-grey">{property.owner?.email}</p>
                            </div>

                            </div>
                            <button class="button is-dark is-fullwidth is-rounded has-text-weight-bold">
                                Contact Host
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </main>
{/if}

<style>
    .shadow-soft {
        box-shadow: 0 8px 20px rgba(0,0,0,0.05) !important;
        border: 1px solid #f0f0f0;
        background: white;
    }
    .is-overflow-hidden { overflow: hidden; border-radius: 12px; }
    .border-bottom { border-bottom: 1px solid #f0f0f0; }
    .is-sticky { position: sticky; top: 0; z-index: 10; }
    .sticky-sidebar { position: sticky; top: 80px; }
    
    .owner-avatar {
        width: 48px; height: 48px;
        min-width: 48px;
        background: #00d1b2; color: white;
        border-radius: 50%; display: flex;
        align-items: center; justify-content: center;
        font-weight: bold; font-size: 1.2rem;
    }
    
.carousel-container {
    position: relative;
    width: 100%;
    border-radius: 12px;
}
.carousel-container img {
    width: 100%;
    height: auto; 
    object-fit: contain; 
    border-radius: 12px;
    display: block; 
}

    .carousel-img { width: 100%; height: 100%; object-fit: cover; }
    .image-counter { position: absolute; bottom: 15px; right: 15px; }
    
    .carousel-btn {
        position: absolute; top: 50%; transform: translateY(-50%);
        background: rgba(255, 255, 255, 0.85); border: none;
        width: 45px; height: 45px; border-radius: 50%;
        cursor: pointer; font-size: 1.2rem; display: flex;
        align-items: center; justify-content: center;
        opacity: 0; transition: opacity 0.3s ease;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    .carousel-container:hover .carousel-btn { opacity: 1; }
    .carousel-btn:hover { background: white; }
    .prev { left: 20px; }
    .next { right: 20px; }

    .border-grey { border: 1px solid #dbdbdb; }

    :global(.title) { color: #000000 !important; }
    :global(.subtitle) { color: #4a4a4a !important; }
</style>