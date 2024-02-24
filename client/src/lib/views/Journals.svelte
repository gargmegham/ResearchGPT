<script lang="ts">
	import type { ViewDataType } from '$lib/types/vite-env';
	import BarGraph from '$lib/components/Visuals/BarGraph.svelte';

	export let data: ViewDataType;

	// Get the data
	const rawFigure = data.journal_count;

	// Sort array from most to least
	const figure = [...rawFigure].sort((a, b) =>
		a.count < b.count ? 1 : a.count === b.count ? (a.name < b.name ? 1 : -1) : -1
	);

	// Get the first 30 of the figure array
	const slicedFigure = [...figure].slice(0, 30);

	//Dynamic height if there's less than 30...
	const height = slicedFigure.length * 25;

	// Generate Graph x and y arrays
	const y = slicedFigure.map(({ name }) => name).reverse();
	const x = slicedFigure.map(({ count }) => count).reverse();

	//Loop through names and figure out left padding...
	let maxLength = 0;
	slicedFigure.forEach((figure) => {
		if (figure.name.length > maxLength) {
			maxLength = figure.name.length;
		}
	});

	//limit the size 'cause some get really long
	if (maxLength > 54) {
		maxLength = 54;
	}

	//each character is about 7px in Plotly? todo make this better
	const left = maxLength * 7;
</script>

<div class="pt-visual-card">
	<h2>Journals</h2>
	<p>These are the journals that have published most on your search parameters.</p>
	<BarGraph {x} {y} title="" label="Number of Articles" {left} {height} />
</div>
