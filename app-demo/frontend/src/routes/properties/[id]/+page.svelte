<script lang="ts">
	import { onDestroy } from 'svelte';
	import { goto } from '$app/navigation';
	import type { PropertyData } from '$lib/types';
	import { selectedProperty } from '$lib/state/selection.svelte';
	import { getAmenityIcon } from '$lib/utils/icons';

	let property = $derived(selectedProperty.value);

	$effect(() => {
		if (property?.rooms) {
			const indices: Record<string, number> = {};
			property.rooms.forEach((r) => (indices[r.id] = 0));
			roomImageIndex = indices;
		}
	});

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

	let roomImageIndex = $state<Record<string, number>>({});

	function nextRoomImage(roomId: string, total: number) {
		roomImageIndex[roomId] = ((roomImageIndex[roomId] ?? 0) + 1) % total;
	}

	function prevRoomImage(roomId: string, total: number) {
		roomImageIndex[roomId] = ((roomImageIndex[roomId] ?? 0) - 1 + total) % total;
	}
</script>

<nav class="navbar-top has-background-white py-4 is-sticky">
	<div class="container is-max-desktop px-4">
		<button class="button is-ghost has-text-black p-0 back-button" onclick={() => history.back()}>
			<span class="icon has-text-primary"><i class="fas fa-arrow-left"></i></span>
			<span class="has-text-weight-bold ml-2">Back to results</span>
		</button>
	</div>
</nav>

