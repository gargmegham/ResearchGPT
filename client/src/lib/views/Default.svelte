<script lang="ts">
	export let query: String, wiki: String, active: Boolean;
</script>

<h2 class="text-center text-3xl font-bold text-neutral-400">ResearchGPT</h2>

{#if active && wiki}
	<div class="clearfix pt-visual-card">
		<h3 class="my-8">{query}</h3>
		<div>{@html wiki}</div>
		<p class="my-8 text-sm"><em>Provided by Wikipedia</em></p>
	</div>
{:else}
	<div class="clearfix pt-visual-card">
		<h3 class="my-8">{query}</h3>
		<p class="my-8 text-sm">No results found</p>
	</div>
{/if}
