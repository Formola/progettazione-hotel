<script lang="ts">
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { fade } from 'svelte/transition';
	import { auth } from '$lib/state/auth.svelte';
	import { propertyApi } from '$lib/api/propertyApi';
	import { roomApi } from '$lib/api/roomApi';
	import { mediaApi } from '$lib/api/mediaApi';
	import { getAmenityIcon } from '$lib/utils/icons';
	import {
		type PropertyData,
		type PropertyInput,
		type PropertyAmenity,
		type RoomAmenity,
		type MediaInput,
		type MediaType,
		type RoomData,
		type RoomInput,
		type NewAmenityInput,
		AMENITY_CATEGORIES
	} from '$lib/types';

	const propertyId = $page.params.id ?? '';

	// --- STATE ---
	let activeTab = $state<'general' | 'amenities' | 'rooms' | 'photos'>('general');
	let isLoading = $state(true);
	let isSaving = $state(false);
	let error = $state<string | null>(null);
	let successMessage = $state<string | null>(null);

	// Dati Property
	let property = $state<PropertyData | null>(null);
	let rooms = $state<RoomData[]>([]);

	// Cataloghi
	let propertyAmenityCatalog = $state<PropertyAmenity[]>([]);
	let roomAmenityCatalog = $state<RoomAmenity[]>([]);
	let existingCustomAmenities = $state<PropertyAmenity[]>([]);

	// Form Property
	let formData = $state<PropertyInput>({
		name: '',
		description: '',
		address: '',
		city: '',
		country: '',
		amenities: [],
		new_amenities: [],
		media_ids: []
	});

	// --- ROOM MODAL STATE ---
	let isRoomModalOpen = $state(false);
	let editingRoomId = $state<string | null>(null);
	let activeRoomTab = $state<'details' | 'photos'>('details');
	let currentRoomCustomAmenities = $state<RoomAmenity[]>([]);

	let newRoomData = $state<RoomInput>({
		type: 'DOUBLE',
		price: 100,
		capacity: 2,
		description: '',
		amenities: [],
		new_amenities: [],
		media_ids: []
	});

	let roomFilter = $state<'ALL' | 'SINGLE' | 'DOUBLE' | 'SUITE'>('ALL');

	const roomTypeWeight: Record<string, number> = {
		SINGLE: 1,
		DOUBLE: 2,
		SUITE: 3
	};

	let displayedRooms = $derived(
		rooms
			// Filtra
			.filter((r) => roomFilter === 'ALL' || r.type === roomFilter)
			// Ordina (Tipo ASC, poi Prezzo ASC)
			.sort((a, b) => {
				const weightA = roomTypeWeight[a.type] || 99;
				const weightB = roomTypeWeight[b.type] || 99;

				// Se i tipi sono diversi, ordina per peso (Single -> Double -> Suite)
				if (weightA !== weightB) return weightA - weightB;

				// Se il tipo è uguale, ordina per prezzo
				return a.price - b.price;
			})
	);

	// Media Stanza
	let roomNewFiles = $state<File[]>([]);
	let roomPreviews = $state<string[]>([]);

	// Temp Inputs Amenities
	let tempNewAmenity = $state<NewAmenityInput>({
		name: '',
		category: AMENITY_CATEGORIES[0],
		description: ''
	});
	let tempNewRoomAmenity = $state<NewAmenityInput>({
		name: '',
		category: AMENITY_CATEGORIES[0],
		description: ''
	});

	// Media Property
	let newFiles = $state<File[]>([]);
	let newPreviews = $state<string[]>([]);

	// --- LIFECYCLE ---
	$effect(() => {
		if (!auth.isAuthenticated) goto('/');
	});

	onMount(async () => {
		if (!propertyId) {
			error = 'Invalid Property ID';
			return;
		}
		await loadAllData();
	});

	async function loadAllData() {
		try {
			isLoading = true;
			const [propCat, roomCat, prop, roomList] = await Promise.all([
				propertyApi.getAmenityCatalog(),
				roomApi.getAmenityCatalog(),
				propertyApi.getPropertyById(propertyId),
				propertyApi.getRoomsForProperty(propertyId)
			]);

			propertyAmenityCatalog = propCat;
			roomAmenityCatalog = roomCat;
			property = prop;
			rooms = roomList;

			recalcPropertyCustomAmenities(prop, propCat);

			formData = {
				name: prop.name,
				description: prop.description || '',
				address: prop.address,
				city: prop.city,
				country: prop.country,
				amenities: prop.amenities.map((a) => ({
					id: a.id,
					custom_description: a.custom_description || ''
				})),
				new_amenities: [],
				media_ids: prop.media.map((m) => m.id)
			};
		} catch (e) {
			console.error(e);
			error = 'Failed to load property details.';
		} finally {
			isLoading = false;
		}
	}

	function recalcPropertyCustomAmenities(prop: PropertyData, catalog: PropertyAmenity[]) {
		const catalogIds = new Set(catalog.map((a) => a.id));
		existingCustomAmenities = prop.amenities.filter((a) => !catalogIds.has(a.id));
	}

	// --- PROPERTY FORM LOGIC ---
	function isPropAmenitySelected(id: string) {
		return formData.amenities.some((a) => a.id === id);
	}

	function togglePropAmenity(id: string) {
		const idx = formData.amenities.findIndex((a) => a.id === id);
		if (idx >= 0) formData.amenities = formData.amenities.filter((a) => a.id !== id);
		else formData.amenities = [...formData.amenities, { id, custom_description: '' }];
	}

	async function handleUpdate(tabName: string) {
		try {
			isSaving = true;
			error = null;
			successMessage = null;
			const updated = await propertyApi.updateProperty(propertyId, formData);
			property = updated;
			recalcPropertyCustomAmenities(updated, propertyAmenityCatalog);

			formData.amenities = updated.amenities.map((a) => ({
				id: a.id,
				custom_description: a.custom_description || ''
			}));
			formData.new_amenities = [];

			successMessage = `${tabName} updated successfully!`;
			setTimeout(() => (successMessage = null), 3000);
		} catch (e) {
			console.error(e);
			error = 'Update failed.';
		} finally {
			isSaving = false;
		}
	}

	function addCustomAmenityToForm() {
		if (!tempNewAmenity.name.trim()) return;
		formData.new_amenities = [...(formData.new_amenities || []), { ...tempNewAmenity }];
		tempNewAmenity = { name: '', category: AMENITY_CATEGORIES[0], description: '' };
	}
	function removeCustomAmenityFromForm(index: number) {
		formData.new_amenities = formData.new_amenities?.filter((_, i) => i !== index);
	}

	// --- ROOMS FORM LOGIC ---
	function openAddRoomModal() {
		editingRoomId = null;
		activeRoomTab = 'details';
		currentRoomCustomAmenities = [];
		roomNewFiles = [];
		roomPreviews = [];
		newRoomData = {
			type: 'DOUBLE',
			price: 100,
			capacity: 2,
			description: '',
			amenities: [],
			new_amenities: [],
			media_ids: []
		};
		isRoomModalOpen = true;
	}

	function openEditRoomModal(room: RoomData, targetTab: 'details' | 'photos' = 'details') {
		editingRoomId = room.id;
		activeRoomTab = targetTab;
		roomNewFiles = [];
		roomPreviews = [];

		const catalogIds = new Set(roomAmenityCatalog.map((a) => a.id));
		currentRoomCustomAmenities = room.amenities.filter((a) => !catalogIds.has(a.id));

		newRoomData = {
			type: room.type,
			price: room.price,
			capacity: room.capacity,
			description: room.description || '',
			amenities: room.amenities.map((a) => ({
				id: a.id,
				custom_description: a.custom_description || ''
			})),
			new_amenities: [],
			media_ids: room.media.map((m) => m.id)
		};
		isRoomModalOpen = true;
	}

	function toggleRoomAmenity(amenityId: string) {
		const idx = newRoomData.amenities.findIndex((a) => a.id === amenityId);
		if (idx >= 0) newRoomData.amenities = newRoomData.amenities.filter((a) => a.id !== amenityId);
		else
			newRoomData.amenities = [...newRoomData.amenities, { id: amenityId, custom_description: '' }];
	}
	function isRoomAmenitySelected(amenityId: string) {
		return newRoomData.amenities.some((a) => a.id === amenityId);
	}

	function addCustomAmenityToRoom() {
		if (!tempNewRoomAmenity.name.trim()) return;
		if (!newRoomData.new_amenities) newRoomData.new_amenities = [];
		newRoomData.new_amenities = [...newRoomData.new_amenities, { ...tempNewRoomAmenity }];
		tempNewRoomAmenity = { name: '', category: AMENITY_CATEGORIES[0], description: '' };
	}
	function removeCustomAmenityFromRoom(index: number) {
		if (newRoomData.new_amenities)
			newRoomData.new_amenities = newRoomData.new_amenities.filter((_, i) => i !== index);
	}

	// --- ROOM MEDIA HANDLING ---
	function handleRoomFileSelect(event: Event) {
		const input = event.target as HTMLInputElement;
		if (input.files) {
			const files = Array.from(input.files);
			roomNewFiles = [...roomNewFiles, ...files];
			files.forEach((file) => {
				const reader = new FileReader();
				reader.onload = (e) => {
					if (e.target?.result) roomPreviews = [...roomPreviews, e.target.result as string];
				};
				reader.readAsDataURL(file);
			});
		}
		input.value = '';
	}

	function removeRoomNewFile(index: number) {
		roomNewFiles = roomNewFiles.filter((_, i) => i !== index);
		roomPreviews = roomPreviews.filter((_, i) => i !== index);
	}

	async function deleteRoomExistingPhoto(mediaId: string) {
		if (!confirm('Delete this photo?')) return;
		try {
			await mediaApi.deleteMedia(mediaId);
			if (editingRoomId) {
				const rIndex = rooms.findIndex((r) => r.id === editingRoomId);
				if (rIndex >= 0) {
					rooms[rIndex].media = rooms[rIndex].media.filter((m) => m.id !== mediaId);
					rooms = [...rooms];
				}
			}
		} catch (e) {
			console.error(e);
			alert('Failed to delete photo');
		}
	}

	// --- SAVE ROOM ORCHESTRATION ---
	async function saveRoom() {
		try {
			isSaving = true;
			let savedRoomId: string | null = null;
			if (editingRoomId) {
				let updated = await roomApi.updateRoom(editingRoomId, newRoomData);
				if (newRoomData.new_amenities && newRoomData.new_amenities.length > 0) {
					for (const newAm of newRoomData.new_amenities) {
						updated = await roomApi.addAmenityToRoom(editingRoomId, newAm);
					}
				}
				savedRoomId = updated.id;
				rooms = rooms.map((r) => (r.id === editingRoomId ? updated : r));
				successMessage = 'Room updated successfully';
			} else {
				const created = await propertyApi.addRoomToProperty(propertyId, newRoomData);
				savedRoomId = created.id;
				rooms = [...rooms, created];
				successMessage = 'Room created successfully';
			}

			if (savedRoomId && roomNewFiles.length > 0) {
				for (const file of roomNewFiles) {
					const fullBase64 = await mediaApi.fileToBase64(file);
					const cleanBase64 = fullBase64.includes(',') ? fullBase64.split(',')[1] : fullBase64;
					const payload: MediaInput = {
						fileName: file.name,
						fileType: file.type as MediaType,
						base64Data: cleanBase64,
						description: 'Room Photo',
						roomId: savedRoomId
					};
					await mediaApi.uploadMedia(payload);
				}
				const freshRoom = await roomApi.getRoomDetails(savedRoomId);
				rooms = rooms.map((r) => (r.id === savedRoomId ? freshRoom : r));
			}

			isRoomModalOpen = false;
			setTimeout(() => (successMessage = null), 3000);
		} catch (e: any) {
			console.error(e);
			alert('Error saving room: ' + (e.message || e));
		} finally {
			isSaving = false;
		}
	}

	async function deleteRoom(roomId: string) {
		if (!confirm('Delete this room?')) return;
		try {
			await roomApi.deleteRoom(roomId);
			rooms = rooms.filter((r) => r.id !== roomId);
		} catch (e) {
			console.error(e);
			alert('Failed to delete room');
		}
	}

	// --- PROPERTY PHOTOS ---
	function handleFileSelect(event: Event) {
		const input = event.target as HTMLInputElement;
		if (input.files) {
			const files = Array.from(input.files);
			newFiles = [...newFiles, ...files];
			files.forEach((file) => {
				const reader = new FileReader();
				reader.onload = (e) => {
					if (e.target?.result) newPreviews = [...newPreviews, e.target.result as string];
				};
				reader.readAsDataURL(file);
			});
		}
		input.value = '';
	}
	async function uploadNewPhotos() {
		if (newFiles.length === 0) return;
		try {
			isSaving = true;
			for (const file of newFiles) {
				const fullBase64 = await mediaApi.fileToBase64(file);
				const cleanBase64 = fullBase64.includes(',') ? fullBase64.split(',')[1] : fullBase64;
				const payload: MediaInput = {
					fileName: file.name,
					fileType: file.type as MediaType,
					base64Data: cleanBase64,
					description: 'Gallery',
					propertyId: propertyId
				};
				await mediaApi.uploadMedia(payload);
			}
			property = await propertyApi.getPropertyById(propertyId);
			newFiles = [];
			newPreviews = [];
			successMessage = 'Photos uploaded successfully!';
			setTimeout(() => (successMessage = null), 3000);
		} catch (e) {
			console.error(e);
			error = 'Failed to upload photos.';
		} finally {
			isSaving = false;
		}
	}

	function removeNewFile(index: number) {
		newFiles = newFiles.filter((_, i) => i !== index);
		newPreviews = newPreviews.filter((_, i) => i !== index);
	}

	async function deletePhoto(mediaId: string) {
		if (!confirm('Delete this photo?')) return;
		try {
			await mediaApi.deleteMedia(mediaId);
			if (property) property.media = property.media.filter((m) => m.id !== mediaId);
		} catch (e) {
			console.error(e);
			alert('Failed to delete photo');
		}
	}

	function getAmenityDesc(amenity: any): string | null {
		return amenity.custom_description || amenity.description || null;
	}

	// Helper per classe colore dinamico
	function getRoomTypeClass(type: string | undefined): string {
		if (!type) return 'type-double'; // Default
		const t = type.toUpperCase();
		if (t === 'SUITE') return 'type-suite';
		if (t === 'SINGLE') return 'type-single';
		return 'type-double';
	}
