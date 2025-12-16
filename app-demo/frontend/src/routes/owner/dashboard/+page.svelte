<script lang="ts">
    import { auth } from '$lib/auth.svelte';
    import { goto } from '$app/navigation';

    let properties = $state([
        { id: 1, name: "Grand Hotel Vista", location: "Rome", rooms: 12, status: "Active" },
        { id: 2, name: "Sea Breeze Resort", location: "Amalfi", rooms: 8, status: "Pending" }
    ]);

    // Auth Guard: se non autenticato, rimanda al login
    $effect(() => {
        console.log("Owner Dashboard Auth Guard:", auth.isAuthenticated);
        if (!auth.isAuthenticated) goto('/');
        
    });

    async function handleLogout() {
        auth.logout();
        await goto('/');
    }
</script>

<header class="has-background-dark py-3">
    <div class="container is-max-desktop px-3">
        <div class="level is-mobile">
            <div class="level-left">
                <h2 class="is-size-4 has-text-white has-text-weight-bold" style="letter-spacing: 0.5px;">
                    OWNER <span class="has-text-primary">PORTAL</span>
                </h2>
            </div>
            <div class="level-right">
                <div class="is-flex is-align-items-center">
                    <span class="has-text-grey-light is-size-7 mr-4">{auth.user?.email}</span>
                    <button class="button is-danger is-small is-outlined" onclick={handleLogout}>
                        Logout
                    </button>
                </div>
            </div>
        </div>
    </div>
</header>

<main class="section has-background-white-bis" style="min-height: 100vh;">
    <div class="container is-max-desktop">
        
        <div class="level mb-6">
            <div class="level-left">
                <div>
                    <h1 class="title is-2 has-text-black has-text-weight-bold">Your Properties</h1>
                    <p class="subtitle is-6 has-text-grey-darker">Manage and monitor your hotel listings</p>
                </div>
            </div>
            <div class="level-right">
                <button class="button is-primary is-medium has-text-weight-bold is-rounded" onclick={() => goto('/owner/add-property')}>
                    + Add New Property
                </button>
            </div>
        </div>

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
                    <p class="title is-2 has-text-black">20</p>
                </div>
            </div>
        </div>

        <div class="box p-0 is-overflow-hidden shadow-soft">
            <table class="table is-fullwidth is-hoverable mb-0">
                <thead>
                    <tr class="has-background-dark">
                        <th class="has-text-white p-4">Property Name</th>
                        <th class="has-text-white p-4">Location</th>
                        <th class="has-text-white p-4">Rooms</th>
                        <th class="has-text-white p-4">Status</th>
                        <th class="has-text-white p-4 has-text-right">Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {#each properties as property}
                        <tr class="has-background-white">
                            <td class="p-4 has-text-weight-bold has-text-black">{property.name}</td>
                            <td class="p-4 has-text-black">{property.location}</td>
                            <td class="p-4 has-text-black">{property.rooms}</td>
                            <td class="p-4">
                                <span class="tag is-rounded {property.status === 'Active' ? 'is-success is-light' : 'is-warning is-light'}">
                                    {property.status}
                                </span>
                            </td>
                            <td class="p-4 has-text-right">
                                <button class="button is-small is-dark is-outlined">Edit</button>
                            </td>
                        </tr>
                    {/each}
                </tbody>
            </table>
        </div>
    </div>
</main>

<style>
    .shadow-soft {
        box-shadow: 0 8px 20px rgba(0,0,0,0.05) !important;
        border: 1px solid #f0f0f0;
    }
    .is-overflow-hidden {
        overflow: hidden;
        border-radius: 12px;
    }
    /* Forza il contrasto massimo */
    :global(.title) {
        color: #000000 !important;
    }
    :global(.subtitle) {
        color: #4a4a4a !important;
    }
</style>