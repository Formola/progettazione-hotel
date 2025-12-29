<script lang="ts">
    import { onDestroy } from 'svelte';
    import { goto } from '$app/navigation';
    import type { PropertyData } from '$lib/types';
    import { selectedProperty } from '$lib/stores/selection';
    import { getAmenityIcon } from '$lib/utils/icons';

    let property = $state<PropertyData | null>(null);

    const unsubscribe = selectedProperty.subscribe((value) => {
        property = value;
    });

    onDestroy(unsubscribe);

    let currentImageIndex = $state(0);
    let carouselWidth = $state(0);
    let carouselHeight = $state(0);

    let displayImages = $derived.by(() => {
        if (property?.media && property.media.length > 0) {
            return property.media.map(
                (m) =>
                    m.storage_path ||
                    `https://placehold.co/1200x500?text=${encodeURIComponent(m.description || 'View')}`
            );
        }
        return [
            'https://placehold.co/1200x500/ffffff/000000?text=Main+Property+Photo',
            'https://placehold.co/1200x500/ffffff/000000?text=Internal+Room+View'
        ];
    });

    function nextImage() {
        currentImageIndex = (currentImageIndex + 1) % displayImages.length;
    }

    function prevImage() {
        currentImageIndex = (currentImageIndex - 1 + displayImages.length) % displayImages.length;
    }

    function onImageLoad(e: Event) {
        const img = e.target as HTMLImageElement;
        const maxWidth = window.innerWidth * 0.9;
        const maxHeight = window.innerHeight * 0.7;
        const scale = Math.min(maxWidth / img.naturalWidth, maxHeight / img.naturalHeight, 1);
        carouselWidth = img.naturalWidth * scale;
        carouselHeight = img.naturalHeight * scale;
    }

    function getAmenityDesc(amenity: any): string | null {
        return amenity.custom_description || amenity.description || null;
    }
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
                <button class="button is-primary is-rounded" onclick={() => goto('/search')}>
                    Back to Search
                </button>
            </div>
        </div>
    </main>
{:else}
    <main class="section has-background-white-bis" style="min-height: 100vh;">
        <div class="container is-max-desktop">
            <div class="mb-5">
                <h1 class="title is-2 has-text-black has-text-weight-bold mb-2">{property.name}</h1>
                <p class="subtitle is-5 has-text-grey-darker">
                    <span class="icon"><i class="fas fa-location-dot"></i></span>
                    {property.address}, {property.city} ({property.country})
                </p>
                {#if property.status === 'DRAFT'}
                    <span class="tag is-warning">Draft</span>
                {/if}
            </div>

            <div class="" style="display: flex; justify-content: center; align-items: center;">
                <div
                    class="box p-0 is-overflow-hidden shadow-soft carousel-container"
                    style="width:{carouselWidth}px; height:{carouselHeight}px;"
                >
                    <img
                        src={displayImages[currentImageIndex]}
                        class="carousel-img"
                        alt={property.name}
                        onload={onImageLoad}
                    />

                    {#if displayImages.length > 1}
                        <button class="carousel-btn prev" onclick={prevImage}>❮</button>
                        <button class="carousel-btn next" onclick={nextImage}>❯</button>

                        <div class="image-counter">
                            <span class="tag is-dark">{currentImageIndex + 1} / {displayImages.length}</span>
                        </div>
                    {/if}
                </div>
            </div>

            <div class="columns is-variable is-8">
                <div class="column is-8">
                    <section class="box p-5 shadow-soft mb-6">
                        <h3 class="title is-4 has-text-black mb-4">About this place</h3>
                        <p class="description-text" style="line-height: 1.7;">
                            {property.description || `Welcome to ${property.name}.`}
                        </p>
                    </section>

                    {#if property.amenities && property.amenities.length > 0}
                        <section class="box p-5 shadow-soft mb-6">
                            <h3 class="title is-4 has-text-black mb-5">What this place offers</h3>
                            <div class="amenities-grid">
                                {#each property.amenities as amenity}
                                    {@const desc = getAmenityDesc(amenity)}
                                    <div class="amenity-chip {desc ? 'has-tooltip' : ''}">
                                        <i class="fas {getAmenityIcon(amenity.name, amenity.category, 'property')} amenity-icon"></i>
                                        <span>{amenity.name}</span>

                                        {#if desc}
                                            <div class="tooltip-content">
                                                {#if amenity.custom_description}
                                                    <span class="has-text-weight-bold has-text-warning-light is-block mb-1">★ Details:</span>
                                                {/if}
                                                {desc}
                                            </div>
                                        {/if}
                                    </div>
                                {/each}
                            </div>
                        </section>
                    {/if}

                    <section>
                        <h3 class="title is-4 has-text-black mb-5">Available Rooms</h3>
                        {#if property.rooms && property.rooms.length > 0}
                            {#each property.rooms as room}
                                <div class="box p-5 shadow-soft mb-4 room-card">
                                    <div class="level is-mobile mb-4">
                                        <div class="level-left">
                                            <div>
                                                <h4 class="title is-5 has-text-black mb-1">
                                                    <i class="fas fa-bed mr-2 has-text-primary"></i>
                                                    {room.type}
                                                </h4>
                                                <p class="is-size-6 has-text-grey-dark">
                                                    <i class="fas fa-users mr-1"></i>
                                                    Max {room.capacity} guests
                                                </p>
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
                                        <div class="amenities-grid mb-4">
                                            {#each room.amenities as amenity}
                                                {@const desc = getAmenityDesc(amenity)}
                                                <div class="amenity-chip {desc ? 'has-tooltip' : ''}">
                                                    <i class="fas {getAmenityIcon(amenity.name, amenity.category, 'room')} amenity-icon"></i>
                                                    <span>{amenity.name}</span>

                                                    {#if desc}
                                                        <div class="tooltip-content">
                                                            {desc}
                                                        </div>
                                                    {/if}
                                                </div>
                                            {/each}
                                        </div>
                                    {/if}

                                    <button class="button is-primary is-fullwidth is-rounded has-text-weight-bold book-button">
                                        <span>Book Now</span>
                                        <i class="fas fa-arrow-right ml-2"></i>
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
                                <i class="fas fa-envelope mr-2"></i>
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
    /* ... stili base invariati ... */
    .shadow-soft { box-shadow: 0 8px 20px rgba(0, 0, 0, 0.05); border: 1px solid #f0f0f0; background: white; }
    .is-overflow-hidden { overflow: hidden; border-radius: 12px; }
    .border-bottom { border-bottom: 1px solid #f0f0f0; }
    .is-sticky { position: sticky; top: 0; z-index: 10; }
    .sticky-sidebar { position: sticky; top: 80px; }
    .owner-avatar { width: 48px; height: 48px; min-width: 48px; background: #00d1b2; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 1.2rem; }
    .carousel-container { position: relative; display: flex; justify-content: center; align-items: center; border-radius: 12px; overflow: hidden; background-color: #f5f5f5; margin-bottom: 1.5rem; }
    .carousel-img { object-fit: contain; display: block; border-radius: 12px; max-width: 100%; max-height: 100%; }
    .carousel-btn { position: absolute; top: 50%; transform: translateY(-50%); background: rgba(255, 255, 255, 0.85); border: none; width: 45px; height: 45px; border-radius: 50%; cursor: pointer; font-size: 1.2rem; display: flex; align-items: center; justify-content: center; opacity: 0; transition: opacity 0.3s ease; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); }
    .carousel-container:hover .carousel-btn { opacity: 1; }
    .carousel-btn:hover { background: white; }
    .prev { left: 20px; }
    .next { right: 20px; }
    .image-counter { position: absolute; bottom: 15px; right: 15px; }
    .description-text { color: #374151; font-size: 1.1rem; }
    .book-button { background: #00d1b2; border: none; box-shadow: 0 4px 12px rgba(0, 209, 178, 0.2); }
    :global(.title) { color: #000000 !important; }
    :global(.subtitle) { color: #4a4a4a !important; }

    /* =========================================
       STILI AMENITIES UNIFICATI
       ========================================= */
    
    .amenities-grid {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
    }

    /* Stile CHIP Unificato (Grigio/Neutro come le Rooms) */
    .amenity-chip {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.35rem 0.65rem;
        
        background-color: #f1f5f9; /* Grigio chiaro */
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        
        font-size: 0.85rem;
        font-weight: 500;
        color: #4a5568; /* Grigio scuro */
        
        transition: all 0.2s ease;
    }

    .amenity-icon {
        color: #64748b; /* Icona grigio neutro */
    }

    /* =========================================
       TOOLTIP LOGIC
       ========================================= */

    .has-tooltip {
        position: relative;
        cursor: help;
        /* Sottolineatura tratteggiata per indicare interattività su tutto */
        border-bottom: 2px dotted #cbd5e1; 
    }

    .has-tooltip:hover {
        background-color: #e2e8f0; /* Leggero scurimento al passaggio */
    }

    .tooltip-content {
        visibility: hidden;
        opacity: 0;
        position: absolute;
        bottom: 130%; /* Appare sopra */
        left: 50%;
        transform: translateX(-50%);

        /* Colore scuro 'ardesia' unificato */
        background-color: #475569; 
        color: #fff;
        text-align: center;
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 400;

        min-width: 180px;
        max-width: 260px;
        width: max-content;

        z-index: 100;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
        transition: opacity 0.2s, bottom 0.2s;
        pointer-events: none;
        white-space: normal;
        line-height: 1.4;
    }

    /* Freccina */
    .tooltip-content::after {
        content: '';
        position: absolute;
        top: 100%;
        left: 50%;
        margin-left: -5px;
        border-width: 5px;
        border-style: solid;
        border-color: #475569 transparent transparent transparent;
    }

    .has-tooltip:hover .tooltip-content {
        visibility: visible;
        opacity: 1;
        bottom: 140%;
    }
</style>