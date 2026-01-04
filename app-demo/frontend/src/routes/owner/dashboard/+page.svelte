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

    async function handleLogout() {
        await auth.logout();
        goto('/');
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

    async function handleChangeStatus(property: PropertyData, newStatus: PropertyStatus) {
        if (property.status === newStatus) return;

        try {
            actionInProgress = property.id;
            let updatedProperty: PropertyData;

            if (newStatus === 'PUBLISHED') {
                updatedProperty = await propertyApi.publishProperty(property.id); // set status to PUBLISHED
            } else if (newStatus === 'DRAFT') {
                updatedProperty = await propertyApi.unpublishProperty(property.id); // set status to DRAFT
            } else if (newStatus === 'INACTIVE') {
                updatedProperty = await propertyApi.archiveProperty(property.id); // set status to INACTIVE
            } else {
                throw new Error('Invalid status');
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

        <div class="owner-header mb-6">
            <div class="owner-header-left">
                <div class="owner-badge shadow-sm">
                    <i class="fas fa-building"></i>
                </div>
                <div>
                    <h1 class="owner-title">Owner Dashboard</h1>
                    <p class="owner-subtitle">Manage your properties</p>
                </div>
            </div>

            <div class="owner-header-right">
                <div class="owner-user is-hidden-mobile">
                    <span class="icon is-small has-text-grey-light mr-1"><i class="fas fa-user-circle"></i></span>
                    <span class="has-text-weight-medium">{auth.user?.email}</span>
                </div>

                <button class="button is-small is-light is-danger is-outlined ml-4" onclick={handleLogout}>
                    <span class="icon is-small"><i class="fas fa-sign-out-alt"></i></span>
                    <span>Logout</span>
                </button>
            </div>
        </div>


        <div class="level mb-6">
            <div class="level-left">
                <div>
                    <h1 class="title is-2 has-text-black has-text-weight-bold">Your Properties</h1>
                    <p class="subtitle is-6 has-text-grey-darker">Manage your listings</p>
                </div>
            </div>
            <div class="level-right">
                <button
                    class="button is-primary is-medium has-text-weight-bold is-rounded shadow-sm"
                    onclick={() => goto('/owner/add-property')}
                >
                    <span class="icon is-small"><i class="fas fa-plus"></i></span>
                    <span>Add New Property</span>
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
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05) !important;
        border: none;
        border-radius: 8px;
    }
    
    .table-container-framed {
        border: 1px solid #dbdbdb; 
        border-radius: 5px;
        overflow: hidden; 
    }

    table.is-vcentered td {
        vertical-align: middle;
    }
    :global(.title) {
        color: #000 !important;
    }


    .owner-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1.25rem 1.5rem;
        margin-bottom: 3rem;
        background: white;
        border-radius: 12px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.06);
    }

    .owner-header-left {
        display: flex;
        align-items: center;
        gap: 1rem;
    }

    .owner-badge {
        width: 48px;
        height: 48px;
        border-radius: 12px;
        background: linear-gradient(135deg, #3273dc, #2759a5);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 1.2rem;
    }

    .owner-title {
        font-size: 1.25rem;
        font-weight: 700;
        margin: 0;
        color: #111;
    }

    .owner-subtitle {
        font-size: 0.8rem;
        color: #777;
        margin-top: 0.1rem;
    }

    .owner-header-right {
        display: flex;
        align-items: center;
        gap: 1rem;
    }

    .owner-user {
        display: flex;
        align-items: center;
        gap: 0.4rem;
        font-size: 0.8rem;
        color: #666;
    }


</style>