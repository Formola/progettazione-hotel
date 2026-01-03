<script lang="ts">
	import { onMount } from 'svelte';
	import { auth } from '$lib/auth.svelte';
	import { goto } from '$app/navigation';
	import { propertyApi } from '$lib/api/propertyApi';
	import { mediaApi } from '$lib/api/mediaApi';
	import {
		type PropertyInput,
		type NewAmenityInput,
		type MediaInput,
		type PropertyAmenity,
		AMENITY_CATEGORIES,

		type MediaType

	} from '$lib/types';

	let currentStep = $state(1);
	let isLoading = $state(false);
	let loadingMessage = $state('');
	let error = $state<string | null>(null);

	// Stato Iniziale (per reset)
	const initialFormData = {
		name: '',
		description: '',
		address: '',
		city: '',
		country: '',
		amenities: [],
		new_amenities: [],
		media_ids: []
	};

	// Dati del Form
	let formData = $state<PropertyInput>({ ...initialFormData });

	let amenityCatalog = $state<PropertyAmenity[]>([]);

	let tempNewAmenity = $state<NewAmenityInput>({
		name: '',
		category: AMENITY_CATEGORIES[0],
		description: ''
	});

	let selectedFiles = $state<File[]>([]);
	let previews = $state<string[]>([]);

	$effect(() => {
		if (!auth.isAuthenticated) goto('/');
	});

	onMount(async () => {
		try {
			amenityCatalog = await propertyApi.getAmenityCatalog();
		} catch (e) {
			console.error('Failed to load amenities:', e);
			error = 'Could not load amenities catalog.';
		}
	});

	function handleFileSelect(event: Event) {
		const input = event.target as HTMLInputElement;
		if (input.files) {
			const newFiles = Array.from(input.files);
			selectedFiles = [...selectedFiles, ...newFiles];

			newFiles.forEach((file) => {
				const reader = new FileReader();
				reader.onload = (e) => {
					if (e.target?.result) previews = [...previews, e.target.result as string];
				};
				reader.readAsDataURL(file);
			});
		}
	}

	function removeFile(index: number) {
		selectedFiles = selectedFiles.filter((_, i) => i !== index);
		previews = previews.filter((_, i) => i !== index);
	}

	function toggleCatalogAmenity(amenityId: string) {
		const index = formData.amenities.findIndex((a) => a.id === amenityId);
		if (index >= 0) {
			formData.amenities = formData.amenities.filter((a) => a.id !== amenityId);
		} else {
			formData.amenities = [...formData.amenities, { id: amenityId }];
		}
	}

	function isSelected(amenityId: string) {
		return formData.amenities.some((a) => a.id === amenityId);
	}

	function addCustomAmenity() {
		if (!tempNewAmenity.name.trim()) return;
		formData.new_amenities = [...(formData.new_amenities || []), { ...tempNewAmenity }];
		tempNewAmenity = { name: '', category: AMENITY_CATEGORIES[0], description: '' };
	}

	function removeCustomAmenity(index: number) {
		formData.new_amenities = formData.new_amenities?.filter((_, i) => i !== index);
	}

	function nextStep() {
		if (currentStep < 4) currentStep++;
	}
	function prevStep() {
		if (currentStep > 1) currentStep--;
	}

	function handleClear() {
		if (confirm('Are you sure you want to clear all fields? This action cannot be undone.')) {
			// Reset profondo clonando l'oggetto iniziale
			formData = JSON.parse(JSON.stringify(initialFormData));
			selectedFiles = [];
			previews = [];
			tempNewAmenity = { name: '', category: AMENITY_CATEGORIES[0], description: '' };
			currentStep = 1;
			error = null;
		}
	}

	async function handleSubmit() {
		// Variabile per tracciare l'ID creato in caso serva cancellarlo
		let createdPropertyId: string | null = null;

		try {
			isLoading = true;
			error = null;

			// CREAZIONE PROPRIETÀ
			loadingMessage = 'Creating property listing...';
			const createdProperty = await propertyApi.createProperty(formData);

			// Salviamo l'ID appena creato
			createdPropertyId = createdProperty.id;

			// UPLOAD MEDIA
			if (selectedFiles.length > 0) {
				for (let i = 0; i < selectedFiles.length; i++) {
					const file = selectedFiles[i];
					loadingMessage = `Uploading photo ${i + 1} of ${selectedFiles.length}...`;

					try {
						const fullBase64 = await mediaApi.fileToBase64(file);
						const cleanBase64 = fullBase64.includes(',') ? fullBase64.split(',')[1] : fullBase64;

                        // SEMPLIFICATO: Passiamo direttamente il mime type del browser
                        // (es: "image/png", "image/jpeg", "video/mp4")
                        const mediaPayload: MediaInput = {
                            fileName: file.name,
                            fileType: file.type as MediaType, // Cast diretto
                            base64Data: cleanBase64,
                            description: 'Main Gallery',
                            propertyId: createdPropertyId!
                        };
						await mediaApi.uploadMedia(mediaPayload);
					} catch (uploadError) {
						console.error(`Error uploading file ${file.name}`, uploadError);
						// Rilanciamo l'errore per attivare il catch principale e il rollback
						throw new Error(`Failed to upload image: ${file.name}`);
					}
				}
			}

			// Tutto ok -> Redirect
			await goto('/owner/dashboard');
		} catch (e: any) {
			console.error('Process failed:', e);
			error = e.message || e.response?.data?.detail || 'An error occurred.';

			// --- ROLLBACK (COMPENSATING TRANSACTION) ---
			// Se abbiamo creato la proprietà ma qualcosa dopo è fallito, la cancelliamo.
			if (createdPropertyId) {
				loadingMessage = 'Error occurred. Cleaning up...';
				try {
					await propertyApi.deleteProperty(createdPropertyId);
					console.log('Cleanup successful: property deleted.');
				} catch (cleanupError) {
					console.error('Critical: Failed to cleanup property after error.', cleanupError);
				}
			}
		} finally {
			isLoading = false;
		}
	}
