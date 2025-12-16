<script>
    let searchQuery = $state("");

    function handleSearch() {
        alert(`You searched for: ${searchQuery}. (Redirecting to results...)`);
    }
</script>

<div style="display: flex; flex-direction: column; min-height: calc(100vh - 3.25rem);">

    <section class="hero is-medium is-link">
      <div class="hero-body">
        <div class="container has-text-centered">
          <h1 class="title is-1 mb-6">
            Find a property for your stay
          </h1>
          
          <div class="columns is-centered">
            <div class="column is-half">
                <div class="box p-2">
                    <div class="field has-addons">
                        <div class="control is-expanded">
                            <input 
                                class="input is-medium" 
                                type="text" 
                                placeholder="Where do you want to go?"
                                bind:value={searchQuery}
                            >
                        </div>
                        <div class="control">
                            <button class="button is-primary is-medium" onclick={handleSearch}>
                                🔍 Search
                            </button>
                        </div>
                    </div>
                </div>
            </div>
          </div>

        </div>
      </div>
    </section>

<section class="section has-background-black" style="flex: 1; display: flex; align-items: center;">
        <div class="container">
            <div class="columns is-centered has-text-centered">
                
                <div class="column is-4">
                    <div class="mb-4">
                        <span class="is-size-1">🏨</span>
                    </div>
                    <h3 class="title is-4 has-text-white">Unique Properties</h3>
                    <p class="has-text-grey-light">Explore thousands of hotels managed directly by owners.</p>
                </div>

                <div class="column is-4">
                    <div class="mb-4">
                        <span class="is-size-1">🛌</span>
                    </div>
                    <h3 class="title is-4 has-text-white">Detailed Rooms</h3>
                    <p class="has-text-grey-light">Check amenities, photos, and specific room details before you go.</p>
                </div>

                <div class="column is-4">
                    <div class="mb-4">
                        <span class="is-size-1">📸</span>
                    </div>
                    <h3 class="title is-4 has-text-white">Verified Media</h3>
                    <p class="has-text-grey-light">High-quality images and media uploaded by property managers.</p>
                </div>

            </div>
        </div>
    </section>

</div> 
<section class="section has-background-light">
    <div class="container">
        <div class="columns is-vcentered">
            <div class="column is-8">
                <h2 class="title is-2 has-text-grey-darker">Are you a Property Owner?</h2>
                <p class="subtitle is-4 has-text-grey-dark">
                    List your property, manage rooms, upload media, and update amenities in real-time.
                </p>
                <p class="has-text-grey-dark">
                    Access your dedicated dashboard to have full control over your hotel assets.
                </p>
            </div>
            <div class="column is-4 has-text-centered">
                <a href="/owner/dashboard" class="button is-dark is-large is-fullwidth">
                    Manage your Property
                </a>
            </div>
        </div>
    </div>
</section>