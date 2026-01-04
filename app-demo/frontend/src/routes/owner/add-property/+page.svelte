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

    // Stato Iniziale
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

    function getAmenityName(id: string): string {
        return amenityCatalog.find(a => a.id === id)?.name || 'Unknown Service';
    }

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
            formData.amenities = [...formData.amenities, { id: amenityId, custom_description: '' }];
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
            formData = JSON.parse(JSON.stringify(initialFormData));
            selectedFiles = [];
            previews = [];
            tempNewAmenity = { name: '', category: AMENITY_CATEGORIES[0], description: '' };
            currentStep = 1;
            error = null;
        }
    }

    async function handleSubmit() {
        let createdPropertyId: string | null = null;
        try {
            isLoading = true;
            error = null;

            // 1. Create Property
            loadingMessage = 'Creating property listing...';
            const createdProperty = await propertyApi.createProperty(formData);
            createdPropertyId = createdProperty.id;

            // 2. Upload Media
            if (selectedFiles.length > 0) {
                for (let i = 0; i < selectedFiles.length; i++) {
                    const file = selectedFiles[i];
                    loadingMessage = `Uploading photo ${i + 1} of ${selectedFiles.length}...`;

                    try {
                        const fullBase64 = await mediaApi.fileToBase64(file);
                        const cleanBase64 = fullBase64.includes(',') ? fullBase64.split(',')[1] : fullBase64;
                        
                        const mediaPayload: MediaInput = {
                            fileName: file.name,
                            fileType: file.type as MediaType,
                            base64Data: cleanBase64,
                            description: 'Main Gallery',
                            propertyId: createdPropertyId!
                        };
                        await mediaApi.uploadMedia(mediaPayload);
                    } catch (uploadError) {
                        console.error(`Error uploading file ${file.name}`, uploadError);
                        throw new Error(`Failed to upload image: ${file.name}`);
                    }
                }
            }
            await goto('/owner/dashboard');
        } catch (e: any) {
            console.error('Process failed:', e);
            error = e.message || e.response?.data?.detail || 'An error occurred.';
            if (createdPropertyId) {
                loadingMessage = 'Error occurred. Cleaning up...';
                try {
                    await propertyApi.deleteProperty(createdPropertyId);
                } catch (cleanupError) {
                    console.error('Failed to cleanup property.', cleanupError);
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
                class="button is-ghost pl-0 has-text-grey-darker"
                onclick={() => goto('/owner/dashboard')}
            >
                <span class="icon is-small"><i class="fas fa-arrow-left"></i></span>
                <span class="has-text-weight-medium">Back to Dashboard</span>
            </button>
            <h1 class="title is-2 has-text-black has-text-weight-bold mt-2">Add New Property</h1>
        </div>

        <div class="steps-container mb-6 box is-shadowless border-light p-5 has-background-white">
            <div class="columns is-mobile has-text-centered is-variable is-1 mb-2">
                <div class="column {currentStep >= 1 ? 'has-text-primary has-text-weight-bold' : 'has-text-grey'}">
                    <span class="is-size-7 is-uppercase is-block mb-1">Step 1</span>
                    <span class="is-size-6">Info</span>
                </div>
                <div class="column {currentStep >= 2 ? 'has-text-primary has-text-weight-bold' : 'has-text-grey'}">
                    <span class="is-size-7 is-uppercase is-block mb-1">Step 2</span>
                    <span class="is-size-6">Location</span>
                </div>
                <div class="column {currentStep >= 3 ? 'has-text-primary has-text-weight-bold' : 'has-text-grey'}">
                    <span class="is-size-7 is-uppercase is-block mb-1">Step 3</span>
                    <span class="is-size-6">Services</span>
                </div>
                <div class="column {currentStep >= 4 ? 'has-text-primary has-text-weight-bold' : 'has-text-grey'}">
                    <span class="is-size-7 is-uppercase is-block mb-1">Step 4</span>
                    <span class="is-size-6">Photos</span>
                </div>
            </div>
            <progress class="progress is-primary is-small" value={currentStep} max="4"></progress>
        </div>

        <div class="box p-6 shadow-soft has-background-white">
            {#if error}
                <div class="notification is-danger is-light mb-5 has-text-weight-medium">{error}</div>
            {/if}

            {#if currentStep === 1}
                <div class="animate-fade">
                    <h2 class="title is-4 mb-5 has-text-black">Basic Information</h2>
                    <div class="field">
                        <label class="label has-text-grey-darker" for="propertyName">Property Name</label>
                        <div class="control">
                            <input id="propertyName" class="input is-medium has-text-black has-background-white" type="text" placeholder="e.g. Grand Hotel Vista" bind:value={formData.name} />
                        </div>
                    </div>
                    <div class="field">
                        <label class="label has-text-grey-darker" for="propertyDescription">Description</label>
                        <div class="control">
                            <textarea id="propertyDescription" class="textarea has-text-black has-background-white" rows="4" placeholder="Describe your property..." bind:value={formData.description}></textarea>
                        </div>
                    </div>
                </div>

            {:else if currentStep === 2}
                <div class="animate-fade">
                    <h2 class="title is-4 mb-5 has-text-black">Location</h2>
                    <div class="field">
                        <label class="label has-text-grey-darker" for="propertyAddress">Address</label>
                        <input id="propertyAddress" class="input has-text-black has-background-white" type="text" placeholder="123 Main St" bind:value={formData.address} />
                    </div>
                    <div class="columns">
                        <div class="column">
                            <label class="label has-text-grey-darker" for="propertyCity">City</label>
                            <input id="propertyCity" class="input has-text-black has-background-white" type="text" placeholder="Rome" bind:value={formData.city} />
                        </div>
                        <div class="column">
                            <label class="label has-text-grey-darker" for="propertyCountry">Country</label>
                            <input id="propertyCountry" class="input has-text-black has-background-white" type="text" placeholder="Italy" bind:value={formData.country} />
                        </div>
                    </div>
                </div>

            {:else if currentStep === 3}
                <div class="animate-fade">
                    <h2 class="title is-4 mb-2 has-text-black">Services & Amenities</h2>
                    <p class="subtitle is-6 has-text-grey-dark mb-5">Select standard services or add your own custom features.</p>

                    <div class="mb-6">
                        <h6 class="heading has-text-grey-dark mb-3 has-text-weight-bold">Select Standard Property Amenities</h6>
                        {#if amenityCatalog.length === 0}
                            <div class="notification is-warning is-light is-small">No catalog amenities loaded.</div>
                        {:else}
                            <div class="buttons">
                                {#each amenityCatalog as amenity}
                                    <button
                                        class="button {isSelected(amenity.id) ? 'is-primary has-text-weight-bold' : 'is-white shadow-sm has-text-grey-darker'}"
                                        onclick={() => toggleCatalogAmenity(amenity.id)}
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

                    {#if formData.amenities.length > 0}
                        <div class="mb-6 animate-fade">
                            <h6 class="heading has-text-grey-dark mb-3 has-text-weight-bold">Add details to selected amenities</h6>
                            <div class="box has-background-white-ter is-shadowless border-light p-4">
                                <div class="columns is-multiline">
                                    {#each formData.amenities as selectedAmenity, i}
                                        <div class="column is-6">
                                            <div class="field">
                                                <label class="label is-small has-text-grey-darker" for={"amenity-" + selectedAmenity.id}>
                                                    {getAmenityName(selectedAmenity.id)} 
                                                    <span class="has-text-grey is-size-7 has-text-weight-normal">(Details)</span>
                                                </label>
                                                <div class="control has-icons-left">
                                                    <input 
                                                        class="input is-small has-text-black has-background-white" 
                                                        type="text" 
                                                        placeholder="e.g. Open 24/7..." 
                                                        bind:value={formData.amenities[i].custom_description}
                                                    />
                                                    <span class="icon is-small is-left has-text-grey">
                                                        <i class="fas fa-pen"></i>
                                                    </span>
                                                </div>
                                            </div>
                                        </div>
                                    {/each}
                                </div>
                            </div>
                        </div>
                    {/if}

                    <div class="mt-5">
                        <h6 class="heading has-text-grey-dark mb-3 has-text-weight-bold">Create Custom Amenity</h6>
                        
                        <div class="box has-background-white is-shadowless border-light p-4">
                            <div class="columns is-mobile is-multiline">
                                <div class="column is-4-desktop is-12-mobile">
                                    <div class="field">
                                        <label class="label is-small has-text-grey-darker" for="amenityName">Name</label>
                                        <div class="control">
                                            <input id="amenityName" class="input has-text-black has-background-white" type="text" placeholder="e.g. Helipad" bind:value={tempNewAmenity.name} />
                                        </div>
                                    </div>
                                </div>
                                <div class="column is-4-desktop is-12-mobile">
                                    <div class="field">
                                        <label class="label is-small has-text-grey-darker" for="amenityCategory">Category</label>
                                        <div class="control">
                                            <div class="select is-fullwidth">
                                                <select id="amenityCategory" class="has-text-black has-background-white" bind:value={tempNewAmenity.category}>
                                                    {#each AMENITY_CATEGORIES as category}
                                                        <option value={category}>{category}</option>
                                                    {/each}
                                                </select>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div class="column is-4-desktop is-12-mobile">
                                    <div class="field">
                                        <label class="label is-small has-text-grey-darker" for="amenityDescription">Description</label>
                                        <div class="control">
                                            <input id="amenityDescription" class="input has-text-black has-background-white" type="text" placeholder="e.g. Private access" bind:value={tempNewAmenity.description} />
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="has-text-right">
                                <button class="button is-info is-small" onclick={addCustomAmenity} disabled={!tempNewAmenity.name}>
                                    <span class="icon is-small"><i class="fas fa-plus"></i></span>
                                    <span>Add to List</span>
                                </button>
                            </div>
                        </div>

                        {#if formData.new_amenities && formData.new_amenities.length > 0}
                            <div class="tags are-medium mt-3">
                                {#each formData.new_amenities as item, i}
                                    <span class="tag is-info is-light is-flex is-align-items-center" style="border: 1px solid #3e8ed0;">
                                        <span class="has-text-weight-bold has-text-black">{item.name}</span>
                                        {#if item.description}
                                            <span class="has-text-grey-dark ml-2">- {item.description}</span>
                                        {/if}
                                        <button class="delete is-small ml-2" onclick={() => removeCustomAmenity(i)} aria-label="Remove amenity"></button>
                                    </span>
                                {/each}
                            </div>
                        {/if}
                    </div>
                </div>

            {:else if currentStep === 4}
                <div class="animate-fade">
                    <h2 class="title is-4 mb-2 has-text-black">Property Photos</h2>
                    <p class="subtitle is-6 has-text-grey-dark mb-5">
                        Add some photos now. You can add room-specific photos later.
                    </p>
                    <div class="file is-boxed is-primary is-centered has-text-centered mb-5">
                        <label class="file-label" style="width: 100%;">
                            <input
                                class="file-input"
                                type="file"
                                multiple
                                accept="image/png, image/jpeg, image/webp, video/mp4"
                                onchange={handleFileSelect}
                            />
                            <span class="file-cta p-6 has-background-white-ter" style="border: 2px dashed #b5b5b5; border-radius: 8px;">
                                <span class="file-icon is-size-1 has-text-primary">
                                    <i class="fas fa-cloud-upload-alt"></i>
                                </span>
                                <span class="file-label mt-2 has-text-grey-darker is-size-5 has-text-weight-semibold">
                                    Click to select photos
                                </span>
                                <span class="is-size-6 has-text-grey-dark mt-1">or drag and drop them here</span>
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
                                            class="delete is-medium"
                                            aria-label="Remove photo"
                                            style="position: absolute; top: 5px; right: 5px; background-color: rgba(0,0,0,0.6);"
                                            onclick={() => removeFile(i)}
                                        ></button>
                                    </div>
                                </div>
                            {/each}
                        </div>
                    {/if}
                </div>
            {/if}

            <div class="level mt-6 pt-5" style="border-top: 1px solid #e0e0e0;">
                <div class="level-left">
                    <div class="buttons">
                        <button class="button is-ghost has-text-grey-dark" onclick={() => goto('/owner/dashboard')}>
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
                            <button class="button is-white border-light has-text-grey-darker has-text-weight-medium" onclick={prevStep} disabled={isLoading}>
                                Back
                            </button>
                        {/if}

                        {#if currentStep < 4}
                            <button
                                class="button is-primary has-text-weight-bold shadow-sm"
                                onclick={nextStep}
                                disabled={currentStep === 1 && !formData.name}
                            >
                                Next Step
                            </button>
                        {:else}
                            <button
                                class="button is-success has-text-weight-bold shadow-sm {isLoading ? 'is-loading' : ''}"
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
        border: 1px solid #877676d6 !important;
    }
    .animate-fade {
        animation: fadeIn 0.4s ease-in-out;
    }
    .input, .textarea, .select select {
        box-shadow: inset 0 1px 2px rgba(10, 10, 10, 0.1);
        border-color: #c0c0c0;
        color: #000 !important;
    }
    .input:focus, .textarea:focus, .select select:focus {
        border-color: #00d1b2;
        box-shadow: 0 0 0 0.125em rgba(0, 209, 178, 0.25) !important;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(5px); }
        to { opacity: 1; transform: translateY(0); }
    }
</style>