{#if !property}
	<main class="section has-background-white-bis" style="min-height: 100vh;">
		<div class="container is-max-desktop has-text-centered">
			<div class="box shadow-soft p-6">
				<div class="empty-state">
					<i class="fas fa-exclamation-triangle"></i>
					<h2 class="title is-4 mt-4">Property not found in memory.</h2>
					<button
						class="button is-primary is-rounded is-medium mt-4"
						onclick={() => goto('/search')}
					>
						<span class="icon"><i class="fas fa-search"></i></span>
						<span>Back to Search</span>
					</button>
				</div>
			</div>
		</div>
	</main>
{:else}
	<main class="section has-background-white-bis pb-6" style="min-height: 100vh;">
		<div class="container is-max-desktop">
			<div class="property-header mb-5">
				<div class="level is-mobile mb-3">
					<div class="level-left">
						<h1 class="title is-2 has-text-black has-text-weight-bold mb-0">{property.name}</h1>
					</div>
					<div class="level-right">
						{#if property.status === 'DRAFT'}
							<span class="tag is-warning is-medium">
								<i class="fas fa-file-alt mr-2"></i>
								Draft
							</span>
						{:else}
							<span class="tag is-success is-medium">
								<i class="fas fa-check-circle mr-2"></i>
								Published
							</span>
						{/if}
					</div>
				</div>
				<div class="location-badge">
					<i class="fas fa-map-marker-alt"></i>
					<span>{property.address}, {property.city}, {property.country}</span>
				</div>
			</div>

			<div class="carousel-wrapper mb-6">
				<div
					class="carousel-container shadow-soft"
					style="width:{carouselWidth}px; height:{carouselHeight}px;"
				>
					<img
						src={displayImages[currentImageIndex]}
						class="carousel-img"
						alt={property.name}
						onload={onImageLoad}
					/>

					{#if displayImages.length > 1}
						<button class="carousel-btn prev" onclick={prevImage} aria-label="Previous image">
							<i class="fas fa-chevron-left"></i>
						</button>
						<button class="carousel-btn next" onclick={nextImage} aria-label="Next image">
							<i class="fas fa-chevron-right"></i>
						</button>

						<div class="image-counter">
							<span class="counter-badge">
								<i class="fas fa-images mr-2"></i>
								{currentImageIndex + 1} / {displayImages.length}
							</span>
						</div>

						<div class="thumbnail-nav">
							{#each displayImages as img, idx}
								<button
									class="thumbnail {idx === currentImageIndex ? 'active' : ''}"
									onclick={() => (currentImageIndex = idx)}
									aria-label="View image {idx + 1}"
								>
									<img src={img} alt="Thumbnail {idx + 1}" />
								</button>
							{/each}
						</div>
					{/if}
				</div>
			</div>

			<div class="columns is-variable is-8">
				<div class="column is-8">
					<section class="box p-6 shadow-soft mb-5 content-card">
						<div class="section-header-clean mb-4">
							<i class="fas fa-info-circle section-icon-clean has-text-info"></i>
							<h3 class="title is-4 has-text-black mb-0">About this place</h3>
						</div>
						<p class="description-text">
							{property.description ||
								`Welcome to ${property.name}. Experience comfort and luxury in this beautiful property.`}
						</p>
					</section>

					{#if property.amenities && property.amenities.length > 0}
						<section class="box p-6 shadow-soft mb-5 content-card">
							<div class="section-header-clean mb-5">
								<i class="fas fa-star section-icon-clean has-text-warning"></i>
								<h3 class="title is-4 has-text-black mb-0">
									What this place offers
									<span class="count-badge">{property.amenities.length}</span>
								</h3>
							</div>
							<div class="amenities-grid-premium">
								{#each property.amenities as amenity}
									{@const desc = getAmenityDesc(amenity)}
									<div class="amenity-item-premium {desc ? 'has-tooltip' : ''}">
										<div class="amenity-icon-wrapper-neutral">
											<i class="fas {getAmenityIcon(amenity.name, amenity.category, 'property')}"
											></i>
										</div>
										<span class="amenity-name">{amenity.name}</span>
										{#if desc}
											<div class="tooltip-content">
												{#if amenity.custom_description}
													<span class="tooltip-highlight">★ Details:</span>
												{/if}
												{desc}
											</div>
										{/if}
									</div>
								{/each}
							</div>
						</section>
					{/if}

					<section class="rooms-section">
						<div class="section-header-clean mb-5">
							<i class="fas fa-bed section-icon-clean has-text-primary-dark"></i>
							<h3 class="title is-4 has-text-black mb-0">
								Available Rooms
								{#if property.rooms && property.rooms.length > 0}
									<span class="count-badge">{property.rooms.length}</span>
								{/if}
							</h3>
						</div>

						{#if property.rooms && property.rooms.length > 0}
							<div class="rooms-list">
								{#each property.rooms as room}
									<div class="room-card-detail box shadow-soft p-0 mb-5">
										<div class="room-content p-5">
											<div class="room-header mb-4">
												<div class="room-title-wrapper">
													<h4 class="room-title">
														<i class="fas fa-door-open mr-2 has-text-grey-dark"></i>
														{room.type}
													</h4>
													<div class="room-meta">
														<span class="meta-item">
															<i class="fas fa-users has-text-grey"></i>
															Up to {room.capacity}
															{room.capacity === 1 ? 'guest' : 'guests'}
														</span>
													</div>
												</div>
												<div class="room-price-tag">
													<span class="price-amount">€{room.price}</span>
													<span class="price-label">per night</span>
												</div>
											</div>

											{#if room.description}
												<p class="room-description mb-4">{room.description}</p>
											{/if}

											{#if room.amenities && room.amenities.length > 0}
												<div class="room-amenities-section mb-5">
													<p class="amenities-label">
														<i class="fas fa-check-circle mr-2 has-text-success"></i>
														Room Features ({room.amenities.length})
													</p>
													<div class="amenities-grid-compact">
														{#each room.amenities as amenity}
															{@const desc = getAmenityDesc(amenity)}
															<div class="amenity-chip-compact {desc ? 'has-tooltip' : ''}">
																<i
																	class="fas {getAmenityIcon(
																		amenity.name,
																		amenity.category,
																		'room'
																	)}"
																></i>
																<span>{amenity.name}</span>
																{#if desc}
																	<div class="tooltip-content">{desc}</div>
																{/if}
															</div>
														{/each}
													</div>
												</div>
											{/if}

											{#if room.media && room.media.length > 0}
												<div class="room-carousel-inline mb-5">
													<img
														src={room.media[roomImageIndex[room.id] ?? 0].storage_path}
														alt={room.type}
														class="room-carousel-img"
													/>

													{#if room.media.length > 1}
														<button
															class="room-carousel-btn prev"
															onclick={() => prevRoomImage(room.id, room.media.length)}
															aria-label="Previous room image"
														>
															❮
														</button>

														<button
															class="room-carousel-btn next"
															onclick={() => nextRoomImage(room.id, room.media.length)}
															aria-label="Next room image"
														>
															❯
														</button>

														<div class="room-carousel-counter">
															{(roomImageIndex[room.id] ?? 0) + 1} / {room.media.length}
														</div>
													{/if}
												</div>
											{/if}

											<button class="button is-primary is-large is-fullwidth book-button">
												<span class="has-text-weight-bold">Book This Room</span>
												<i class="fas fa-arrow-right ml-3"></i>
											</button>
										</div>
									</div>
								{/each}
							</div>
						{:else}
							<div class="empty-rooms">
								<i class="fas fa-bed"></i>
								<p>No rooms available at the moment</p>
							</div>
						{/if}
					</section>
				</div>

				<div class="column is-4">
					<div class="sticky-sidebar">
						<div class="box p-5 shadow-soft host-card">
							<p class="heading-label mb-4">
								<i class="fas fa-user-tie mr-2 has-text-info-dark"></i>
								Property Manager
							</p>
							<div class="host-info mb-4">
								<div class="host-avatar">
									{property.owner?.name ? property.owner.name.charAt(0).toUpperCase() : '?'}
								</div>
								<div class="host-details">
									<p class="host-name">
										{property.owner?.name || 'Property Manager'}
									</p>
									<p class="host-email">{property.owner?.email || 'contact@property.com'}</p>
								</div>
							</div>
							<button class="button is-primary is-fullwidth is-medium contact-button">
								<span class="icon"><i class="fas fa-envelope"></i></span>
								<span class="has-text-weight-bold">Contact Host</span>
							</button>
						</div>

						<div class="box p-5 shadow-soft mt-4 info-card">
							<p class="heading-label mb-4">
								<i class="fas fa-info-circle mr-2 has-text-info"></i>
								Quick Info
							</p>
							<div class="info-items">
								<div class="info-item">
									<i class="fas fa-hotel"></i>
									<div>
										<span class="info-label">Rooms</span>
										<span class="info-value">{property.rooms?.length || 0}</span>
									</div>
								</div>
								<div class="info-item">
									<i class="fas fa-images"></i>
									<div>
										<span class="info-label">Photos</span>
										<span class="info-value">{property.media?.length || 0}</span>
									</div>
								</div>
								<div class="info-item">
									<i class="fas fa-concierge-bell"></i>
									<div>
										<span class="info-label">Amenities</span>
										<span class="info-value">{property.amenities?.length || 0}</span>
									</div>
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</main>
{/if}

<style>
	/* Base Styles */
	.navbar-top {
		border-bottom: 2px solid #f0f0f0;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
	}

	.is-sticky {
		position: sticky;
		top: 0;
		z-index: 50;
		backdrop-filter: blur(10px);
		background: rgba(255, 255, 255, 0.95) !important;
	}

	.back-button {
		transition: all 0.2s ease;
	}

	.back-button:hover {
		transform: translateX(-4px);
	}

	.shadow-soft {
		box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
		border: 1px solid #f0f0f0;
		background: white;
	}

	/* Property Header */
	.property-header {
		animation: fadeInUp 0.5s ease;
	}

	.location-badge {
		display: inline-flex;
		align-items: center;
		gap: 0.75rem;
		padding: 0.75rem 1.25rem;
		background: linear-gradient(135deg, #00d1b2 0%, #00b89c 100%);
		color: white;
		border-radius: 30px;
		font-weight: 600;
		font-size: 1rem;
		box-shadow: 0 4px 12px rgba(0, 209, 178, 0.25);
	}

	.location-badge i {
		font-size: 1.1rem;
	}

	/* Carousel */
	.carousel-wrapper {
		display: flex;
		justify-content: center;
		animation: fadeIn 0.6s ease;
	}

	.carousel-container {
		position: relative;
		border-radius: 16px;
		overflow: hidden;
		background: #f5f5f5;
		transition: all 0.3s ease;
	}

	.carousel-container:hover {
		box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
	}

	.carousel-img {
		object-fit: contain;
		display: block;
		border-radius: 16px;
		max-width: 100%;
		max-height: 100%;
	}

	.carousel-btn {
		position: absolute;
		top: 50%;
		transform: translateY(-50%);
		background: rgba(255, 255, 255, 0.95);
		border: none;
		width: 50px;
		height: 50px;
		border-radius: 50%;
		cursor: pointer;
		display: flex;
		align-items: center;
		justify-content: center;
		opacity: 0;
		transition: all 0.3s ease;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
		color: #00d1b2;
		font-size: 1.2rem;
	}

	.carousel-container:hover .carousel-btn {
		opacity: 1;
	}

	.carousel-btn:hover {
		background: white;
		transform: translateY(-50%) scale(1.1);
	}

	.carousel-btn.prev {
		left: 20px;
	}

	.carousel-btn.next {
		right: 20px;
	}

	.image-counter {
		position: absolute;
		bottom: 20px;
		right: 20px;
	}

	.counter-badge {
		background: rgba(0, 0, 0, 0.75);
		backdrop-filter: blur(10px);
		color: white;
		padding: 0.75rem 1.25rem;
		border-radius: 25px;
		font-weight: 600;
		font-size: 0.95rem;
		display: inline-flex;
		align-items: center;
	}

	.thumbnail-nav {
		position: absolute;
		bottom: 20px;
		left: 50%;
		transform: translateX(-50%);
		display: flex;
		gap: 0.5rem;
		padding: 0.5rem;
		background: rgba(0, 0, 0, 0.5);
		backdrop-filter: blur(10px);
		border-radius: 12px;
	}

	.thumbnail {
		width: 60px;
		height: 40px;
		border-radius: 6px;
		overflow: hidden;
		border: 2px solid transparent;
		cursor: pointer;
		transition: all 0.2s ease;
		background: none;
		padding: 0;
	}

	.thumbnail img {
		width: 100%;
		height: 100%;
		object-fit: cover;
		display: block;
	}

	.thumbnail.active {
		border-color: #00d1b2;
		transform: scale(1.1);
	}

	.thumbnail:hover {
		border-color: white;
	}

	/* Content Cards */
	.content-card {
		animation: fadeInUp 0.6s ease;
		transition: all 0.3s ease;
	}

	.content-card:hover {
		transform: translateY(-4px);
		box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
	}

	/* SECTION HEADERS (NEW CLEAN STYLE) */
	.section-header-clean {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		padding-bottom: 0.75rem;
		border-bottom: 1px solid #f0f0f0;
	}

	.section-icon-clean {
		font-size: 1.5rem;
		/* Rimosso sfondo verde pesante */
	}

	.count-badge {
		display: inline-block;
		background: #00d1b2;
		color: white;
		padding: 0.2rem 0.6rem;
		border-radius: 20px;
		font-size: 0.8rem;
		font-weight: 600;
		margin-left: 0.5rem;
		vertical-align: middle;
	}

	.description-text {
		color: #4a5568;
		font-size: 1.1rem;
		line-height: 1.8;
	}

	/* Premium Amenities Grid */
	.amenities-grid-premium {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
		gap: 1rem;
	}

	.amenity-item-premium {
		display: flex;
		align-items: center;
		gap: 1rem;
		padding: 1rem;
		background: #ffffff;
		border: 1px solid #e2e8f0;
		border-radius: 12px;
		transition: all 0.3s ease;
		position: relative;
	}

	.amenity-item-premium:hover {
		border-color: #cbd5e0;
		transform: translateY(-2px);
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
	}

	/* ICONA NEUTRA/ELEGANTE (Non più verde) */
	.amenity-icon-wrapper-neutral {
		width: 40px;
		height: 40px;
		background: #f1f5f9; /* Grigio chiaro elegante */
		color: #475569; /* Slate Blue scuro */
		border-radius: 10px;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 1.1rem;
		flex-shrink: 0;
	}

	.amenity-name {
		font-weight: 600;
		color: #2d3748;
		font-size: 0.95rem;
	}

	/* Room Cards */
	.room-card-detail {
		border-radius: 16px;
		overflow: hidden;
		transition: all 0.3s ease;
		animation: fadeInUp 0.7s ease;
	}

	.room-card-detail:hover {
		transform: translateY(-4px);
		box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12);
	}

	.room-content {
		display: flex;
		flex-direction: column;
		height: 100%;
	}

	.room-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		gap: 1rem;
	}

	.room-title {
		font-size: 1.5rem;
		font-weight: 800;
		color: #2d3748;
		margin-bottom: 0.5rem;
		display: flex;
		align-items: center;
	}

	.room-meta {
		display: flex;
		gap: 1rem;
		flex-wrap: wrap;
	}

	.meta-item {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		color: #718096;
		font-weight: 500;
		font-size: 0.95rem;
	}

	.room-price-tag {
		display: flex;
		flex-direction: column;
		align-items: flex-end;
		padding: 0.75rem 1.25rem;
		background: linear-gradient(135deg, #00d1b2 0%, #00b89c 100%);
		border-radius: 12px;
		color: white;
	}

	.price-amount {
		font-size: 1.8rem;
		font-weight: 800;
		line-height: 1;
	}

	.price-label {
		font-size: 0.85rem;
		opacity: 0.9;
		margin-top: 0.25rem;
	}

	.room-description {
		color: #4a5568;
		line-height: 1.7;
		font-size: 1rem;
	}

	.room-amenities-section {
		padding: 1rem;
		background: #f8fafc;
		border-radius: 10px;
	}

	.amenities-label {
		font-weight: 700;
		color: #2d3748;
		margin-bottom: 0.75rem;
		font-size: 0.95rem;
	}

	.amenities-grid-compact {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
	}

	.amenity-chip-compact {
		display: inline-flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.5rem 0.9rem;
		background: white;
		border: 1px solid #e2e8f0; /* Bordo più sottile */
		border-radius: 10px;
		font-size: 0.85rem;
		font-weight: 600;
		color: #4a5568;
		transition: all 0.2s ease;
		position: relative;
	}

	.amenity-chip-compact:hover {
		border-color: #cbd5e0;
		background: #f1f5f9;
		transform: translateY(-1px);
	}

	.amenity-chip-compact i {
		color: #475569; /* Colore scuro, non verde */
	}

	/* ========================================= */
	/* ROOM CAROUSEL INLINE                      */
	/* ========================================= */

	.room-carousel-inline {
		position: relative;
		background: #f5f5f5;
		width: 100%;
		height: 300px; /* Altezza bilanciata */
		border-radius: 12px;
		overflow: hidden;
		box-shadow: inset 0 0 20px rgba(0, 0, 0, 0.05);
	}

	.room-carousel-img {
		width: 100%;
		height: 100%;
		object-fit: cover;
		display: block;
		transition: transform 0.5s ease;
	}

	.room-carousel-inline:hover .room-carousel-img {
		transform: scale(1.03);
	}

	.room-carousel-btn {
		position: absolute;
		top: 50%;
		transform: translateY(-50%);
		background: rgba(255, 255, 255, 0.9);
		border: none;
		width: 40px;
		height: 40px;
		border-radius: 50%;
		cursor: pointer;
		display: flex;
		align-items: center;
		justify-content: center;
		opacity: 0;
		transition: all 0.2s ease;
		box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
		color: #333;
		z-index: 5;
		font-size: 1rem;
	}

	.room-carousel-inline:hover .room-carousel-btn {
		opacity: 1;
	}

	.room-carousel-btn:hover {
		background: white;
		transform: translateY(-50%) scale(1.1);
		color: #00d1b2;
	}

	.room-carousel-btn.prev {
		left: 15px;
	}
	.room-carousel-btn.next {
		right: 15px;
	}

	.room-carousel-counter {
		position: absolute;
		bottom: 15px;
		right: 15px;
		background: rgba(0, 0, 0, 0.7);
		color: white;
		font-size: 0.8rem;
		font-weight: 600;
		padding: 4px 10px;
		border-radius: 20px;
		backdrop-filter: blur(4px);
		z-index: 5;
		pointer-events: none;
	}

	.book-button {
		background: linear-gradient(135deg, #00d1b2 0%, #00b89c 100%);
		border: none;
		border-radius: 12px;
		box-shadow: 0 4px 16px rgba(0, 209, 178, 0.3);
		transition: all 0.3s ease;
		margin-top: auto;
	}

	.book-button:hover {
		transform: translateY(-2px);
		box-shadow: 0 8px 24px rgba(0, 209, 178, 0.4);
	}

	/* Sidebar */
	.sticky-sidebar {
		position: sticky;
		top: 100px;
		animation: fadeInRight 0.6s ease;
	}

	.host-card,
	.info-card {
		transition: all 0.3s ease;
	}

	.host-card:hover,
	.info-card:hover {
		transform: translateY(-4px);
		box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
	}

	.heading-label {
		font-weight: 700;
		color: #2d3748;
		text-transform: uppercase;
		font-size: 0.8rem;
		letter-spacing: 0.5px;
	}

	.host-info {
		display: flex;
		align-items: center;
		gap: 1rem;
		padding: 1rem;
		background: #f8fafc;
		border-radius: 12px;
	}

	.host-avatar {
		width: 60px;
		height: 60px;
		min-width: 60px;
		background: linear-gradient(135deg, #00d1b2 0%, #00b89c 100%);
		color: white;
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		font-weight: 800;
		font-size: 1.5rem;
		box-shadow: 0 4px 12px rgba(0, 209, 178, 0.3);
	}

	.host-details {
		flex: 1;
		overflow: hidden;
	}

	.host-name {
		font-weight: 700;
		color: #2d3748;
		font-size: 1.05rem;
		margin-bottom: 0.25rem;
		white-space: nowrap;
		text-overflow: ellipsis;
		overflow: hidden;
	}

	.host-email {
		color: #718096;
		font-size: 0.9rem;
		white-space: nowrap;
		text-overflow: ellipsis;
		overflow: hidden;
	}

	.contact-button {
		background: linear-gradient(135deg, #00d1b2 0%, #00b89c 100%);
		border: none;
		border-radius: 10px;
		box-shadow: 0 4px 12px rgba(0, 209, 178, 0.25);
		transition: all 0.3s ease;
	}

	.contact-button:hover {
		transform: translateY(-2px);
		box-shadow: 0 6px 20px rgba(0, 209, 178, 0.35);
	}

	.info-items {
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.info-item {
		display: flex;
		align-items: center;
		gap: 1rem;
		padding: 1rem;
		background: #f8fafc;
		border-radius: 10px;
		transition: all 0.2s ease;
	}

	.info-item:hover {
		background: #f0fdf4;
		transform: translateX(4px);
	}

	/* Icone info laterali: lasciamo il verde/blu qui per continuità ma più sobrio */
	.info-item i {
		width: 40px;
		height: 40px;
		background: linear-gradient(135deg, #00d1b2 0%, #00b89c 100%);
		color: white;
		border-radius: 10px;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 1.1rem;
		flex-shrink: 0;
	}

	.info-item div {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
	}

	.info-label {
		font-size: 0.85rem;
		color: #718096;
		font-weight: 500;
	}

	.info-value {
		font-size: 1.25rem;
		color: #2d3748;
		font-weight: 700;
	}

	/* Tooltip */
	.has-tooltip {
		position: relative;
		cursor: help;
	}

	.tooltip-content {
		visibility: hidden;
		opacity: 0;
		position: absolute;
		bottom: 130%;
		left: 50%;
		transform: translateX(-50%);
		background-color: #2d3748;
		color: #fff;
		text-align: center;
		padding: 0.75rem 1rem;
		border-radius: 8px;
		font-size: 0.85rem;
		font-weight: 400;
		min-width: 200px;
		max-width: 280px;
		width: max-content;
		z-index: 100;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
		transition:
			opacity 0.3s,
			bottom 0.3s;
		pointer-events: none;
		white-space: normal;
		line-height: 1.5;
	}

	.tooltip-content::after {
		content: '';
		position: absolute;
		top: 100%;
		left: 50%;
		margin-left: -6px;
		border-width: 6px;
		border-style: solid;
		border-color: #2d3748 transparent transparent transparent;
	}

	.has-tooltip:hover .tooltip-content {
		visibility: visible;
		opacity: 1;
		bottom: 140%;
	}

	.tooltip-highlight {
		display: block;
		color: #fbbf24;
		font-weight: 700;
		margin-bottom: 0.5rem;
	}

	/* Empty States */
	.empty-state {
		padding: 4rem 2rem;
		text-align: center;
	}

	.empty-state i {
		font-size: 4rem;
		color: #cbd5e0;
	}

	.empty-rooms {
		padding: 4rem 2rem;
		text-align: center;
		background: #f8fafc;
		border-radius: 12px;
		border: 2px dashed #e2e8f0;
	}

	.empty-rooms i {
		font-size: 3rem;
		color: #cbd5e0;
		margin-bottom: 1rem;
	}

	.empty-rooms p {
		color: #718096;
		font-size: 1.1rem;
	}

	/* Animations */
	@keyframes fadeIn {
		from {
			opacity: 0;
		}
		to {
			opacity: 1;
		}
	}

	@keyframes fadeInUp {
		from {
			opacity: 0;
			transform: translateY(20px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	@keyframes fadeInRight {
		from {
			opacity: 0;
			transform: translateX(20px);
		}
		to {
			opacity: 1;
			transform: translateX(0);
		}
	}

	/* Responsive */
	@media (max-width: 768px) {
		.room-card-detail .columns {
			flex-direction: column;
		}

		.room-image-section {
			min-height: 250px;
		}

		.room-header {
			flex-direction: column;
		}

		.room-price-tag {
			width: 100%;
			flex-direction: row;
			justify-content: space-between;
			align-items: center;
		}

		.amenities-grid-premium {
			grid-template-columns: 1fr;
		}

		.thumbnail-nav {
			display: none;
		}

		.sticky-sidebar {
			position: static;
		}

		.room-carousel-inline {
			height: 220px;
		}
	}
</style>
