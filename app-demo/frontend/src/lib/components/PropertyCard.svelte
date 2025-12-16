<script lang="ts">
    import type { PropertyData, RoomData } from '$lib/types';

    // Destrutturazione reattiva delle props
    let { property } = $props<{ property: PropertyData }>();

    // Questo non blocca l'esecuzione e non crea loop di render
    $inspect(property);

    let minPrice = $derived.by(() => {
        if (!property?.rooms || property.rooms.length === 0) return 0;
        return Math.min(...property.rooms.map((r: RoomData) => r.price));
    });
</script>

<div class="card h-100">
	<div class="card-image">
		<figure class="image is-4by3">
			<img
				src={property.mainImage || 'https://bulma.io/images/placeholders/1280x960.png'}
				alt={property.name}
				style="object-fit: cover;"
			/>
		</figure>
	</div>
	<div class="card-content">
		<div class="media">
			<div class="media-content">
				<p class="title is-4">{property.name}</p>
				<p class="subtitle is-6 has-text-grey">{property.address}</p>
			</div>
		</div>

		<div class="content">
			<p class="is-size-7 has-text-grey-dark">
				{property.description.substring(0, 100)}...
			</p>

			<div class="tags">
				{#if property.amenities}
					{#each property.amenities.slice(0, 3) as amenity}
						<span class="tag is-light is-info">{amenity.name}</span>
					{/each}
				{/if}
			</div>

			<hr class="dropdown-divider" />

			<div class="level is-mobile">
				<div class="level-left">
					<div>
						<p class="heading">Starting from</p>
						<p class="title is-5 has-text-primary">
							{minPrice > 0 ? `€${minPrice}` : 'Check avail.'}
							<span class="is-size-7 has-text-grey has-text-weight-normal">/night</span>
						</p>
					</div>
				</div>
				<div class="level-right">
					<a href="/properties/{property.id}" class="button is-primary is-outlined is-small">
                        Details
                    </a>
				</div>
			</div>
		</div>
	</div>
</div>

<style>
	/* Un piccolo tocco per rendere le card tutte uguali in altezza se necessario */
	.card {
		height: 100%;
		display: flex;
		flex-direction: column;
	}
	.card-content {
		flex: 1;
		display: flex;
		flex-direction: column;
		justify-content: space-between;
	}
</style>
