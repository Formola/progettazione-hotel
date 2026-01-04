<script lang="ts">
    import { page } from '$app/stores';
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import { fade } from 'svelte/transition';
    import { auth } from '$lib/auth.svelte';
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

    // Dati
    let property = $state<PropertyData | null>(null);
    let propertyAmenityCatalog = $state<PropertyAmenity[]>([]); 
    let roomAmenityCatalog = $state<RoomAmenity[]>([]); 
    let existingCustomAmenities = $state<PropertyAmenity[]>([]); 
    
    // Per Edit Room: tracciamo le amenity custom SPECIFICHE della stanza
    let currentRoomCustomAmenities = $state<RoomAmenity[]>([]); 

    let rooms = $state<RoomData[]>([]);

    // Form Update Property
    let formData = $state<PropertyInput>({
        name: '', description: '', address: '', city: '', country: '',
        amenities: [], new_amenities: [], media_ids: []
    });

    // Form Room
    let isRoomModalOpen = $state(false);
    let editingRoomId = $state<string | null>(null);
    
    let newRoomData = $state<RoomInput>({
        type: 'DOUBLE', price: 100, capacity: 2, description: '', 
        amenities: [], new_amenities: [], media_ids: [] 
    });

    // Temp Inputs
    let tempNewAmenity = $state<NewAmenityInput>({
        name: '', category: AMENITY_CATEGORIES[0], description: ''
    });
    let tempNewRoomAmenity = $state<NewAmenityInput>({
        name: '', category: AMENITY_CATEGORIES[0], description: ''
    });

    // Media
    let newFiles = $state<File[]>([]);
    let newPreviews = $state<string[]>([]);

    $effect(() => {
        if (!auth.isAuthenticated) goto('/');
    });

    onMount(async () => {
        if (!propertyId) { error = "Invalid Property ID"; return; }
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

            recalcCustomAmenities(prop, propCat);

            formData = {
                name: prop.name,
                description: prop.description || '',
                address: prop.address,
                city: prop.city,
                country: prop.country,
                amenities: prop.amenities.map(a => ({ id: a.id, custom_description: a.custom_description || '' })),
                new_amenities: [], media_ids: prop.media.map(m => m.id)
            };
        } catch (e) {
            console.error(e);
            error = 'Failed to load property details.';
        } finally {
            isLoading = false;
        }
    }

    function recalcCustomAmenities(prop: PropertyData, catalog: PropertyAmenity[]) {
        const catalogIds = new Set(catalog.map(a => a.id));
        existingCustomAmenities = prop.amenities.filter(a => !catalogIds.has(a.id));
    }

    // --- PROPERTY LOGIC ---
    function isPropAmenitySelected(id: string) { return formData.amenities.some(a => a.id === id); }
    
    function togglePropAmenity(id: string) {
        const idx = formData.amenities.findIndex(a => a.id === id);
        if (idx >= 0) formData.amenities = formData.amenities.filter(a => a.id !== id);
        else formData.amenities = [...formData.amenities, { id, custom_description: '' }];
    }

    async function handleUpdate(tabName: string) {
        try {
            isSaving = true;
            error = null; successMessage = null;
            const updated = await propertyApi.updateProperty(propertyId, formData);
            property = updated;
            recalcCustomAmenities(updated, propertyAmenityCatalog);
            
            formData.amenities = updated.amenities.map(a => ({ id: a.id, custom_description: a.custom_description || '' }));
            formData.new_amenities = []; 
            
            successMessage = `${tabName} updated successfully!`;
            setTimeout(() => successMessage = null, 3000);
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

    // --- ROOMS LOGIC ---
    function openAddRoomModal() {
        editingRoomId = null;
        currentRoomCustomAmenities = [];
        newRoomData = { type: 'DOUBLE', price: 100, capacity: 2, description: '', amenities: [], new_amenities: [], media_ids: [] };
        isRoomModalOpen = true;
    }

    function openEditRoomModal(room: RoomData) {
        editingRoomId = room.id;
        
        // Calcola amenities custom della stanza corrente per visualizzarle
        const catalogIds = new Set(roomAmenityCatalog.map(a => a.id));
        currentRoomCustomAmenities = room.amenities.filter(a => !catalogIds.has(a.id));

        newRoomData = {
            type: room.type,
            price: room.price,
            capacity: room.capacity,
            description: room.description || '',
            amenities: room.amenities.map(a => ({ id: a.id, custom_description: a.custom_description || '' })),
            new_amenities: [], 
            media_ids: room.media.map(m => m.id)
        };
        isRoomModalOpen = true;
    }

    function toggleRoomAmenity(amenityId: string) {
        const idx = newRoomData.amenities.findIndex(a => a.id === amenityId);
        if (idx >= 0) newRoomData.amenities = newRoomData.amenities.filter(a => a.id !== amenityId);
        else newRoomData.amenities = [...newRoomData.amenities, { id: amenityId, custom_description: '' }];
    }
    function isRoomAmenitySelected(amenityId: string) { return newRoomData.amenities.some(a => a.id === amenityId); }

    function addCustomAmenityToRoom() {
        if (!tempNewRoomAmenity.name.trim()) return;
        if (!newRoomData.new_amenities) newRoomData.new_amenities = [];
        newRoomData.new_amenities = [...newRoomData.new_amenities, { ...tempNewRoomAmenity }];
        tempNewRoomAmenity = { name: '', category: AMENITY_CATEGORIES[0], description: '' };
    }
    function removeCustomAmenityFromRoom(index: number) {
        if(newRoomData.new_amenities) newRoomData.new_amenities = newRoomData.new_amenities.filter((_, i) => i !== index);
    }

    function getAmenityDesc(amenity: RoomAmenity | PropertyAmenity): string | null {
        return amenity.custom_description && amenity.custom_description.trim() !== '' ? amenity.custom_description : null;
    }

    // === GESTIONE ATOMICITÀ E ROLLBACK ===
    async function saveRoom() {
        try {
            isSaving = true;
            
            if (editingRoomId) {
                // --- UPDATE FLOW ---
                
                // SNAPSHOT per Rollback: Troviamo lo stato attuale della stanza
                const originalRoom = rooms.find(r => r.id === editingRoomId);
                const newlyCreatedAmenityIds: string[] = []; // Traccia amenities create in questo ciclo

                try {
                    // Aggiornamento Base (Dati + Link Amenities esistenti)
                    let updated = await roomApi.updateRoom(editingRoomId, newRoomData);

                    // Creazione Nuove Custom Amenities (Loop)
                    if (newRoomData.new_amenities && newRoomData.new_amenities.length > 0) {
                        for (const newAm of newRoomData.new_amenities) {
                            const prevAmenities = updated.amenities; // Stato prima dell'aggiunta
                            updated = await roomApi.addAmenityToRoom(editingRoomId, newAm);
                            
                            // Troviamo l'ID della nuova amenity per eventuale rollback
                            // È l'ID che è in 'updated' ma non era in 'prevAmenities'
                            const newId = updated.amenities.find(a => !prevAmenities.some(p => p.id === a.id))?.id;
                            if (newId) newlyCreatedAmenityIds.push(newId);
                        }
                    }

                    // Se tutto ok, aggiorno la UI
                    rooms = rooms.map(r => r.id === editingRoomId ? updated : r);
                    successMessage = "Room updated successfully";
                    isRoomModalOpen = false;

                } catch (innerError) {
                    console.error("Update sequence failed. Rolling back...", innerError);
                    
                    // --- ROLLBACK PROCEDURE ---
                    
                    // Elimina le amenities create parzialmente
                    if (newlyCreatedAmenityIds.length > 0) {
                        await Promise.all(newlyCreatedAmenityIds.map(id => 
                            roomApi.removeAmenityFromRoom(editingRoomId!, id).catch(e => console.error("Rollback cleanup failed", e))
                        ));
                    }

                    // Ripristina i dati base della stanza (Se updateRoom era passato ma il loop no)
                    if (originalRoom) {
                        const revertData: RoomInput = {
                            type: originalRoom.type,
                            price: originalRoom.price,
                            capacity: originalRoom.capacity,
                            description: originalRoom.description || '',
                            amenities: originalRoom.amenities.map(a => ({ id: a.id, custom_description: a.custom_description || '' })),
                            new_amenities: [], // Non ricreiamo nulla nel rollback
                            media_ids: originalRoom.media.map(m => m.id)
                        };
                        await roomApi.updateRoom(editingRoomId, revertData);
                    }

                    throw new Error("Update failed and changes were reverted.");
                }

            } else {
                // CREATE FLOW (Atomico lato Backend di solito, ma gestiamo errori base) ---
                const created = await propertyApi.addRoomToProperty(propertyId, newRoomData);
                rooms = [...rooms, created];
                successMessage = "Room created successfully";
                isRoomModalOpen = false;
            }

            setTimeout(() => successMessage = null, 3000);

        } catch (e: any) {
            console.error(e);
            alert('Error saving room: ' + (e.message || e));
        } finally {
            isSaving = false;
        }
    }

    async function deleteRoom(roomId: string) {
        if(!confirm("Delete this room?")) return;
        try {
            await roomApi.deleteRoom(roomId);
            rooms = rooms.filter(r => r.id !== roomId);
        } catch(e) { console.error(e); alert("Failed to delete room"); }
    }

    // --- PHOTOS LOGIC ---
    function handleFileSelect(event: Event) {
        const input = event.target as HTMLInputElement;
        if (input.files) {
            const files = Array.from(input.files);
            newFiles = [...newFiles, ...files];
            files.forEach(file => {
                const reader = new FileReader();
                reader.onload = (e) => { if (e.target?.result) newPreviews = [...newPreviews, e.target.result as string]; };
                reader.readAsDataURL(file);
            });
        }
    }
    
    async function uploadNewPhotos() {
        if (newFiles.length === 0) return;
        let uploadedMediaIds: string[] = [];
        try {
            isSaving = true;
            error = null;
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
                const uploaded = await mediaApi.uploadMedia(payload);
                uploadedMediaIds.push(uploaded.id);
            }
            property = await propertyApi.getPropertyById(propertyId);
            newFiles = []; newPreviews = [];
            successMessage = 'Photos uploaded successfully!';
            setTimeout(() => successMessage = null, 3000);
        } catch (e) {
            console.error(e);
            error = 'Failed to upload photos. Reverting...';
            // Rollback per le foto
            if (uploadedMediaIds.length > 0) {
                try { await Promise.all(uploadedMediaIds.map(id => mediaApi.deleteMedia(id))); } catch (ex) { console.error(ex); }
            }
        } finally {
            isSaving = false;
        }
    }

    async function deletePhoto(mediaId: string) {
        if(!confirm("Delete this photo?")) return;
        try {
            await mediaApi.deleteMedia(mediaId);
            if (property) property.media = property.media.filter(m => m.id !== mediaId);
        } catch(e) { console.error(e); alert("Failed to delete photo"); }
    }
</script>

<main class="section has-background-white-bis" style="min-height: 100vh;">
    <div class="container is-max-desktop">
        
        <div class="mb-6 is-flex is-justify-content-space-between is-align-items-center">
            <div>
                <button class="button is-ghost pl-0 has-text-grey-darker" onclick={() => goto('/owner/dashboard')}>
                    <span class="icon is-small"><i class="fas fa-arrow-left"></i></span>
                    <span class="has-text-weight-medium">Back to Dashboard</span>
                </button>
                <h1 class="title is-2 has-text-black has-text-weight-bold mt-2">Edit Property</h1>
            </div>
            {#if property}
                <div class="tags has-addons">
                    <span class="tag is-medium is-dark">Status</span>
                    <span class="tag is-medium {property.status === 'PUBLISHED' ? 'is-success' : 'is-warning'}">
                        {property.status}
                    </span>
                </div>
            {/if}
        </div>

        {#if isLoading}
            <div class="has-text-centered p-6"><button class="button is-loading is-ghost is-large">Loading</button></div>
        {:else if !property}
            <div class="notification is-danger shadow-sm">Property not found.</div>
        {:else}

            <div class="tabs is-boxed is-medium mb-0">
                <ul>
                    <li class={activeTab === 'general' ? 'is-active' : ''}>
                        <button class="button is-ghost is-fullwidth" onclick={() => activeTab = 'general'}>
                            <span class="icon is-small"><i class="fas fa-info-circle"></i></span>
                            <span>General Info</span>
                        </button>
                    </li>
                    <li class={activeTab === 'amenities' ? 'is-active' : ''}>
                        <button class="button is-ghost is-fullwidth" onclick={() => activeTab = 'amenities'}>
                            <span class="icon is-small"><i class="fas fa-concierge-bell"></i></span>
                            <span>Amenities</span>
                        </button>
                    </li>
                    <li class={activeTab === 'rooms' ? 'is-active' : ''}>
                        <button class="button is-ghost is-fullwidth" onclick={() => activeTab = 'rooms'}>
                            <span class="icon is-small"><i class="fas fa-bed"></i></span>
                            <span>Rooms ({rooms.length})</span>
                        </button>
                    </li>
                    <li class={activeTab === 'photos' ? 'is-active' : ''}>
                        <button class="button is-ghost is-fullwidth" onclick={() => activeTab = 'photos'}>
                            <span class="icon is-small"><i class="fas fa-images"></i></span>
                            <span>Photos</span>
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
                                    <input id="propName" class="input has-text-black has-background-white" type="text" bind:value={formData.name} />
                                </div>
                                <div class="field">
                                    <label class="label has-text-black" for="propDesc">Description</label>
                                    <textarea id="propDesc" class="textarea has-text-black has-background-white" rows="4" bind:value={formData.description}></textarea>
                                </div>
                                <h3 class="title is-5 has-text-black mt-5">Location</h3>
                                <div class="field">
                                    <label class="label has-text-black" for="propAddr">Address</label>
                                    <input id="propAddr" class="input has-text-black has-background-white" type="text" bind:value={formData.address} />
                                </div>
                                <div class="columns">
                                    <div class="column">
                                        <label class="label has-text-black" for="propCity">City</label>
                                        <input id="propCity" class="input has-text-black has-background-white" type="text" bind:value={formData.city} />
                                    </div>
                                    <div class="column">
                                        <label class="label has-text-black" for="propCountry">Country</label>
                                        <input id="propCountry" class="input has-text-black has-background-white" type="text" bind:value={formData.country} />
                                    </div>
                                </div>
                            </div>
                        </div>
                        <hr class="dropdown-divider" />
                        <div class="has-text-right">
                            <button class="button is-primary has-text-weight-bold shadow-sm {isSaving ? 'is-loading' : ''}" onclick={() => handleUpdate('General Info')}>
                                Save General Info
                            </button>
                        </div>
                    </div>

                {:else if activeTab === 'amenities'}
                    <div class="animate-fade">
                        <div class="columns">
                            <div class="column is-6">
                                <h3 class="title is-5 has-text-black">Catalog Services</h3>
                                <div class="box has-background-white-ter is-shadowless border-light p-4" style="max-height: 600px; overflow-y: auto;">
                                    {#each propertyAmenityCatalog as amenity}
                                        <div class="field mb-3 p-3 has-background-white border-light shadow-sm" style="border-radius: 6px;">
                                            <label class="checkbox is-flex is-align-items-center mb-2">
                                                <input type="checkbox" checked={isPropAmenitySelected(amenity.id)} onchange={() => togglePropAmenity(amenity.id)} class="mr-2" style="transform: scale(1.2);">
                                                <span class="icon is-small has-text-grey mr-2"><i class="fas {getAmenityIcon(amenity.name, amenity.category, 'property')}"></i></span>
                                                <span class="has-text-grey-darker has-text-weight-bold">{amenity.name}</span>
                                            </label>
                                            {#if isPropAmenitySelected(amenity.id)}
                                                {@const idx = formData.amenities.findIndex(a => a.id === amenity.id)}
                                                <div class="control">
                                                    <input class="input is-small has-text-black has-background-white" type="text" placeholder="Add details (e.g. Free, 24/7)" bind:value={formData.amenities[idx].custom_description} />
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
                                        <h6 class="heading has-text-grey-dark mb-3 has-text-weight-bold">Active Custom Services</h6>
                                        {#each existingCustomAmenities as amenity}
                                            <div class="field mb-3 p-3 has-background-white border-light shadow-sm" style="border-radius: 6px;">
                                                <label class="checkbox is-flex is-align-items-center mb-2">
                                                    <input type="checkbox" checked={isPropAmenitySelected(amenity.id)} onchange={() => togglePropAmenity(amenity.id)} class="mr-2" style="transform: scale(1.2);">
                                                    <span class="icon is-small has-text-grey mr-2"><i class="fas {getAmenityIcon(amenity.name, amenity.category, 'property')}"></i></span>
                                                    <span class="has-text-black has-text-weight-bold">{amenity.name}</span>
                                                    <span class="tag is-info is-light is-rounded is-small ml-2">Custom</span>
                                                </label>
                                                {#if isPropAmenitySelected(amenity.id)}
                                                    {@const idx = formData.amenities.findIndex(a => a.id === amenity.id)}
                                                    <div class="control">
                                                        <input class="input is-small has-text-black has-background-white" type="text" placeholder="Details" bind:value={formData.amenities[idx].custom_description} />
                                                    </div>
                                                {/if}
                                            </div>
                                        {/each}
                                    </div>
                                {/if}
                                <div class="box has-background-white border-light shadow-sm p-5">
                                    <h6 class="heading has-text-grey-dark mb-3 has-text-weight-bold">Create New Service</h6>
                                    <div class="field"><label class="label is-small has-text-black" for="custAmName">Name</label><input id="custAmName" class="input has-text-black has-background-white mb-2" type="text" placeholder="e.g. Helipad" bind:value={tempNewAmenity.name} /></div>
                                    <div class="field"><label class="label is-small has-text-black" for="custAmCat">Category</label><div class="select is-fullwidth mb-2"><select id="custAmCat" class="has-text-black has-background-white" bind:value={tempNewAmenity.category}>{#each AMENITY_CATEGORIES as category}<option value={category}>{category}</option>{/each}</select></div></div>
                                    <div class="field"><label class="label is-small has-text-black" for="custAmDesc">Description</label><input id="custAmDesc" class="input has-text-black has-background-white mb-4" type="text" placeholder="Details" bind:value={tempNewAmenity.description} /></div>
                                    <button class="button is-info has-text-weight-bold is-fullwidth shadow-sm" onclick={addCustomAmenityToForm} disabled={!tempNewAmenity.name}><span class="icon is-small"><i class="fas fa-plus"></i></span><span>Add to List</span></button>
                                    {#if formData.new_amenities && formData.new_amenities.length > 0}
                                        <div class="tags mt-4">{#each formData.new_amenities as item, i}<span class="tag is-info is-medium">{item.name}<button aria-label="remove-{item.name}" class="delete is-small" onclick={() => removeCustomAmenityFromForm(i)}></button></span>{/each}</div>
                                    {/if}
                                </div>
                            </div>
                        </div>
                        <hr class="dropdown-divider" />
                        <div class="has-text-right"><button class="button is-primary has-text-weight-bold shadow-sm {isSaving ? 'is-loading' : ''}" onclick={() => handleUpdate('Amenities')}>Save Amenities</button></div>
                    </div>

                {:else if activeTab === 'rooms'}
                    <div class="animate-fade">
                        <div class="level">
                            <div class="level-left">
                                <div><h3 class="title is-5 has-text-black">Manage Rooms</h3><p class="subtitle is-6 has-text-grey-dark">Add or remove rooms.</p></div>
                            </div>
                            <div class="level-right"><button class="button is-info shadow-sm has-text-weight-bold" onclick={openAddRoomModal}><span class="icon"><i class="fas fa-plus"></i></span><span>Add Room</span></button></div>
                        </div>
                        {#if rooms.length === 0}
                            <div class="notification is-light has-text-centered border-light"><p class="has-text-grey-dark">No rooms added yet.</p></div>
                        {:else}
                            <div class="room-list">
                                {#each rooms as room}
                                    <div class="box has-background-white border-light shadow-sm mb-4">
                                        <div class="columns is-vcentered">
                                            <div class="column is-9">
                                                <div class="mb-2 is-flex is-align-items-center">
                                                    <span class="title is-5 has-text-black mr-3 mb-0">{room.type}</span>
                                                    <span class="tag is-success is-light has-text-weight-bold">€{room.price}</span>
                                                </div>
                                                <div class="mb-2">
                                                    <span class="icon-text has-text-grey-darker mr-4 is-flex is-align-items-center">
                                                        <span class="icon is-small"><i class="fas fa-user-friends"></i></span><span>Capacity: {room.capacity}</span>
                                                    </span>
                                                </div>
                                                <p class="is-size-7 has-text-grey-dark">{room.description || 'No description provided.'}</p>
                                                {#if room.amenities && room.amenities.length > 0}
                                                    <div class="amenities-grid mt-3">
                                                        {#each room.amenities as amenity}
                                                            {@const desc = getAmenityDesc(amenity)}
                                                            <div class="amenity-chip {desc ? 'has-tooltip' : ''}">
                                                                <i class="fas {getAmenityIcon(amenity.name, amenity.category, 'room')} amenity-icon"></i>
                                                                <span>{amenity.name}</span>
                                                                {#if desc}<div class="tooltip-content">{desc}</div>{/if}
                                                            </div>
                                                        {/each}
                                                    </div>
                                                {/if}
                                            </div>
                                            <div class="column is-3 has-text-right">
                                                <div class="buttons is-right">
                                                    <button class="button is-small is-info is-light" onclick={() => openEditRoomModal(room)}><span class="icon"><i class="fas fa-edit"></i></span><span>Edit</span></button>
                                                    <button class="button is-small is-danger is-light" onclick={() => deleteRoom(room.id)}><span class="icon"><i class="fas fa-trash"></i></span><span>Delete</span></button>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                {/each}
                            </div>
                        {/if}
                    </div>

                {:else if activeTab === 'photos'}
                    <div class="animate-fade">
                        <h3 class="title is-5 has-text-black">Photo Gallery</h3>
                        <div class="columns is-multiline is-mobile mb-6">
                            {#each property.media as media}
                                <div class="column is-3-desktop is-6-mobile">
                                    <div class="card shadow-sm border-light">
                                        <div class="card-image"><figure class="image is-4by3"><img src={media.storage_path} alt="Property" style="object-fit:cover; border-radius: 4px 4px 0 0;"></figure></div>
                                        <button class="delete is-medium" style="position: absolute; top: 5px; right: 5px; background: rgba(0,0,0,0.6);" onclick={() => deletePhoto(media.id)} aria-label="Delete"></button>
                                    </div>
                                </div>
                            {/each}
                        </div>
                        <hr class="dropdown-divider" />
                        <h3 class="title is-5 has-text-black mb-4">Upload New Photos</h3>
                        <div class="file is-boxed is-primary is-centered has-text-centered mb-5">
                            <label class="file-label" style="width: 100%;">
                                <input class="file-input" type="file" multiple accept="image/*" onchange={handleFileSelect} />
                                <span class="file-cta p-5 has-background-white-ter" style="border: 2px dashed #b5b5b5; border-radius: 8px;">
                                    <span class="file-icon is-size-2 has-text-primary"><i class="fas fa-cloud-upload-alt"></i></span>
                                    <span class="file-label mt-2 has-text-grey-darker is-size-5 has-text-weight-semibold">Click to select new photos</span>
                                </span>
                            </label>
                        </div>
                        {#if newPreviews.length > 0}
                            <div class="columns is-multiline is-mobile mb-4">{#each newPreviews as src}<div class="column is-2"><figure class="image is-1by1 shadow-sm"><img {src} alt="Preview" style="object-fit:cover; border-radius:4px"></figure></div>{/each}</div>
                            <div class="has-text-centered"><button class="button is-primary has-text-weight-bold shadow-sm {isSaving ? 'is-loading' : ''}" onclick={uploadNewPhotos}>Upload {newFiles.length} Files</button></div>
                        {/if}
                    </div>
                {/if}
            </div>
        {/if}
    </div>

    <div class="modal {isRoomModalOpen ? 'is-active' : ''}">
        <div class="modal-background" onclick={() => isRoomModalOpen = false} aria-hidden="true"></div>
        <div class="modal-card shadow-soft" style="width: 900px; max-width: 95vw;">
            <header class="modal-card-head has-background-white border-light">
                <p class="modal-card-title has-text-black">{editingRoomId ? 'Edit Room' : 'Add New Room'}</p>
                <button class="delete" aria-label="close" onclick={() => isRoomModalOpen = false}></button>
            </header>
            <section class="modal-card-body has-background-white">
                <div class="columns">
                    <div class="column is-5">
                        <h6 class="heading has-text-grey-dark mb-3 has-text-weight-bold">Details</h6>
                        <div class="field"><label class="label is-small has-text-black" for="rType">Type</label><div class="select is-fullwidth"><select id="rType" class="has-text-black has-background-white" bind:value={newRoomData.type}><option value="SINGLE">Single</option><option value="DOUBLE">Double</option><option value="SUITE">Suite</option></select></div></div>
                        <div class="columns is-mobile"><div class="column"><div class="field"><label class="label is-small has-text-black" for="rPrice">Price (€)</label><input id="rPrice" class="input has-text-black has-background-white" type="number" bind:value={newRoomData.price} min="0" /></div></div><div class="column"><div class="field"><label class="label is-small has-text-black" for="rCap">Capacity</label><input id="rCap" class="input has-text-black has-background-white" type="number" bind:value={newRoomData.capacity} min="1" /></div></div></div>
                        <div class="field"><label class="label is-small has-text-black" for="rDesc">Description</label><textarea id="rDesc" class="textarea has-text-black has-background-white" rows="4" bind:value={newRoomData.description}></textarea></div>
                    </div>
                    
                    <div class="column is-7" style="border-left: 1px solid #f0f0f0;">
                        <h6 class="heading has-text-grey-dark mb-3 has-text-weight-bold">Room Amenities</h6>
                        <div class="box has-background-white-ter is-shadowless border-light p-3 mb-4" style="max-height: 250px; overflow-y: auto;">
                            {#each roomAmenityCatalog as ra}
                                <div class="field mb-2 p-2 has-background-white border-light" style="border-radius: 4px;">
                                    <label class="checkbox is-flex is-align-items-center">
                                        <input type="checkbox" checked={isRoomAmenitySelected(ra.id)} onchange={() => toggleRoomAmenity(ra.id)} class="mr-2">
                                        <span class="icon is-small has-text-grey mr-2"><i class="fas {getAmenityIcon(ra.name, ra.category, 'room')}"></i></span>
                                        <span class="is-size-7 has-text-weight-bold has-text-black">{ra.name}</span>
                                    </label>
                                    {#if isRoomAmenitySelected(ra.id)}
                                        {@const idx = newRoomData.amenities.findIndex(a => a.id === ra.id)}
                                        <input class="input is-small mt-1 has-text-black has-background-white" type="text" placeholder="Details" bind:value={newRoomData.amenities[idx].custom_description} />
                                    {/if}
                                </div>
                            {/each}
                        </div>

                        {#if currentRoomCustomAmenities.length > 0}
                            <div class="box has-background-white-ter is-shadowless border-light p-3 mb-4">
                                <h6 class="heading has-text-grey-dark is-size-7 has-text-weight-bold mb-2">Active Custom Services</h6>
                                {#each currentRoomCustomAmenities as ra}
                                    <div class="field mb-2 p-2 has-background-white border-light" style="border-radius: 4px;">
                                        <label class="checkbox is-flex is-align-items-center">
                                            <input type="checkbox" checked={isRoomAmenitySelected(ra.id)} onchange={() => toggleRoomAmenity(ra.id)} class="mr-2">
                                            <span class="icon is-small has-text-grey mr-2"><i class="fas {getAmenityIcon(ra.name, ra.category, 'room')}"></i></span>
                                            <span class="is-size-7 has-text-weight-bold has-text-black">{ra.name}</span>
                                            <span class="tag is-info is-light is-rounded is-small ml-2" style="font-size: 0.65rem;">Custom</span>
                                        </label>
                                        {#if isRoomAmenitySelected(ra.id)}
                                            {@const idx = newRoomData.amenities.findIndex(a => a.id === ra.id)}
                                            <input class="input is-small mt-1 has-text-black has-background-white" type="text" placeholder="Details" bind:value={newRoomData.amenities[idx].custom_description} />
                                        {/if}
                                    </div>
                                {/each}
                            </div>
                        {/if}

                        <div class="box has-background-white border-light shadow-sm p-3">
                            <p class="is-size-7 has-text-weight-bold mb-2 has-text-black">Create Custom Room Amenity</p>
                            <div class="field is-grouped">
                                <div class="control is-expanded"><input class="input is-small has-text-black has-background-white" type="text" placeholder="Name" bind:value={tempNewRoomAmenity.name} aria-label="Name"></div>
                                <div class="control"><div class="select is-small"><select class="has-text-black has-background-white" bind:value={tempNewRoomAmenity.category} aria-label="Cat">{#each AMENITY_CATEGORIES as category}<option value={category}>{category}</option>{/each}</select></div></div>
                            </div>
                            <div class="field has-addons">
                                <div class="control is-expanded"><input class="input is-small has-text-black has-background-white" type="text" placeholder="Details" bind:value={tempNewRoomAmenity.description} aria-label="Desc"></div>
                                <div class="control"><button class="button is-small is-info has-text-weight-bold" onclick={addCustomAmenityToRoom} disabled={!tempNewRoomAmenity.name}>Add</button></div>
                            </div>
                            {#if newRoomData.new_amenities && newRoomData.new_amenities.length > 0}
                                <div class="tags mt-2">{#each newRoomData.new_amenities as item, i}<span class="tag is-info is-light">{item.name}<button class="delete is-small" onclick={() => removeCustomAmenityFromRoom(i)} aria-label="remove"></button></span>{/each}</div>
                            {/if}
                        </div>
                    </div>
                </div>
            </section>
            <footer class="modal-card-foot has-background-white-ter border-light" style="justify-content: flex-end;">
                <button class="button has-text-grey-darker" onclick={() => isRoomModalOpen = false}>Cancel</button>
                <button class="button is-success has-text-weight-bold shadow-sm {isSaving ? 'is-loading' : ''}" onclick={saveRoom}>{editingRoomId ? 'Update Room' : 'Save Room'}</button>
            </footer>
        </div>
    </div>
</main>

<style>
    .shadow-soft { box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08) !important; border: 1px solid #e0e0e0; border-radius: 8px; }
    .shadow-sm { box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1); border: 1px solid #d0d0d0; border-radius: 6px; }
    .border-light { border: 1px solid #e0e0e0 !important; }
    .animate-fade { animation: fadeIn 0.3s ease-out; }
    
    .input, .textarea, .select select { box-shadow: inset 0 1px 2px rgba(10, 10, 10, 0.1); border-color: #c0c0c0; color: #000 !important; }
    .input::placeholder, .textarea::placeholder { color: #7a7a7a !important; opacity: 1; }
    .input:focus, .textarea:focus, .select select:focus { border-color: #00d1b2; box-shadow: 0 0 0 0.125em rgba(0, 209, 178, 0.25) !important; }

    .tabs.is-boxed li.is-active button { background-color: white; border-color: #e0e0e0; border-bottom-color: transparent !important; color: #00d1b2; }
    .tabs.is-boxed button { border: 1px solid transparent; border-radius: 4px 4px 0 0; color: #4a4a4a; background: transparent; text-decoration: none; }
    .tabs.is-boxed ul { border-bottom-color: #e0e0e0; }
    
    .amenities-grid { display: flex; flex-wrap: wrap; gap: 0.5rem; }
    .amenity-chip { display: inline-flex; align-items: center; gap: 0.4rem; padding: 0.35rem 0.65rem; background-color: #f1f5f9; border: 1px solid #e2e8f0; border-radius: 10px; font-size: 0.85rem; font-weight: 500; color: #4a5568; transition: all 0.2s ease; }
    .amenity-icon { color: #64748b; }
    
    .has-tooltip { position: relative; cursor: help; border-bottom: 2px dotted #cbd5e1; }
    .has-tooltip:hover { background-color: #e2e8f0; }
    .tooltip-content { visibility: hidden; opacity: 0; position: absolute; bottom: 130%; left: 50%; transform: translateX(-50%); background-color: #475569; color: #fff; text-align: center; padding: 8px 12px; border-radius: 6px; font-size: 0.8rem; font-weight: 400; min-width: 180px; max-width: 260px; width: max-content; z-index: 100; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2); transition: opacity 0.2s, bottom 0.2s; pointer-events: none; white-space: normal; line-height: 1.4; }
    .tooltip-content::after { content: ''; position: absolute; top: 100%; left: 50%; margin-left: -5px; border-width: 5px; border-style: solid; border-color: #475569 transparent transparent transparent; }
    .has-tooltip:hover .tooltip-content { visibility: visible; opacity: 1; bottom: 140%; }

    @keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }
</style>