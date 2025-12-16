<script lang="ts">
    import { page } from '$app/state';
    import { searchApi } from '$lib/api/search';
    import type { PropertyData } from '$lib/types';
    import { goto } from '$app/navigation';

    // si aggiorna id se navighiamo a un'altra proprietà
    let propertyId = $derived(Number(page.params.id));
    let property = $state<PropertyData | null>(null);
    let isLoading = $state(true);
    let error = $state<string | null>(null);

    // Carousel state
    let currentImageIndex = $state(0);
    const mockImages = [
        "https://placehold.co/1200x800/f8f9fa/212529?text=Main+Property+Photo",
        "https://placehold.co/1200x800/f1f3f5/212529?text=Bedroom+View",
        "https://placehold.co/1200x800/e9ecef/212529?text=Modern+Kitchen",
        "https://placehold.co/1200x800/dee2e6/212529?text=Outdoor+Area"
    ];

    function nextImage() { currentImageIndex = (currentImageIndex + 1) % mockImages.length; }
    function prevImage() { currentImageIndex = (currentImageIndex - 1 + mockImages.length) % mockImages.length; }

    $effect(() => {
        const currentId = propertyId;
        if (!currentId) return;
        const fetchData = async () => {
            if (property && property.id === currentId) return;
            isLoading = true;
            try {
                property = await searchApi.getPropertyById(currentId);
            } catch (err) {
                error = 'Error loading property details.';
            } finally {
                isLoading = false;
            }
        };
        fetchData();
    });
</script>

