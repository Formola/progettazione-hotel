<script lang="ts">
    import { auth } from '$lib/auth.svelte';
    import { propertyApi } from '$lib/api/propertyApi';
    import { goto } from '$app/navigation';
    import type { PropertyData, PropertyStatus } from '$lib/types';

    let properties = $state<PropertyData[]>([]);
    let isLoading = $state(true);
    let error = $state<string | null>(null);

    // Gestione Spinner
    let actionInProgress = $state<string | null>(null);

    let totalRooms = $derived(properties.reduce((sum, p) => sum + (p.rooms?.length || 0), 0));

    $effect(() => {
        if (!auth.isAuthenticated) {
            goto('/');
            return;
        }
        loadData();
    });

    async function loadData() {
        try {
            isLoading = true;
            properties = await propertyApi.getMyProperties();
        } catch (e) {
            error = 'Failed to load properties.';
            console.error(e);
        } finally {
            isLoading = false;
        }
    }

    // --- DELETE ---
    async function handleDelete(id: string) {
        if (!confirm('Are you sure? This cannot be undone.')) return;

        try {
            actionInProgress = id;
            await propertyApi.deleteProperty(id);
            properties = properties.filter((p) => p.id !== id);
        } catch (e) {
            console.error(e);
            alert('Error deleting property');
        } finally {
            actionInProgress = null;
        }
    }

    // --- CHANGE STATUS ---
    async function handleChangeStatus(property: PropertyData, newStatus: PropertyStatus) {
        if (property.status === newStatus) return;

        try {
            actionInProgress = property.id;
            let updatedProperty: PropertyData;

            if (newStatus === 'PUBLISHED') {
                updatedProperty = await propertyApi.publishProperty(property.id);
            } else if (newStatus === 'DRAFT') {
                updatedProperty = await propertyApi.unpublishProperty(property.id);
            } else if (newStatus === 'INACTIVE') {
                updatedProperty = await propertyApi.archiveProperty(property.id);
            } else {
                throw new Error('Stato non gestito');
            }

            properties = properties.map((p) => (p.id === property.id ? updatedProperty : p));
        } catch (e: any) {
            console.error(e);
            const msg = e.response?.data?.detail || 'Status change failed';
            alert(msg);
        } finally {
            actionInProgress = null;
        }
    }
</script>

