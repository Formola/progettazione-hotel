<script lang="ts">
	import favicon from '$lib/assets/favicon.svg';
	import 'bulma/css/bulma.css';

	let { children } = $props();

	// 1. STATO DEL MENU
	// Usiamo $state per tenere traccia se il menu è aperto (true) o chiuso (false)
	let isMenuOpen = $state(false);

	// 2. FUNZIONE TOGGLE
	// Inverte lo stato quando clicchi sulle tre lineette
	function toggleMenu() {
		isMenuOpen = !isMenuOpen;
	}
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<title>HotelManager Demo</title>
</svelte:head>

<nav class="navbar is-white has-shadow" aria-label="main navigation">
	<div class="container">
		<div class="navbar-brand">
        <a class="navbar-item" href="/">
            <span class="is-size-2 mr-2">🏨</span>
            
            <div style="display: flex; flex-direction: column; justify-content: center; line-height: 1.1;">
                <span class="has-text-weight-bold has-text-grey-darker is-size-5">HotelManager</span>
            </div>
        </a>

			<button
				type="button"
				class="navbar-burger"
				aria-label="menu"
				aria-expanded={isMenuOpen}
				class:is-active={isMenuOpen}
				onclick={toggleMenu}
				onkeydown={(e) => e.key === 'Enter' && toggleMenu()}
			>
				<span aria-hidden="true"></span>
				<span aria-hidden="true"></span>
				<span aria-hidden="true"></span>
				<span aria-hidden="true"></span>
			</button>
		</div>

		<div class="navbar-menu" class:is-active={isMenuOpen}>
			<div class="navbar-end">
				<a class="navbar-item" href="/">Home</a>

				<div class="navbar-item is-hidden-touch">
					<span style="border-left: 1px solid #ddd; height: 20px;"></span>
				</div>

				<div class="navbar-item">
					<div class="buttons">
						<a class="button is-dark is-outlined" href="/owner/dashboard">
							<strong>Start hosting your Property </strong>
						</a>
					</div>
				</div>
			</div>
		</div>
	</div>
</nav>

{@render children()}