{#if isLoading}
    <div class="is-flex is-justify-content-center is-align-items-center" style="height: 60vh;">
        <div class="loader is-loading" style="width: 3rem; height: 3rem;"></div>
    </div>
{:else if error || !property}
    <div class="container p-6">
        <div class="notification is-danger is-light">
            {error || 'Property not found'}
            <button class="button is-small is-dark mt-2" onclick={() => goto('/search')}>← Back to search</button>
        </div>
    </div>
{:else}
    <nav class="py-4 has-background-white border-bottom sticky-nav">
        <div class="container is-max-desktop px-3">
            <button class="button is-ghost has-text-black px-0" onclick={() => history.back()}>
                <span class="icon">←</span> <span class="has-text-weight-bold">Back to results</span>
            </button>
        </div>
    </nav>

    <main class="has-background-white pb-6">
        <div class="container is-max-desktop py-5 px-3">
            
            <div class="mb-5">
                <h1 class="title is-2 has-text-black has-text-weight-bold mb-2">{property.name}</h1>
                <p class="subtitle is-5 has-text-grey-darker">
                    <span class="icon">📍</span> {property.address}
                </p>
            </div>

            <div class="carousel-container mb-6 shadow-soft">
                <div class="carousel-slide">
                    <img src={currentImageIndex === 0 ? property.mainImage : mockImages[currentImageIndex]} alt="Property" />
                    
                    <button class="nav-btn prev" onclick={prevImage}>❮</button>
                    <button class="nav-btn next" onclick={nextImage}>❯</button>
                    
                    <div class="image-counter">
                        {currentImageIndex + 1} / {mockImages.length}
                    </div>
                </div>
            </div>

            <div class="columns is-variable is-8">
                <div class="column is-8">
                    <section class="content">
                        <h3 class="title is-4 has-text-black mb-4">Description</h3>
                        <p class="is-size-5 has-text-grey-darker" style="line-height: 1.7;">
                            {property.description}
                        </p>
                    </section>

                    <hr class="my-6" />

                    <section>
                        <h3 class="title is-4 has-text-black mb-5">What this place offers</h3>
                        <div class="columns is-multiline is-mobile">
                            {#if property.amenities}
                                {#each property.amenities as amenity}
                                    <div class="column is-6-tablet is-12-mobile">
                                        <div class="amenity-box">
                                            <span class="amenity-icon">✓</span>
                                            <span class="has-text-black has-text-weight-semibold">
                                                {typeof amenity === 'string' ? amenity : amenity.name}
                                            </span>
                                        </div>
                                    </div>
                                {/each}
                            {/if}
                        </div>
                    </section>

                    <hr class="my-6" />

                    <section>
                        <h3 class="title is-4 has-text-black mb-5">Available Rooms</h3>
                        {#if property.rooms}
                            {#each property.rooms as room}
                                <div class="room-row-modern mb-4">
                                    <div class="room-info">
                                        <h4 class="title is-5 has-text-black mb-1">{room.type}</h4>
                                        <p class="has-text-grey-darker mb-2">Max {room.capacity} guests</p>
                                        <div class="tags">
                                            {#each room.amenities || [] as a}
                                                <span class="tag is-white border-grey">{a}</span>
                                            {/each}
                                        </div>
                                    </div>
                                    <div class="room-booking">
                                        <div class="price-display">
                                            <span class="price-amount">€{room.price}</span>
                                            <span class="price-unit">/night</span>
                                        </div>
                                        <button class="button is-black is-rounded is-fullwidth mt-2">Book Now</button>
                                    </div>
                                </div>
                            {/each}
                        {/if}
                    </section>
                </div>

                <div class="column is-4">
                    <div class="sticky-sidebar">
                        <div class="box owner-card p-5">
                            <h3 class="title is-5 has-text-black mb-4">Owner Info</h3>
                            <div class="is-flex is-align-items-center mb-5">
                                <div class="owner-avatar">H</div>
                                <div>
                                    <p class="has-text-weight-bold has-text-black">Owner #{property.ownerId}</p>
                                    <p class="is-size-7 has-text-grey-darker has-text-weight-medium">Verified Property Manager</p>
                                </div>
                            </div>
                            <button class="button is-primary is-fullwidth is-rounded has-text-weight-bold">
                                Contact Owner
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </main>
{/if}

<style>
    /* UTILITIES */
    .border-bottom { border-bottom: 1px solid #f0f0f0; }
    .border-grey { border: 1px solid #dbdbdb; }
    .shadow-soft { box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
    .sticky-nav { position: sticky; top: 0; z-index: 30; }
    .sticky-sidebar { position: sticky; top: 85px; }

    /* CAROUSEL */
    .carousel-container {
        position: relative;
        height: 500px;
        background: #f5f5f5;
        border-radius: 16px;
        overflow: hidden;
    }
    .carousel-slide img { width: 100%; height: 100%; object-fit: cover; }

    /* Buttons visible on hover */
    .nav-btn {
        position: absolute;
        top: 50%;
        transform: translateY(-50%);
        background: rgba(255, 255, 255, 0.9);
        border: none;
        width: 48px;
        height: 48px;
        border-radius: 50%;
        cursor: pointer;
        opacity: 0;
        transition: all 0.2s ease-in-out;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
    }
    .carousel-container:hover .nav-btn { opacity: 1; }
    .prev { left: 20px; }
    .next { right: 20px; }

    .image-counter {
        position: absolute;
        bottom: 20px;
        right: 20px;
        background: rgba(0, 0, 0, 0.75);
        color: white;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
    }

    /* AMENITY BOX */
    .amenity-box {
        display: flex;
        align-items: center;
        padding: 1.2rem;
        background: #fafafa;
        border: 1px solid #eee;
        border-radius: 12px;
    }
    .amenity-icon { color: #00d1b2; font-weight: bold; margin-right: 15px; }

    /* ROOM ROW */
    .room-row-modern {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1.5rem;
        background: white;
        border: 1px solid #eee;
        border-radius: 16px;
        transition: border-color 0.2s;
    }
    .room-row-modern:hover { border-color: #333; }
    .price-amount { font-size: 1.8rem; font-weight: 800; color: #000; }
    .price-unit { color: #4a4a4a; font-size: 0.9rem; margin-left: 2px; }

    /* OWNER CARD (FIXED COLORS) */
    .owner-card {
        background: #ffffff;
        border: 1px solid #dbdbdb;
        border-radius: 16px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.06);
    }
    .owner-avatar {
        width: 48px; height: 48px;
        background: #f0f0f0; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        margin-right: 15px; font-weight: bold; color: #222;
        border: 1px solid #dbdbdb;
    }

    @media (max-width: 768px) {
        .carousel-container { height: 320px; }
        .room-row-modern { flex-direction: column; align-items: flex-start; }
        .room-booking { width: 100%; margin-top: 1rem; }
    }
</style>