<main class="section has-background-white-bis" style="min-height: 100vh;">
    <div class="container is-max-desktop">
        <div class="level mb-6">
            <div class="level-left">
                <div>
                    <h1 class="title is-2 has-text-black has-text-weight-bold">Your Properties</h1>
                    <p class="subtitle is-6 has-text-grey-darker">Manage your listings</p>
                </div>
            </div>
            <div class="level-right">
                <button
                    class="button is-primary is-medium has-text-weight-bold is-rounded"
                    onclick={() => goto('/owner/add-property')}
                >
                    + Add New Property
                </button>
            </div>
        </div>

        {#if isLoading}
            <div class="has-text-centered py-6">
                <button class="button is-loading is-ghost is-large">Loading</button>
            </div>
        {:else if error}
            <div class="notification is-danger is-light">{error}</div>
        {:else}
            <div class="columns mb-6">
                <div class="column">
                    <div class="box p-5 has-background-white shadow-soft">
                        <p class="heading has-text-grey-darker has-text-weight-bold">Total Properties</p>
                        <p class="title is-2 has-text-black">{properties.length}</p>
                    </div>
                </div>
                <div class="column">
                    <div class="box p-5 has-background-white shadow-soft">
                        <p class="heading has-text-grey-darker has-text-weight-bold">Total Rooms</p>
                        <p class="title is-2 has-text-black">{totalRooms}</p>
                    </div>
                </div>
            </div>

            <div class="box p-0 shadow-soft table-container-framed">
                <table class="table is-fullwidth is-hoverable is-bordered is-striped mb-0 is-vcentered">
                    <thead>
                        <tr class="has-background-dark">
                            <th class="has-text-white p-4">Name</th>
                            <th class="has-text-white p-4">Location</th>
                            <th class="has-text-white p-4 has-text-centered">Rooms</th>
                            <th class="has-text-white p-4 has-text-centered">Current Status</th>
                            <th class="has-text-white p-4 has-text-centered">Change Status</th>
                            <th class="has-text-white p-4 has-text-right">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {#each properties as property}
                            <tr class="has-background-white">
                                <td class="p-4 has-text-weight-bold has-text-black">
                                    {property.name}
                                </td>
                                
                                <td class="p-4 has-text-black">{property.city}, {property.country}</td>
                                
                                <td class="p-4 has-text-black has-text-centered">
                                    <span class="tag is-light is-rounded">{property.rooms?.length || 0}</span>
                                </td>

                                <td class="p-4 has-text-centered">
                                    <span
                                        class="tag is-rounded has-text-weight-bold
                                        {property.status === 'PUBLISHED'
                                            ? 'is-success is-light'
                                            : property.status === 'DRAFT'
                                                ? 'is-warning is-light'
                                                : 'is-danger is-light'}"
                                    >
                                        {property.status}
                                    </span>
                                </td>

                                <td class="p-4 has-text-centered">
                                    <div class="buttons are-small is-centered">
                                        
                                        {#if property.status === 'PUBLISHED'}
                                            <button
                                                class="button is-warning is-light"
                                                onclick={() => handleChangeStatus(property, 'DRAFT')}
                                                disabled={actionInProgress === property.id}
                                                title="Unpublish listing"
                                            >
                                                <span class="icon is-small"><i class="fas fa-pencil-alt"></i></span>
                                                <span>Set Draft</span>
                                            </button>

                                        {:else if property.status === 'DRAFT'}
                                            <button
                                                class="button is-success is-light"
                                                onclick={() => handleChangeStatus(property, 'PUBLISHED')}
                                                disabled={actionInProgress === property.id}
                                                title="Publish listing"
                                            >
                                                <span class="icon is-small"><i class="fas fa-upload"></i></span>
                                                <span>Publish</span>
                                            </button>

                                        {:else if property.status === 'INACTIVE'}
                                            <button
                                                class="button is-info is-light"
                                                onclick={() => handleChangeStatus(property, 'DRAFT')}
                                                disabled={actionInProgress === property.id}
                                                title="Restore to Draft"
                                            >
                                                <span class="icon is-small"><i class="fas fa-undo"></i></span>
                                                <span>Restore Draft</span>
                                            </button>
                                        {/if}

                                        {#if property.status !== 'INACTIVE'}
                                            <button
                                                class="button is-danger is-light"
                                                style="border: 1px solid #dbdbdb;"
                                                onclick={() => handleChangeStatus(property, 'INACTIVE')}
                                                disabled={actionInProgress === property.id}
                                                title="Archive property"
                                            >
                                                <span class="icon is-small"><i class="fas fa-archive"></i></span>
                                                <span>Archive</span>
                                            </button>
                                        {/if}

                                    </div>
                                </td>

                                <td class="p-4 has-text-right">
                                    <div class="buttons is-right are-small">
                                        <button
                                            class="button is-info is-light"
                                            onclick={() => goto(`/owner/edit-property/${property.id}`)}
                                            disabled={actionInProgress === property.id}
                                        >
                                            <span class="icon is-small"><i class="fas fa-edit"></i></span>
                                            <span>Edit</span>
                                        </button>

                                        <button
                                            class="button is-danger is-light"
                                            onclick={() => handleDelete(property.id)}
                                            disabled={actionInProgress === property.id}
                                        >
                                            <span class="icon is-small"><i class="fas fa-trash"></i></span>
                                            <span>Delete</span>
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        {:else}
                            <tr>
                                <td colspan="6" class="p-6 has-text-centered has-text-grey">
                                    No properties found.
                                </td>
                            </tr>
                        {/each}
                    </tbody>
                </table>
            </div>
        {/if}
    </div>
</main>

<style>
    .shadow-soft {
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.05) !important;
        border: none; 
    }

    .table-container-framed {
        border: 2px solid #363636; 
        border-radius: 8px;
        overflow: hidden; 
    }

    table.is-vcentered td {
        vertical-align: middle;
    }
    :global(.title) {
        color: #000 !important;
    }
</style>