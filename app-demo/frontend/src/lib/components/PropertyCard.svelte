<script lang="ts">
    import { goto } from '$app/navigation';
    import { selectedProperty } from '$lib/stores/selection';
    import type { MediaData, PropertyData, RoomData } from '$lib/types';
    import { getAmenityIcon } from '$lib/utils/icons';

    let { property } = $props<{ property: PropertyData }>();

    let minPrice = $derived.by(() => {
        if (!property?.rooms || property.rooms.length === 0) return 0;
        return Math.min(...property.rooms.map((r: RoomData) => r.price));
    });

    function goToDetails(e: MouseEvent) {
        e.preventDefault();
        selectedProperty.set($state.snapshot(property));
        goto(`/properties/${property.id}`);
    }

</script>

<div class="card property-card">
    <div class="card-image">
        <figure class="image is-4by3">
            <img
                src={property.media?.find((m: MediaData) => m.file_type?.startsWith('image'))?.storage_path
                    || 'https://bulma.io/images/placeholders/1280x960.png'}
                alt={property.name}
            />
        </figure>
    </div>
    
    <div class="card-content">
        <div class="mb-4">
            <h2 class="title is-4 mb-2 property-title">{property.name}</h2>
            <p class="is-size-7 has-text-primary has-text-weight-semibold location-text">
                <i class="fas fa-map-marker-alt mr-1"></i>
                {property.city}, {property.country}
            </p>
        </div>

        <div class="mb-4">
            <p class="description-text is-size-7">
                {property.description ? property.description.substring(0, 100) + '...' : 'Luxury stay with premium services.'}
            </p>
        </div>

        <div class="amenities-container mb-4">
            {#if property.amenities && property.amenities.length > 0}
                <div class="amenities-grid">
                    {#each property.amenities as amenity}
                        <div class="amenity-chip">
                            <i class="fas {getAmenityIcon(amenity.name)} amenity-icon"></i>
                            <span class="amenity-name">{amenity.name}</span>
                        </div>
                    {/each}
                </div>
            {/if}
        </div>

        <div class="mt-auto">
            <hr class="dark-divider" />

            <div class="price-footer">
                <div class="price-info">
                    <span class="price-label">From</span>
                    <div class="price-value">
                        <span class="price-amount">€{minPrice}</span>
                        <span class="price-period">/night</span>
                    </div>
                </div>
                
                <button 
                    class="button is-primary is-rounded view-button"
                    onclick={goToDetails}
                >
                    <span>View Details</span>
                    <i class="fas fa-arrow-right ml-2"></i>
                </button>
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
        border-radius: 20px;
        background: linear-gradient(145deg, #0f1115 0%, #1a1d23 100%);
        overflow: hidden;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    .property-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.4);
    }

    .card-image {
        overflow: hidden;
    }

    .card-image img {
        object-fit: cover;
        transform: scale(1.1);
        transition: transform 0.4s ease;
    }

    .property-card:hover .card-image img {
        transform: scale(0.95);
    }

    .card-content {
        flex: 1;
        display: flex;
        flex-direction: column;
        padding: 1.5rem;
    }

    .location-text {
        display: flex;
        align-items: center;
    }

    .property-title {
        color: #f9fafb !important;
        font-weight: 700;
    }

    .description-text {
        color: #9ca3af;
        line-height: 1.6;
        min-height: 3em;
    }

    /* Amenities Grid Styling */
    .amenities-grid {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
    }

    .amenity-chip {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.4rem 0.75rem;
        background-color: #1a1d23;
        border: 1px solid #2d3139;
        border-radius: 12px;
        transition: all 0.2s ease;
    }

    .amenity-chip:hover {
        background-color: #252930;
        border-color: #00d1b2;
    }

    .amenity-icon {
        color: #00d1b2;
        font-size: 0.9rem;
        min-width: 1rem;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .amenity-name {
        color: #e5e7eb;
        font-size: 0.75rem;
        font-weight: 500;
        white-space: nowrap;
    }

    .dark-divider {
        background-color: #2d3139;
        height: 1px;
        margin: 1rem 0 1.25rem 0;
        border: none;
    }

    /* Price Footer - Layout migliorato */
    .price-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 1rem;
    }

    .price-info {
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
    }

    .price-label {
        text-transform: uppercase;
        font-size: 0.625rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        color: #6b7280;
    }

    .price-value {
        display: flex;
        align-items: baseline;
        gap: 0.25rem;
    }

    .price-amount {
        font-size: 1.75rem;
        font-weight: 700;
        color: #00d1b2;
        line-height: 1;
    }

    .price-period {
        font-size: 0.75rem;
        color: #9ca3af;
        font-weight: 500;
    }

    /* Button Styling - Più compatto e professionale */
    .view-button {
        background: linear-gradient(135deg, #00d1b2 0%, #00c4a7 100%);
        border: none;
        box-shadow: 0 4px 14px rgba(0, 209, 178, 0.25);
        padding: 0.625rem 1.25rem;
        font-size: 0.875rem;
        font-weight: 600;
        height: auto;
        display: inline-flex;
        align-items: center;
        white-space: nowrap;
        transition: all 0.2s ease;
    }

    .view-button:hover {
        background: linear-gradient(135deg, #00c4a7 0%, #00b89e 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 209, 178, 0.35);
    }

    .view-button:active {
        transform: translateY(0);
    }

    .has-text-primary {
        color: #00d1b2 !important;
    }

    /* Responsive adjustments */
    @media screen and (max-width: 768px) {
        .price-footer {
            flex-direction: column;
            align-items: flex-start;
            gap: 1rem;
        }

        .view-button {
            width: 100%;
            justify-content: center;
        }

        .amenities-grid {
            justify-content: flex-start;
        }
    }
</style>