</script>

<main class="section has-background-white-bis" style="min-height: 100vh;">
	<div class="container is-max-desktop">
		<div class="mb-6 is-flex is-justify-content-space-between is-align-items-center">
			<div>
				<button
					class="button is-ghost pl-0 has-text-grey-darker"
					onclick={() => goto('/owner/dashboard')}
				>
					<span class="icon is-small"><i class="fas fa-arrow-left"></i></span>
					<span class="has-text-weight-medium">Back to Dashboard</span>
				</button>
				<h1 class="title is-2 has-text-black has-text-weight-bold mt-2">Edit Property</h1>
			</div>
			{#if property}
				<div class="tags has-addons">
					<span class="tag is-medium is-dark">Status</span>
					<span
						class="tag is-medium {property.status === 'PUBLISHED' ? 'is-success' : 'is-warning'}"
					>
						{property.status}
					</span>
				</div>
			{/if}
		</div>

		{#if isLoading}
			<div class="has-text-centered p-6">
				<button class="button is-loading is-ghost is-large">Loading</button>
			</div>
		{:else if !property}
			<div class="notification is-danger shadow-sm">Property not found.</div>
		{:else}
			<div class="tabs is-boxed is-medium mb-0">
				<ul>
					<li class={activeTab === 'general' ? 'is-active' : ''}>
						<button class="button is-ghost is-fullwidth" onclick={() => (activeTab = 'general')}>
							<span class="icon is-small"><i class="fas fa-info-circle"></i></span>
							<span>General Info</span>
						</button>
					</li>
					<li class={activeTab === 'amenities' ? 'is-active' : ''}>
						<button class="button is-ghost is-fullwidth" onclick={() => (activeTab = 'amenities')}>
							<span class="icon is-small"><i class="fas fa-concierge-bell"></i></span>
							<span>Amenities</span>
						</button>
					</li>
					<li class={activeTab === 'rooms' ? 'is-active' : ''}>
						<button class="button is-ghost is-fullwidth" onclick={() => (activeTab = 'rooms')}>
							<span class="icon is-small"><i class="fas fa-bed"></i></span>
							<span>Rooms ({rooms.length})</span>
						</button>
					</li>
					<li class={activeTab === 'photos' ? 'is-active' : ''}>
						<button class="button is-ghost is-fullwidth" onclick={() => (activeTab = 'photos')}>
							<span class="icon is-small"><i class="fas fa-images"></i></span>
							<span>Property Photos</span>
						</button>
					</li>
				</ul>
			</div>

			<div class="box has-background-white shadow-soft" style="border-top-left-radius: 0;">
				{#if successMessage}
					<div transition:fade class="notification is-success is-light mb-5 has-text-weight-medium">
						{successMessage}
					</div>
				{/if}
				{#if error}
					<div transition:fade class="notification is-danger is-light mb-5 has-text-weight-medium">
						{error}
					</div>
				{/if}

				{#if activeTab === 'general'}
					<div class="animate-fade">
						<div class="columns">
							<div class="column is-12">
								<h3 class="title is-5 has-text-black">Basic Details</h3>
								<div class="field">
									<label class="label has-text-black" for="propName">Property Name</label>
									<input
										id="propName"
										class="input has-text-black has-background-white"
										type="text"
										bind:value={formData.name}
									/>
								</div>
								<div class="field">
									<label class="label has-text-black" for="propDesc">Description</label>
									<textarea
										id="propDesc"
										class="textarea has-text-black has-background-white"
										rows="4"
										bind:value={formData.description}
									></textarea>
								</div>
								<h3 class="title is-5 has-text-black mt-5">Location</h3>
								<div class="field">
									<label class="label has-text-black" for="propAddr">Address</label>
									<input
										id="propAddr"
										class="input has-text-black has-background-white"
										type="text"
										bind:value={formData.address}
									/>
								</div>
								<div class="columns">
									<div class="column">
										<label class="label has-text-black" for="propCity">City</label>
										<input
											id="propCity"
											class="input has-text-black has-background-white"
											type="text"
											bind:value={formData.city}
										/>
									</div>
									<div class="column">
										<label class="label has-text-black" for="propCountry">Country</label>
										<input
											id="propCountry"
											class="input has-text-black has-background-white"
											type="text"
											bind:value={formData.country}
										/>
									</div>
								</div>
							</div>
						</div>
						<hr class="dropdown-divider" />
						<div class="has-text-right">
							<button
								class="button is-primary has-text-weight-bold shadow-sm {isSaving
									? 'is-loading'
									: ''}"
								onclick={() => handleUpdate('General Info')}>Save General Info</button
							>
						</div>
					</div>
				{:else if activeTab === 'amenities'}
					<div class="animate-fade">
						<div class="columns">
							<div class="column is-6">
								<h3 class="title is-5 has-text-black">Catalog Services</h3>
								<div
									class="box has-background-white-ter is-shadowless border-light p-4"
									style="max-height: 600px; overflow-y: auto;"
								>
									{#each propertyAmenityCatalog as amenity}
										<div
											class="field mb-3 p-3 has-background-white border-light shadow-sm"
											style="border-radius: 6px;"
										>
											<label class="checkbox is-flex is-align-items-center mb-2">
												<input
													type="checkbox"
													checked={isPropAmenitySelected(amenity.id)}
													onchange={() => togglePropAmenity(amenity.id)}
													class="mr-2"
													style="transform: scale(1.2);"
												/>
												<span class="icon is-small has-text-grey mr-2"
													><i
														class="fas {getAmenityIcon(amenity.name, amenity.category, 'property')}"
													></i></span
												>
												<span class="has-text-grey-darker has-text-weight-bold">{amenity.name}</span
												>
											</label>
											{#if isPropAmenitySelected(amenity.id)}
												{@const idx = formData.amenities.findIndex((a) => a.id === amenity.id)}
												<div class="control">
													<input
														class="input is-small has-text-black has-background-white"
														type="text"
														placeholder="Details"
														bind:value={formData.amenities[idx].custom_description}
													/>
												</div>
											{/if}
										</div>
									{/each}
								</div>
							</div>
							<div class="column is-6">
								<h3 class="title is-5 has-text-black">Custom Services</h3>
								{#if existingCustomAmenities.length > 0}
									<div class="box has-background-white-ter is-shadowless border-light p-4 mb-5">
										<h6 class="heading has-text-grey-dark mb-3 has-text-weight-bold">
											Active Custom Services
										</h6>
										{#each existingCustomAmenities as amenity}
											<div
												class="field mb-3 p-3 has-background-white border-light shadow-sm"
												style="border-radius: 6px;"
											>
												<label class="checkbox is-flex is-align-items-center mb-2">
													<input
														type="checkbox"
														checked={isPropAmenitySelected(amenity.id)}
														onchange={() => togglePropAmenity(amenity.id)}
														class="mr-2"
														style="transform: scale(1.2);"
													/>
													<span class="icon is-small has-text-grey mr-2"
														><i
															class="fas {getAmenityIcon(
																amenity.name,
																amenity.category,
																'property'
															)}"
														></i></span
													>
													<span class="has-text-black has-text-weight-bold">{amenity.name}</span>
													<span class="tag is-info is-light is-rounded is-small ml-2">Custom</span>
												</label>
												{#if isPropAmenitySelected(amenity.id)}
													{@const idx = formData.amenities.findIndex((a) => a.id === amenity.id)}
													<div class="control">
														<input
															class="input is-small has-text-black has-background-white"
															type="text"
															placeholder="Details"
															bind:value={formData.amenities[idx].custom_description}
														/>
													</div>
												{/if}
											</div>
										{/each}
									</div>
								{/if}
								<div class="box has-background-white border-light shadow-sm p-5">
									<h6 class="heading has-text-grey-dark mb-3 has-text-weight-bold">
										Create New Service
									</h6>
									<div class="field">
										<label class="label is-small has-text-black" for="custAmName">Name</label><input
											id="custAmName"
											class="input has-text-black has-background-white mb-2"
											type="text"
											placeholder="e.g. Helipad"
											bind:value={tempNewAmenity.name}
										/>
									</div>
									<div class="field">
										<label class="label is-small has-text-black" for="custAmCat">Category</label>
										<div class="select is-fullwidth mb-2">
											<select
												id="custAmCat"
												class="has-text-black has-background-white"
												bind:value={tempNewAmenity.category}
												>{#each AMENITY_CATEGORIES as category}<option value={category}
														>{category}</option
													>{/each}</select
											>
										</div>
									</div>
									<div class="field">
										<label class="label is-small has-text-black" for="custAmDesc">Description</label
										><input
											id="custAmDesc"
											class="input has-text-black has-background-white mb-4"
											type="text"
											placeholder="Details"
											bind:value={tempNewAmenity.description}
										/>
									</div>
									<button
										class="button is-info has-text-weight-bold is-fullwidth shadow-sm"
										onclick={addCustomAmenityToForm}
										disabled={!tempNewAmenity.name}
										><span class="icon is-small"><i class="fas fa-plus"></i></span><span
											>Add to List</span
										></button
									>
									{#if formData.new_amenities && formData.new_amenities.length > 0}
										<div class="tags mt-4">
											{#each formData.new_amenities as item, i}<span class="tag is-info is-medium"
													>{item.name}<button
														aria-label="remove-{item.name}"
														class="delete is-small"
														onclick={() => removeCustomAmenityFromForm(i)}
													></button></span
												>{/each}
										</div>
									{/if}
								</div>
							</div>
						</div>
						<hr class="dropdown-divider" />
						<div class="has-text-right">
							<button
								class="button is-primary has-text-weight-bold shadow-sm {isSaving
									? 'is-loading'
									: ''}"
								onclick={() => handleUpdate('Amenities')}>Save Amenities</button
							>
						</div>
					</div>
				{:else if activeTab === 'rooms'}
					<div class="animate-fade">
						<div class="level mb-5">
							<div class="level-left">
								<div>
									<h3 class="title is-5 has-text-black">Manage Rooms</h3>
									<p class="subtitle is-6 has-text-grey-dark">
										Add, edit or organize your inventory.
									</p>
								</div>
							</div>
							<div class="level-right">
								<button
									class="button is-info shadow-sm has-text-weight-bold"
									onclick={openAddRoomModal}
								>
									<span class="icon"><i class="fas fa-plus"></i></span><span>Add Room</span>
								</button>
							</div>
						</div>

						{#if rooms.length > 0}
							<div class="tabs is-toggle is-rounded mb-5 room-filters">
								<ul>
									<li class={roomFilter === 'ALL' ? 'is-active tab-all' : ''}>
										<button onclick={() => (roomFilter = 'ALL')}>
											<span>All</span>
											<span class="tag is-rounded ml-2">
												{rooms.length}
											</span>
										</button>
									</li>

									<li class={roomFilter === 'SINGLE' ? 'is-active tab-single' : ''}>
										<button onclick={() => (roomFilter = 'SINGLE')}>
											<span>Single</span>
											<span class="tag is-rounded ml-2">
												{rooms.filter((r) => r.type === 'SINGLE').length}
											</span>
										</button>
									</li>

									<li class={roomFilter === 'DOUBLE' ? 'is-active tab-double' : ''}>
										<button onclick={() => (roomFilter = 'DOUBLE')}>
											<span>Double</span>
											<span class="tag is-rounded ml-2">
												{rooms.filter((r) => r.type === 'DOUBLE').length}
											</span>
										</button>
									</li>

									<li class={roomFilter === 'SUITE' ? 'is-active tab-suite' : ''}>
										<button onclick={() => (roomFilter = 'SUITE')}>
											<span>Suite</span>
											<span class="tag is-rounded ml-2">
												{rooms.filter((r) => r.type === 'SUITE').length}
											</span>
										</button>
									</li>
								</ul>
							</div>
						{/if}

						{#if displayedRooms.length === 0}
							<div class="notification is-light has-text-centered border-light py-6">
								<span class="icon is-large has-text-grey-light mb-2"
									><i class="fas fa-bed fa-2x"></i></span
								>
								<p class="has-text-grey-dark">
									{rooms.length === 0 ? 'No rooms added yet.' : 'No rooms found for this category.'}
								</p>
							</div>
						{:else}
							<div class="room-list">
								{#each displayedRooms as room (room.id)}
									<div
										class="room-card {getRoomTypeClass(room.type)}"
										transition:fade={{ duration: 200 }}
									>
										<div class="room-card-header">
											<div class="header-left">
												<h4 class="room-type-title">{room.type}</h4>

												<div class="header-meta-row">
													<div class="meta-badge price-tag">
														<span class="currency">€</span>
														<span class="amount">{room.price}</span>
														<span class="period">/ night</span>
													</div>
													<div class="meta-divider"></div>
													<div class="meta-badge capacity-tag">
														<i class="fas fa-user-friends"></i>
														<span>{room.capacity} {room.capacity === 1 ? 'Guest' : 'Guests'}</span>
													</div>
												</div>
											</div>

											<div class="header-right">
												<div class="room-actions">
													<button
														class="action-btn btn-edit"
														onclick={() => openEditRoomModal(room, 'details')}
														title="Edit room details"
													>
														<i class="fas fa-pen"></i>
													</button>
													<button
														class="action-btn btn-delete"
														onclick={() => deleteRoom(room.id)}
														title="Delete room"
													>
														<i class="fas fa-trash-alt"></i>
													</button>
												</div>
											</div>

											<div class="header-bg-pattern"></div>
										</div>

										{#if room.description}
											<p class="room-description">{room.description}</p>
										{/if}

										{#if room.media && room.media.length > 0}
											<div class="room-gallery">
												<button
													class="gallery-main"
													onclick={() => openEditRoomModal(room, 'photos')}
													aria-label="View all room photos"
												>
													<img
														src={room.media[0].storage_path}
														alt={room.type}
														class="gallery-main-img"
													/>
													<div class="gallery-overlay">
														<i class="fas fa-search-plus"></i>
														<span>View all photos</span>
													</div>
												</button>
												{#if room.media.length > 1}
													<div class="gallery-grid">
														{#each room.media.slice(1, 4) as media, idx}
															<button
																class="gallery-thumb"
																onclick={() => openEditRoomModal(room, 'photos')}
																aria-label="View room photos"
															>
																<img src={media.storage_path} alt={`${room.type} - ${idx + 2}`} />
																{#if idx === 2 && room.media.length > 4}
																	<div class="gallery-more">
																		<span>+{room.media.length - 4}</span>
																	</div>
																{/if}
															</button>
														{/each}
													</div>
												{/if}
											</div>
										{:else}
											<div class="room-no-photos">
												<div class="no-photos-content">
													<i class="fas fa-camera"></i>
													<p>No photos yet</p>
													<button
														class="button is-small is-primary is-light"
														onclick={() => openEditRoomModal(room, 'photos')}
													>
														<span>Upload Photos</span>
													</button>
												</div>
											</div>
										{/if}

										{#if room.amenities && room.amenities.length > 0}
											<div class="room-amenities">
												<h5 class="amenities-title">
													<i class="fas fa-sparkles"></i> Room Amenities
												</h5>
												<div class="amenities-grid-modern">
													{#each room.amenities as amenity}
														{@const desc = getAmenityDesc(amenity)}
														<div class="amenity-chip-modern {desc ? 'has-tooltip' : ''}">
															<i
																class="fas {getAmenityIcon(amenity.name, amenity.category, 'room')}"
															></i>
															<span>{amenity.name}</span>
															{#if desc}<div class="tooltip-content">{desc}</div>{/if}
														</div>
													{/each}
												</div>
											</div>
										{/if}
									</div>
								{/each}
							</div>
						{/if}
					</div>
				{:else if activeTab === 'photos'}
					<div class="animate-fade">
						<div class="level mb-4">
							<div class="level-left">
								<h3 class="title is-5 has-text-black mb-0">Photo Gallery</h3>
							</div>
							<div class="level-right">
								<span class="tag is-info is-light"
									>Total photos: {property.media ? property.media.length : 0}</span
								>
							</div>
						</div>

						{#if property.media && property.media.length > 0}
							<div class="columns is-multiline is-mobile mb-5">
								{#each property.media as media}
									<div class="column is-3-desktop is-4-tablet is-6-mobile">
										<div
											class="card shadow-sm border-light"
											style="border-radius: 8px; overflow: hidden;"
										>
											<div class="card-image">
												<figure class="image is-4by3" style="position: relative;">
													<img src={media.storage_path} alt="Property" style="object-fit: cover;" />
													<div
														style="position: absolute; top:0; right:0; width: 100%; height: 40px; background: linear-gradient(to bottom, rgba(0,0,0,0.3), transparent);"
													></div>
													<button
														aria-label="Delete photo"
														class="delete is-medium hover-effect"
														style="position: absolute; top: 8px; right: 8px; background-color: rgba(255, 56, 96, 0.9);"
														onclick={() => deletePhoto(media.id)}
													></button>
												</figure>
											</div>
										</div>
									</div>
								{/each}
							</div>
						{:else}
							<div class="notification is-light has-text-centered border-light mb-5">
								<span class="icon is-large has-text-grey-light"
									><i class="fas fa-images fa-2x"></i></span
								>
								<p class="has-text-grey mt-2">No photos uploaded for this property yet.</p>
							</div>
						{/if}

						<hr class="dropdown-divider mb-5" />
						<h3 class="title is-5 has-text-black mb-4">Upload New Photos</h3>
						<div class="file is-boxed is-primary is-centered has-text-centered mb-5">
							<label class="file-label" style="width: 100%;">
								<input
									class="file-input"
									type="file"
									multiple
									accept="image/*"
									onchange={handleFileSelect}
								/>
								<span
									class="file-cta p-5 has-background-white-ter"
									style="border: 2px dashed #b5b5b5; border-radius: 8px; transition: all 0.2s;"
								>
									<span class="file-icon is-size-2 has-text-primary"
										><i class="fas fa-cloud-upload-alt"></i></span
									>
									<span
										class="file-label mt-2 has-text-grey-darker is-size-5 has-text-weight-semibold"
										>Click to select new photos</span
									>
									<span class="is-size-7 has-text-grey mt-1">Supported formats: JPG, PNG, WEBP</span
									>
								</span>
							</label>
						</div>

						{#if newPreviews.length > 0}
							<h6 class="heading has-text-grey-dark mb-3 has-text-weight-bold">Ready to Upload</h6>
							<div class="columns is-multiline is-mobile mb-4">
								{#each newPreviews as src, i}
									<div class="column is-2-desktop is-3-tablet is-4-mobile">
										<figure
											class="image is-1by1 shadow-sm"
											style="position: relative; border-radius: 6px; overflow: hidden;"
										>
											<img {src} alt="Preview" style="object-fit:cover;" />
											<button
												class="delete is-small"
												style="position: absolute; top: 5px; right: 5px; background-color: rgba(0,0,0,0.6);"
												onclick={() => removeNewFile(i)}
												aria-label="Remove photo"
											></button>
										</figure>
									</div>
								{/each}
							</div>
							<div class="field is-grouped is-grouped-centered">
								<div class="control">
									<button
										class="button is-danger is-light"
										onclick={() => {
											newFiles = [];
											newPreviews = [];
										}}
										><span class="icon is-small"><i class="fas fa-times"></i></span><span
											>Clear All</span
										></button
									>
								</div>
								<div class="control">
									<button
										class="button is-primary has-text-weight-bold shadow-sm {isSaving
											? 'is-loading'
											: ''}"
										onclick={uploadNewPhotos}
										><span class="icon is-small"><i class="fas fa-cloud-upload-alt"></i></span><span
											>Upload {newFiles.length} Files</span
										></button
									>
								</div>
							</div>
						{/if}
					</div>
				{/if}
			</div>
		{/if}
	</div>

	<div class="modal {isRoomModalOpen ? 'is-active' : ''}">
		<div
			class="modal-background"
			onclick={() => (isRoomModalOpen = false)}
			aria-hidden="true"
		></div>
		<div class="modal-card shadow-soft" style="width: 900px; max-width: 95vw;">
			<header
				class="modal-card-head has-background-white border-light pb-0"
				style="display: block;"
			>
				<div class="level is-mobile mb-2">
					<div class="level-left">
						<p class="modal-card-title has-text-black">
							{editingRoomId ? 'Edit Room' : 'Add New Room'}
						</p>
					</div>
					<div class="level-right">
						<button class="delete" aria-label="close" onclick={() => (isRoomModalOpen = false)}
						></button>
					</div>
				</div>
				<div class="tabs is-boxed is-small mb-0 mt-5">
					<ul style="">
						<li class={activeRoomTab === 'details' ? 'is-active' : ''}>
							<button onclick={() => (activeRoomTab = 'details')}>
								<span class="icon is-small"><i class="fas fa-info-circle"></i></span>
								<span>Room Details & Amenities</span>
							</button>
						</li>
						<li class={activeRoomTab === 'photos' ? 'is-active' : ''}>
							<button onclick={() => (activeRoomTab = 'photos')}>
								<span class="icon is-small"><i class="fas fa-images"></i></span>
								<span>Room Photos</span>
							</button>
						</li>
					</ul>
				</div>
			</header>
			<section class="modal-card-body has-background-white" style="border-top-left-radius: 0;">
				{#if activeRoomTab === 'details'}
					<div class="animate-fade">
						<div class="columns">
							<div class="column is-5">
								<h6 class="heading has-text-grey-dark mb-3 has-text-weight-bold">Basic Info</h6>
								<div class="field">
									<label class="label is-small has-text-black" for="rType">Type</label>
									<div class="select is-fullwidth">
										<select
											id="rType"
											class="has-text-black has-background-white"
											bind:value={newRoomData.type}
										>
											<option value="SINGLE">Single</option><option value="DOUBLE">Double</option
											><option value="SUITE">Suite</option>
										</select>
									</div>
								</div>
								<div class="columns is-mobile">
									<div class="column">
										<div class="field">
											<label class="label is-small has-text-black" for="rPrice">Price (€)</label
											><input
												id="rPrice"
												class="input has-text-black has-background-white"
												type="number"
												bind:value={newRoomData.price}
												min="0"
											/>
										</div>
									</div>
									<div class="column">
										<div class="field">
											<label class="label is-small has-text-black" for="rCap">Capacity</label><input
												id="rCap"
												class="input has-text-black has-background-white"
												type="number"
												bind:value={newRoomData.capacity}
												min="1"
											/>
										</div>
									</div>
								</div>
								<div class="field">
									<label class="label is-small has-text-black" for="rDesc">Description</label>
									<textarea
										id="rDesc"
										class="textarea has-text-black has-background-white"
										rows="5"
										bind:value={newRoomData.description}
									></textarea>
								</div>
							</div>
							<div class="column is-7" style="border-left: 1px solid #f0f0f0;">
								<h6 class="heading has-text-grey-dark mb-3 has-text-weight-bold">Room Amenities</h6>
								<div
									class="box has-background-white-ter is-shadowless border-light p-3 mb-4"
									style="max-height: 250px; overflow-y: auto;"
								>
									{#each roomAmenityCatalog as ra}
										<div
											class="field mb-2 p-2 has-background-white border-light"
											style="border-radius: 4px;"
										>
											<label class="checkbox is-flex is-align-items-center">
												<input
													type="checkbox"
													checked={isRoomAmenitySelected(ra.id)}
													onchange={() => toggleRoomAmenity(ra.id)}
													class="mr-2"
												/>
												<span class="icon is-small has-text-grey mr-2"
													><i class="fas {getAmenityIcon(ra.name, ra.category, 'room')}"></i></span
												>
												<span class="is-size-7 has-text-weight-bold has-text-black">{ra.name}</span>
											</label>
											{#if isRoomAmenitySelected(ra.id)}
												{@const idx = newRoomData.amenities.findIndex((a) => a.id === ra.id)}
												<input
													class="input is-small mt-1 has-text-black has-background-white"
													type="text"
													placeholder="Details"
													bind:value={newRoomData.amenities[idx].custom_description}
												/>
											{/if}
										</div>
									{/each}
								</div>
								{#if currentRoomCustomAmenities.length > 0}
									<div class="box has-background-white-ter is-shadowless border-light p-3 mb-4">
										<h6 class="heading has-text-grey-dark is-size-7 has-text-weight-bold mb-2">
											Active Custom Services
										</h6>
										{#each currentRoomCustomAmenities as ra}
											<div
												class="field mb-2 p-2 has-background-white border-light"
												style="border-radius: 4px;"
											>
												<label class="checkbox is-flex is-align-items-center">
													<input
														type="checkbox"
														checked={isRoomAmenitySelected(ra.id)}
														onchange={() => toggleRoomAmenity(ra.id)}
														class="mr-2"
													/>
													<span class="icon is-small has-text-grey mr-2"
														><i class="fas {getAmenityIcon(ra.name, ra.category, 'room')}"
														></i></span
													>
													<span class="is-size-7 has-text-weight-bold has-text-black"
														>{ra.name}</span
													>
													<span
														class="tag is-info is-light is-rounded is-small ml-2"
														style="font-size: 0.65rem;">Custom</span
													>
												</label>
												{#if isRoomAmenitySelected(ra.id)}
													{@const idx = newRoomData.amenities.findIndex((a) => a.id === ra.id)}
													<input
														class="input is-small mt-1 has-text-black has-background-white"
														type="text"
														placeholder="Details"
														bind:value={newRoomData.amenities[idx].custom_description}
													/>
												{/if}
											</div>
										{/each}
									</div>
								{/if}
								<div class="box has-background-white border-light shadow-sm p-3">
									<p class="is-size-7 has-text-weight-bold mb-2 has-text-black">
										Create Custom Room Amenity
									</p>
									<div class="field is-grouped">
										<div class="control is-expanded">
											<input
												class="input is-small has-text-black has-background-white"
												type="text"
												placeholder="Name"
												bind:value={tempNewRoomAmenity.name}
											/>
										</div>
										<div class="control">
											<div class="select is-small">
												<select
													class="has-text-black has-background-white"
													bind:value={tempNewRoomAmenity.category}
													>{#each AMENITY_CATEGORIES as category}<option value={category}
															>{category}</option
														>{/each}</select
												>
											</div>
										</div>
									</div>
									<div class="field has-addons">
										<div class="control is-expanded">
											<input
												class="input is-small has-text-black has-background-white"
												type="text"
												placeholder="Details"
												bind:value={tempNewRoomAmenity.description}
											/>
										</div>
										<div class="control">
											<button
												class="button is-small is-info has-text-weight-bold"
												onclick={addCustomAmenityToRoom}
												disabled={!tempNewRoomAmenity.name}>Add</button
											>
										</div>
									</div>
									{#if newRoomData.new_amenities && newRoomData.new_amenities.length > 0}
										<div class="tags mt-2">
											{#each newRoomData.new_amenities as item, i}<span class="tag is-info is-light"
													>{item.name}<button
														aria-label="Remove custom amenity"
														class="delete is-small"
														onclick={() => removeCustomAmenityFromRoom(i)}
													></button></span
												>{/each}
										</div>
									{/if}
								</div>
							</div>
						</div>
					</div>
				{:else if activeRoomTab === 'photos'}
					<div class="animate-fade">
						<div class="notification is-light is-info is-small mb-4">
							<i class="fas fa-info-circle mr-2"></i> Photos added here will be specific to this room.
						</div>
						{#if editingRoomId}
							{@const currentRoom = rooms.find((r) => r.id === editingRoomId)}
							{#if currentRoom && currentRoom.media && currentRoom.media.length > 0}
								<h6 class="heading has-text-grey-dark mb-3 has-text-weight-bold">
									Existing Photos
								</h6>
								<div class="columns is-multiline is-mobile mb-5">
									{#each currentRoom.media as media}
										<div class="column is-3-desktop is-4-tablet is-6-mobile">
											<div class="card shadow-sm border-light">
												<div class="card-image">
													<figure class="image is-4by3">
														<img src={media.storage_path} alt="Room" style="object-fit: cover;" />
													</figure>
												</div>
												<button
													aria-label="Delete photo"
													class="delete is-medium"
													style="position: absolute; top: 5px; right: 5px; background: rgba(0,0,0,0.6);"
													onclick={() => deleteRoomExistingPhoto(media.id)}
												></button>
											</div>
										</div>
									{/each}
								</div>
							{/if}
						{/if}
						<hr class="dropdown-divider" />
						<h6 class="heading has-text-grey-dark mb-3 has-text-weight-bold">Upload New Photos</h6>
						<div class="file is-boxed is-primary is-centered has-text-centered mb-5">
							<label class="file-label" style="width: 100%;">
								<input
									class="file-input"
									type="file"
									multiple
									accept="image/*"
									onchange={handleRoomFileSelect}
								/>
								<span
									class="file-cta p-5 has-background-white-ter"
									style="border: 2px dashed #b5b5b5; border-radius: 8px;"
								>
									<span class="file-icon is-size-2 has-text-primary"
										><i class="fas fa-cloud-upload-alt"></i></span
									>
									<span
										class="file-label mt-2 has-text-grey-darker is-size-5 has-text-weight-semibold"
										>Click to select photos</span
									>
								</span>
							</label>
						</div>
						{#if roomPreviews.length > 0}
							<div class="columns is-multiline is-mobile mb-4">
								{#each roomPreviews as src, i}
									<div class="column is-2">
										<figure class="image is-1by1 shadow-sm" style="position: relative;">
											<img {src} alt="Preview" style="object-fit:cover; border-radius:4px" /><button
												aria-label="Remove photo"
												class="delete is-small"
												style="position: absolute; top: 2px; right: 2px;"
												onclick={() => removeRoomNewFile(i)}
											></button>
										</figure>
									</div>
								{/each}
							</div>
						{/if}
					</div>
				{/if}
			</section>
			<footer
				class="modal-card-foot has-background-white-ter border-light"
				style="justify-content: flex-end;"
			>
				<button class="button" onclick={() => (isRoomModalOpen = false)}>Cancel</button>
				<button
					class="button is-success has-text-weight-bold shadow-sm {isSaving ? 'is-loading' : ''}"
					onclick={saveRoom}>{editingRoomId ? 'Update Room' : 'Save Room'}</button
				>
			</footer>
		</div>
	</div>
</main>

<style>
	/* UTILITIES E BASE */
	.shadow-soft {
		box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08) !important;
		border: 1px solid #e0e0e0;
		border-radius: 8px;
	}
	.shadow-sm {
		box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
		border: 1px solid #d0d0d0;
		border-radius: 6px;
	}
	.border-light {
		border: 1px solid #e0e0e0 !important;
	}
	.animate-fade {
		animation: fadeIn 0.3s ease-out;
	}

	/* INPUTS */
	.input,
	.textarea,
	.select select {
		box-shadow: inset 0 1px 2px rgba(10, 10, 10, 0.1);
		border-color: #c0c0c0;
		color: #000 !important;
	}
	.input::placeholder,
	.textarea::placeholder {
		color: #7a7a7a !important;
		opacity: 1;
	}
	.input:focus,
	.textarea:focus,
	.select select:focus {
		border-color: #00d1b2;
		box-shadow: 0 0 0 0.125em rgba(0, 209, 178, 0.25) !important;
	}

	/* TABS */
	.tabs.is-boxed li.is-active button {
		background-color: white;
		border-color: #e0e0e0;
		border-bottom-color: transparent !important;
		color: #00d1b2;
	}
	.tabs.is-boxed button {
		border: 1px solid transparent;
		border-radius: 4px 4px 0 0;
		color: #4a4a4a;
		background: transparent;
		text-decoration: none;
	}
	.tabs.is-boxed ul {
		border-bottom-color: #e0e0e0;
		gap: 20px;
	}
	.tabs .icon:first-child {
		margin-inline-end: 0 !important;
		margin-right: 0 !important;
	}

	/* AMENITIES */
	.amenities-grid {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
	}
	.amenity-chip {
		display: inline-flex;
		align-items: center;
		gap: 0.4rem;
		padding: 0.35rem 0.65rem;
		background-color: #f1f5f9;
		border: 1px solid #e2e8f0;
		border-radius: 10px;
		font-size: 0.85rem;
		font-weight: 500;
		color: #4a5568;
		transition: all 0.2s ease;
	}

	.amenities-grid-modern {
		display: flex;
		flex-wrap: wrap;
		gap: 0.6rem;
	}
	.amenity-chip-modern {
		display: inline-flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.5rem 0.9rem;
		background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
		border: 1px solid #e2e8f0;
		border-radius: 12px;
		font-size: 0.85rem;
		font-weight: 600;
		color: #4a5568;
		transition: all 0.2s ease;
		position: relative;
	}
	.amenity-chip-modern i {
		color: #667eea;
		font-size: 0.9rem;
	}
	.amenity-chip-modern:hover {
		background: linear-gradient(135deg, #667eea25 0%, #764ba225 100%);
		border-color: #667eea;
		transform: translateY(-1px);
		box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
	}

	/* TOOLTIPS */
	.has-tooltip {
		position: relative;
		cursor: help;
		border-bottom: 2px dotted #cbd5e1;
	}
	.has-tooltip:hover {
		background-color: #e2e8f0;
	}
	.tooltip-content {
		visibility: hidden;
		opacity: 0;
		position: absolute;
		bottom: 130%;
		left: 50%;
		transform: translateX(-50%);
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
		transition:
			opacity 0.2s,
			bottom 0.2s;
		pointer-events: none;
		white-space: normal;
		line-height: 1.4;
	}
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

	/* ROOM CARD - CONTAINER */
	.room-card {
		background: white;
		border-radius: 16px;
		overflow: hidden;
		/* Bordo base un po' più spesso (2px) per far vedere bene il colore */
		border: 2px solid #eaecf0;
		margin-bottom: 2rem;
		transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
		position: relative;
	}
	.room-card:hover {
		transform: translateY(-4px);
		box-shadow: 0 12px 30px rgba(0, 0, 0, 0.1);
	}

	/* --- TEMI COLORE (Bordo Card + Gradiente Header) --- */

	/* SINGLE (Blue) */
	.room-card.type-single {
		border-color: #bfdbfe; /* Blue-200 */
	}
	.room-card.type-single:hover {
		border-color: #3b82f6;
		box-shadow: 0 12px 30px rgba(59, 130, 246, 0.15);
	}
	.room-card.type-single .room-card-header {
		background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
	}
	.room-card.type-single .btn-edit:hover {
		color: #2563eb;
	}

	/* DOUBLE (Emerald/Green - Default) */
	.room-card.type-double {
		border-color: #a7f3d0; /* Emerald-200 */
	}
	.room-card.type-double:hover {
		border-color: #059669;
		box-shadow: 0 12px 30px rgba(5, 150, 105, 0.15);
	}
	.room-card.type-double .room-card-header {
		background: linear-gradient(135deg, #059669 0%, #047857 100%);
	}
	.room-card.type-double .btn-edit:hover {
		color: #047857;
	}

	/* SUITE (Violet/Indigo) */
	.room-card.type-suite {
		border-color: #ddd6fe; /* Violet-200 */
	}
	.room-card.type-suite:hover {
		border-color: #7c3aed;
		box-shadow: 0 12px 30px rgba(124, 58, 237, 0.15);
	}
	.room-card.type-suite .room-card-header {
		background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%);
	}
	.room-card.type-suite .btn-edit:hover {
		color: #6d28d9;
	}

	
    /* SINGLE - Blue Gradient */

    .tabs.is-toggle li.is-active.tab-all button {
		background: linear-gradient(135deg, #5fce44 0%, #4dcb55 100%) !important;
		border-color: #2563eb !important;
		color: white !important;
	}

	.tabs.is-toggle li.is-active.tab-single button {
		background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
		border-color: #2563eb !important;
		color: white !important;
	}

	/* DOUBLE - Emerald Gradient */
	.tabs.is-toggle li.is-active.tab-double button {
		background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
		border-color: #047857 !important;
		color: white !important;
	}

	/* SUITE - Violet Gradient */
	.tabs.is-toggle li.is-active.tab-suite button {
		background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%) !important;
		border-color: #6d28d9 !important;
		color: white !important;
	}

	/* ROOM CARD - HEADER LAYOUT */
	.room-card-header {
		position: relative;
		padding: 1.5rem;
		color: white;
		overflow: hidden;
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	/* DECORAZIONE HEADER */
	.header-bg-pattern {
		position: absolute;
		top: 0;
		right: 0;
		bottom: 0;
		left: 0;
		background-image:
			radial-gradient(circle at 100% 0%, rgba(255, 255, 255, 0.15) 0%, transparent 25%),
			radial-gradient(circle at 0% 100%, rgba(255, 255, 255, 0.1) 0%, transparent 25%);
		pointer-events: none;
	}

	/* HEADER LEFT (Titolo + Prezzo) */
	.header-left {
		position: relative;
		z-index: 1;
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}
	.room-type-title {
		font-size: 1.6rem;
		font-weight: 800;
		margin: 0;
		color: white;
		letter-spacing: -0.02em;
		text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
		text-transform: capitalize;
		line-height: 1.2;
	}

	.header-meta-row {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		flex-wrap: wrap;
	}
	.meta-badge {
		display: inline-flex;
		align-items: center;
		color: rgba(255, 255, 255, 0.95);
	}
	.price-tag {
		background: rgba(255, 255, 255, 0.2);
		padding: 0.35rem 0.75rem;
		border-radius: 8px;
		backdrop-filter: blur(8px);
		border: 1px solid rgba(255, 255, 255, 0.15);
		font-weight: 600;
	}
	.currency {
		font-size: 0.9em;
		margin-right: 2px;
		opacity: 0.9;
	}
	.amount {
		font-size: 1.1em;
		font-weight: 800;
	}
	.period {
		font-size: 0.8em;
		opacity: 0.9;
		margin-left: 4px;
		font-weight: 400;
	}
	.capacity-tag {
		font-size: 0.95rem;
		font-weight: 500;
		opacity: 0.95;
	}
	.capacity-tag i {
		margin-right: 6px;
		opacity: 0.8;
	}
	.meta-divider {
		width: 1px;
		height: 16px;
		background: rgba(255, 255, 255, 0.4);
	}

	/* HEADER RIGHT (Bottoni) */
	.header-right {
		position: relative;
		z-index: 1;
		padding-left: 1rem;
	}
	.room-actions {
		display: flex;
		gap: 0.75rem;
		align-items: center;
	}
	.action-btn {
		width: 40px;
		height: 40px;
		border-radius: 50%;
		border: none;
		background: rgba(255, 255, 255, 0.2);
		backdrop-filter: blur(4px);
		color: white;
		display: flex;
		align-items: center;
		justify-content: center;
		cursor: pointer;
		transition: all 0.2s ease;
		font-size: 1rem;
		box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
	}
	.action-btn:hover {
		background: white;
		transform: scale(1.1);
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
	}

	.btn-delete:hover {
		color: #ef4444;
	}

	/* STILI CONTENUTO CARD (Rimasti uguali, solo ripuliti) */
	.room-description {
		padding: 1.25rem 1.5rem;
		color: #1a202c;
		line-height: 1.6;
		font-size: 1rem;
		font-weight: 400;
		border-bottom: 1px solid #f0f0f0;
	}

	.room-amenities {
		padding: 1.5rem;
		background: white;
	}
	.amenities-title {
		font-size: 1rem;
		font-weight: 700;
		color: #2d3748;
		margin-bottom: 1rem;
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}
	.amenities-title i {
		color: #f59e0b;
	}
	.amenities-grid-modern {
		display: flex;
		flex-wrap: wrap;
		gap: 0.6rem;
	}
	.amenity-chip-modern {
		display: inline-flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.5rem 0.9rem;
		background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
		border: 1px solid #e2e8f0;
		border-radius: 12px;
		font-size: 0.85rem;
		font-weight: 600;
		color: #4a5568;
		transition: all 0.2s ease;
		position: relative;
	}
	.amenity-chip-modern i {
		color: #667eea;
		font-size: 0.9rem;
	}
	.amenity-chip-modern:hover {
		background: linear-gradient(135deg, #667eea25 0%, #764ba225 100%);
		border-color: #667eea;
		transform: translateY(-1px);
		box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
	}

	/* STILI GALLERY (Rimasti uguali) */
	.room-gallery {
		padding: 1.5rem;
		display: grid;
		grid-template-columns: 2fr 1fr;
		gap: 0.75rem;
		background: #fafafa;
	}
	.gallery-main {
		position: relative;
		border-radius: 12px;
		overflow: hidden;
		cursor: pointer;
		height: 280px;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
		background: none;
		border: none;
		padding: 0;
		width: 100%;
		display: block;
	}
	.gallery-main-img {
		width: 100%;
		height: 100%;
		object-fit: cover;
		transition: transform 0.3s ease;
	}
	.gallery-main:hover .gallery-main-img {
		transform: scale(1.05);
	}
	.gallery-overlay {
		position: absolute;
		inset: 0;
		background: rgba(0, 0, 0, 0.5);
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		opacity: 0;
		transition: opacity 0.3s ease;
		color: white;
		font-weight: 600;
		gap: 0.5rem;
	}
	.gallery-main:hover .gallery-overlay {
		opacity: 1;
	}
	.gallery-overlay i {
		font-size: 2rem;
	}

	.gallery-grid {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
	}
	.gallery-thumb {
		position: relative;
		border-radius: 10px;
		overflow: hidden;
		cursor: pointer;
		height: 90px;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
		background: none;
		border: none;
		padding: 0;
		width: 100%;
		display: block;
	}
	.gallery-thumb img {
		width: 100%;
		height: 100%;
		object-fit: cover;
		transition: transform 0.3s ease;
	}
	.gallery-thumb:hover img {
		transform: scale(1.1);
	}
	.gallery-more {
		position: absolute;
		inset: 0;
		background: rgba(0, 0, 0, 0.7);
		display: flex;
		align-items: center;
		justify-content: center;
		color: white;
		font-size: 1.5rem;
		font-weight: 700;
	}

	.room-no-photos {
		padding: 3rem 1.5rem;
		background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
	}
	.no-photos-content {
		text-align: center;
		color: #64748b;
	}
	.no-photos-content i {
		font-size: 3rem;
		margin-bottom: 1rem;
		opacity: 0.5;
	}
	.no-photos-content p {
		margin-bottom: 1rem;
		font-weight: 500;
	}

	/* UTILITIES E BASE (Dal vecchio blocco) */
	.shadow-soft {
		box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08) !important;
		border: 1px solid #e0e0e0;
		border-radius: 8px;
	}
	.shadow-sm {
		box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
		border: 1px solid #d0d0d0;
		border-radius: 6px;
	}
	.border-light {
		border: 1px solid #e0e0e0 !important;
	}
	.animate-fade {
		animation: fadeIn 0.3s ease-out;
	}
	.input,
	.textarea,
	.select select {
		box-shadow: inset 0 1px 2px rgba(10, 10, 10, 0.1);
		border-color: #c0c0c0;
		color: #000 !important;
	}
	.input::placeholder,
	.textarea::placeholder {
		color: #7a7a7a !important;
		opacity: 1;
	}
	.input:focus,
	.textarea:focus,
	.select select:focus {
		border-color: #00d1b2;
		box-shadow: 0 0 0 0.125em rgba(0, 209, 178, 0.25) !important;
	}
	.tabs.is-boxed li.is-active button {
		background-color: white;
		border-color: #e0e0e0;
		border-bottom-color: transparent !important;
		color: #00d1b2;
	}
	.tabs.is-boxed button {
		border: 1px solid transparent;
		border-radius: 4px 4px 0 0;
		color: #4a4a4a;
		background: transparent;
		text-decoration: none;
	}
	.tabs.is-boxed ul {
		border-bottom-color: #e0e0e0;
		gap: 20px;
	}
	.tabs .icon:first-child {
		margin-inline-end: 0 !important;
		margin-right: 0 !important;
	}
	@media (max-width: 768px) {
		.room-gallery {
			grid-template-columns: 1fr;
		}
		.gallery-main {
			height: 220px;
		}
		.gallery-grid {
			flex-direction: row;
			overflow-x: auto;
		}
		.gallery-thumb {
			min-width: 100px;
		}
		.room-card-header {
			flex-direction: column;
			align-items: flex-start;
			gap: 1rem;
		}
		.header-right {
			padding-left: 0;
			width: 100%;
			display: flex;
			justify-content: flex-end;
		}
	}

	/* ROOM FILTERS - FIX */
	.room-filters {
		margin-bottom: 2rem;
	}

	.room-filters ul {
		border-bottom: none !important;
		display: flex;
		justify-content: center;
		align-items: center;
		gap: 10px; /* Spazio tra i bottoni */
	}

	.room-filters li {
		display: inline-block; /* Evita il collasso */
		margin: 0 !important;
        
	}

	/* Stile base del bottone Filtro */
	.room-filters button {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 8px;
		padding: 8px 16px;
		background-color: white;
		border: 1px solid #e5e7eb; /* Grigio chiaro */
		border-radius: 50px; /* Pillola rotonda */
		color: #4b5563; /* Grigio scuro */
		font-weight: 500;
		font-size: 0.9rem;
		cursor: pointer;
		transition: all 0.2s ease;
		box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
	}

	/* Hover */
	.room-filters button:hover {
		background-color: #f9fafb;
		border-color: #d1d5db;
		color: #111827;
		transform: translateY(-1px);
	}

	/* STATO ATTIVO (Selezionato) */
	.room-filters li.is-active button {
		background-color: #059669 !important; /* Verde Smeraldo */
		border-color: #059669 !important;
		color: white !important;
		box-shadow: 0 4px 6px rgba(5, 150, 105, 0.2);
	}

	/* Badge numerico dentro il bottone */
	.room-filters .tag {
		background-color: rgba(0, 0, 0, 0.08);
		color: inherit; /* Prende il colore del testo del bottone */
		font-weight: 700;
		height: 1.5em;
		padding-left: 0.6em;
		padding-right: 0.6em;
		border-radius: 999px;
	}

	/* Badge quando il bottone è attivo */
	.room-filters li.is-active .tag {
		background-color: rgba(255, 255, 255, 0.2);
		color: white;
	}
</style>