</script>

<main class="section has-background-white-bis" style="min-height: 100vh;">
	<div class="container is-max-desktop">
		<div class="mb-6">
			<button
				class="button is-ghost pl-0 has-text-grey-dark"
				onclick={() => goto('/owner/dashboard')}
			>
				← Back to Dashboard
			</button>
			<h1 class="title is-2 has-text-black has-text-weight-bold">Add New Property</h1>
		</div>

		<div class="steps-container mb-6 box p-4">
			<div class="columns is-mobile has-text-centered is-variable is-1">
				<div
					class="column {currentStep >= 1
						? 'has-text-primary has-text-weight-bold'
						: 'has-text-grey-light'}"
				>
					1. Info
				</div>
				<div
					class="column {currentStep >= 2
						? 'has-text-primary has-text-weight-bold'
						: 'has-text-grey-light'}"
				>
					2. Location
				</div>
				<div
					class="column {currentStep >= 3
						? 'has-text-primary has-text-weight-bold'
						: 'has-text-grey-light'}"
				>
					3. Services
				</div>
				<div
					class="column {currentStep >= 4
						? 'has-text-primary has-text-weight-bold'
						: 'has-text-grey-light'}"
				>
					4. Photos
				</div>
			</div>
			<progress class="progress is-primary is-small" value={currentStep} max="4"></progress>
		</div>

		<div class="box p-6 shadow-soft has-background-white">
			{#if error}
				<div class="notification is-danger is-light mb-5">{error}</div>
			{/if}

			{#if currentStep === 1}
				<div class="animate-fade">
					<h2 class="title is-4 mb-5 has-text-black">Basic Information</h2>
					<div class="field">
						<label class="label has-text-grey-dark" for="propertyName">Property Name</label>
						<div class="control">
							<input
								id="propertyName"
								class="input is-medium"
								type="text"
								placeholder="e.g. Grand Hotel Vista"
								bind:value={formData.name}
							/>
						</div>
					</div>
					<div class="field">
						<label class="label has-text-grey-dark" for="propertyDescription">Description</label>
						<div class="control">
							<textarea
								id="propertyDescription"
								class="textarea"
								rows="4"
								placeholder="Describe your property..."
								bind:value={formData.description}
							></textarea>
						</div>
					</div>
				</div>
			{:else if currentStep === 2}
				<div class="animate-fade">
					<h2 class="title is-4 mb-5 has-text-black">Location</h2>
					<div class="field">
						<label class="label has-text-grey-dark" for="propertyAddress">Address</label>
						<input
							id="propertyAddress"
							class="input"
							type="text"
							placeholder="123 Main St"
							bind:value={formData.address}
						/>
					</div>
					<div class="columns">
						<div class="column">
							<label class="label has-text-grey-dark" for="propertyCity">City</label>
							<input
								id="propertyCity"
								class="input"
								type="text"
								placeholder="Rome"
								bind:value={formData.city}
							/>
						</div>
						<div class="column">
							<label class="label has-text-grey-dark" for="propertyCountry">Country</label>
							<input
								id="propertyCountry"
								class="input"
								type="text"
								placeholder="Italy"
								bind:value={formData.country}
							/>
						</div>
					</div>
				</div>
			{:else if currentStep === 3}
				<div class="animate-fade">
					<h2 class="title is-4 mb-5 has-text-black">Amenities</h2>
					<div class="mb-6">
						<h6 class="heading has-text-grey mb-3 has-text-weight-bold">Popular Amenities</h6>
						{#if amenityCatalog.length === 0}
							<div class="notification is-warning is-light is-small">
								No catalog amenities loaded.
							</div>
						{:else}
							<div class="buttons">
								{#each amenityCatalog as amenity}
									<button
										class="button {isSelected(amenity.id) ? 'is-primary' : 'is-white shadow-sm'}"
										onclick={() => toggleCatalogAmenity(amenity.id)}
										title={amenity.description || ''}
									>
										<span>{amenity.name}</span>
										{#if isSelected(amenity.id)}
											<span class="icon is-small ml-2"><i class="fas fa-check"></i></span>
										{/if}
									</button>
								{/each}
							</div>
						{/if}
					</div>
					<hr class="dropdown-divider" />
					<div class="mt-5">
						<h6 class="heading has-text-grey mb-3 has-text-weight-bold">Add Custom Amenity</h6>
						<div class="box has-background-white-ter is-shadowless border-light p-4">
							<div class="columns is-mobile is-multiline">
								<div class="column is-7-desktop is-12-mobile">
									<div class="field">
										<label class="label is-small has-text-grey" for="amenityName">Name</label>
										<div class="control">
											<input
												id="amenityName"
												class="input"
												type="text"
												placeholder="e.g. Private Beach Access"
												bind:value={tempNewAmenity.name}
											/>
										</div>
									</div>
								</div>
								<div class="column is-5-desktop is-12-mobile">
									<div class="field">
										<label class="label is-small has-text-grey" for="amenityCategory"
											>Category</label
										>
										<div class="control">
											<div class="select is-fullwidth">
												<select id="amenityCategory" bind:value={tempNewAmenity.category}>
													{#each AMENITY_CATEGORIES as category}
														<option value={category}>{category}</option>
													{/each}
												</select>
											</div>
										</div>
									</div>
								</div>
								<div class="column is-12">
									<div class="field">
										<label class="label is-small has-text-grey" for="amenityDescription"
											>Description <span class="has-text-grey-light is-italic">(Optional)</span
											></label
										>
										<div class="control">
											<input
												id="amenityDescription"
												class="input"
												type="text"
												placeholder="Short description..."
												bind:value={tempNewAmenity.description}
											/>
										</div>
									</div>
								</div>
							</div>
							<div class="has-text-right">
								<button
									class="button is-info is-small"
									onclick={addCustomAmenity}
									disabled={!tempNewAmenity.name}
								>
									<span class="icon is-small"><i class="fas fa-plus"></i></span>
									<span>Add Amenity</span>
								</button>
							</div>
						</div>
						{#if formData.new_amenities && formData.new_amenities.length > 0}
							<div class="tags are-medium mt-3">
								{#each formData.new_amenities as item, i}
									<span
										class="tag is-info is-light is-flex is-align-items-center"
										title={item.description || 'No description provided'}
									>
										<span>{item.name}</span>
										<span class="has-text-grey ml-2" style="line-height: 1;">({item.category})</span
										>
										<button
											class="delete is-small ml-2"
											onclick={() => removeCustomAmenity(i)}
											aria-label="Remove amenity"
										></button>
									</span>
								{/each}
							</div>
						{/if}
					</div>
				</div>
			{:else if currentStep === 4}
				<div class="animate-fade">
					<h2 class="title is-4 mb-2 has-text-black">Property Photos</h2>
					<p class="subtitle is-6 has-text-grey mb-5">
						Add some photos now. You can add room-specific photos later.
					</p>
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
								class="file-cta p-6 has-background-white-ter"
								style="border: 2px dashed #dbdbdb;"
							>
								<span class="file-icon is-size-1">📸</span>
								<span class="file-label mt-2 has-text-grey-dark">Click to select photos</span>
							</span>
						</label>
					</div>
					{#if previews.length > 0}
						<div class="columns is-multiline is-mobile">
							{#each previews as src, i}
								<div class="column is-one-quarter-desktop is-half-mobile">
									<div class="card shadow-sm">
										<div class="card-image">
											<figure class="image is-4by3">
												<img {src} alt="Preview" style="object-fit: cover; border-radius: 4px;" />
											</figure>
										</div>
										<button
											class="delete is-small"
											aria-label="Remove photo"
											style="position: absolute; top: 5px; right: 5px;"
											onclick={() => removeFile(i)}
										></button>
									</div>
								</div>
							{/each}
						</div>
					{/if}
				</div>
			{/if}

			<div class="level mt-6 pt-5" style="border-top: 1px solid #eee;">
				<div class="level-left">
					<div class="buttons">
						<button class="button is-ghost has-text-grey" onclick={() => goto('/owner/dashboard')}>
							Cancel
						</button>
						<button class="button is-ghost has-text-danger" onclick={handleClear}>
							Clear Form
						</button>
					</div>
				</div>

				<div class="level-right">
					<div class="buttons">
						{#if currentStep > 1}
							<button class="button is-medium" onclick={prevStep} disabled={isLoading}>
								Back
							</button>
						{/if}

						{#if currentStep < 4}
							<button
								class="button is-primary is-medium"
								onclick={nextStep}
								disabled={currentStep === 1 && !formData.name}
							>
								Next Step
							</button>
						{:else}
							<button
								class="button is-success is-medium {isLoading ? 'is-loading' : ''}"
								onclick={handleSubmit}
							>
								{#if isLoading}
									{loadingMessage}
								{:else}
									Create Property
								{/if}
							</button>
						{/if}
					</div>
				</div>
			</div>
		</div>
	</div>
</main>

<style>
	.shadow-soft {
		box-shadow: 0 8px 20px rgba(0, 0, 0, 0.05) !important;
		border: 1px solid #f0f0f0;
	}
	.shadow-sm {
		box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
		border: 1px solid #dbdbdb;
	}
	.animate-fade {
		animation: fadeIn 0.4s ease-in-out;
	}
	.border-light {
		border: 1px solid #ededed;
	}
	@keyframes fadeIn {
		from {
			opacity: 0;
			transform: translateY(5px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}
</style>
