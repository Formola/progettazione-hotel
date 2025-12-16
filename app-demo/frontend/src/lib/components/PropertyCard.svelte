<script lang="ts">
    import type { PropertyData, RoomData } from '$lib/types';

    let { property } = $props<{ property: PropertyData }>();

    let minPrice = $derived.by(() => {
        if (!property?.rooms || property.rooms.length === 0) return 0;
        return Math.min(...property.rooms.map((r: RoomData) => r.price));
    });
</script>

<div class="card property-card">
    <div class="card-image">
        <figure class="image is-4by3">
            <img
                src={property.mainImage || 'https://bulma.io/images/placeholders/1280x960.png'}
                alt={property.name}
            />
            </figure>
    </div>
    
    <div class="card-content has-background-dark">
        <div class="media mb-4">
            <div class="media-content">
                <p class="title is-4 has-text-white mb-1">{property.name}</p>
                <p class="subtitle is-6 has-text-grey-light">{property.address}</p>
            </div>
        </div>

        <div class="content">
            <p class="is-size-7 has-text-grey mb-4">
                {property.description.substring(0, 100)}...
            </p>

            <div class="tags">
                {#if property.amenities}
                    {#each property.amenities.slice(0, 3) as amenity}
                        <span class="tag is-dark has-text-grey-light border-grey">{amenity.name}</span>
                    {/each}
                {/if}
            </div>

            <hr class="dark-divider" />

            <div class="level is-mobile mt-auto">
                <div class="level-left">
                    <div>
                        <p class="heading has-text-grey-light">Starting from</p>
                        <p class="title is-5 has-text-primary">
                            {minPrice > 0 ? `€${minPrice}` : 'N/A'}
                            <span class="is-size-7 has-text-grey-light has-text-weight-normal">/night</span>
                        </p>
                    </div>
                </div>
                <div class="level-right">
                    <a href="/properties/{property.id}" class="button is-primary is-outlined is-small is-rounded has-text-weight-bold">
                        Details
                    </a>
                </div>
            </div>
        </div>
    </div>
</div>

<style>
    .property-card {
        height: 100%;
        display: flex;
        flex-direction: column;
        border: none;
        overflow: hidden;
        border-radius: 12px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        background-color: #121417; /* Sfondo nero come da immagine */
    }

    .property-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(0,0,0,0.3);
    }

    .card-image img {
        object-fit: cover;
    }

    .has-background-dark {
        background-color: #121417 !important; /* */
    }

    .card-content {
        flex: 1;
        display: flex;
        flex-direction: column;
        padding: 1.5rem;
    }

    .dark-divider {
        background-color: #2d3139; /* Grigio scuro per separare i contenuti */
        height: 1px;
        border: none;
        margin: 1rem 0;
    }

    .border-grey {
        border: 1px solid #2d3139;
    }

    /* Override Bulma Title per contrasto */
    .title {
        color: #f8fafc !important; /* Bianco ghiaccio */
    }

    .has-text-grey-light {
        color: #94a3b8 !important; /* Grigio bluastro */
    }
</style>