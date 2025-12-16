<script lang="ts">
    import { page } from '$app/state';
    import { goto } from '$app/navigation';
</script>

<div class="hero is-fullheight-with-navbar has-background-white">
    <div class="hero-body">
        <div class="container has-text-centered">
            <span class="is-size-1 mb-4" style="display: block;">🔍</span>
            
            <h1 class="title is-1 has-text-black has-text-weight-bold">
                {page.status}
            </h1>
            
            <h2 class="subtitle is-4 has-text-grey-darker mb-6">
                {#if page.status === 404}
                    Oops! The page you're looking for doesn't exist.
                {:else}
                    Something went wrong on our end.
                {/if}
            </h2>

            <div class="buttons is-centered">
                <button 
                    class="button is-primary is-rounded is-medium has-text-weight-bold px-6"
                    onclick={() => goto('/')}
                >
                    Back to Home
                </button>
                <button 
                    class="button is-light is-rounded is-medium has-text-weight-bold px-6"
                    onclick={() => history.back()}
                >
                    Go Back
                </button>
            </div>
        </div>
    </div>
</div>

<style>
    /* Stile per centrare bene il contenuto se la navbar è presente */
    .hero.is-fullheight-with-navbar {
        min-height: calc(100vh - 3.25rem);
    }
</style>