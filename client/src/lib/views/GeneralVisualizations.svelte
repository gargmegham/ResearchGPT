<script lang="ts">
	import type { Words, AllWords, General } from '$lib/types/general-visual';

	import BarGraph from '$lib/components/Visuals/BarGraph.svelte';
	import WordCloud from '$lib/components/Visuals/WordCloud.svelte';
	import VisNetwork from '$lib/components/Visuals/VisNetwork.svelte';

	export let data: General;

	// Single Word Data
	const rawFigure: Words[] = data.singlewordplot;
	// Sort array from most words to least
	const figure: Words[] = [...rawFigure].sort((a, b) =>
		a.n < b.n ? 1 : a.n === b.n ? (a.word < b.word ? 1 : -1) : -1
	);

	//  Array of objects with all the words
	const allWords: AllWords[] = figure.map((fig, index) => {
		return {
			text: fig.word,
			size: fig.n,
			index
		};
	});

	// Get the first 25 of the figure array
	const slicedFigure = [...figure].slice(0, 25);
	// Generate Graph x and y arrays
	const wo_x = slicedFigure.map(({ n }) => n).reverse();
	const wo_y = slicedFigure.map(({ word }) => word).reverse();

	// Bigram Data
	const bigRawFigure = data.bigram;
	// Sort array from most occurrances to least
	const bigFigure = [...bigRawFigure].sort((a, b) =>
		a.n < b.n ? 1 : a.n === b.n ? (a.bigram < b.bigram ? 1 : -1) : -1
	);

	// Get the first 15 of the figure array
	const slicedBigFigure = [...bigFigure].slice(0, 15);
	// Generate Graph x and y arrays
	const bigram_y = slicedBigFigure.map(({ bigram }) => bigram).reverse();
	const bigram_x = slicedBigFigure.map(({ n }) => n).reverse();

	// Network Visualization Data
	const vis_data = {
		nodes: data.nodes,
		edges: data.edges
	};

	// Network Visualization Data
	const correlation_vis_data = {
		nodes: data.correlation_nodes,
		edges: data.correlation_edges
	};
</script>

<div class="pt-visual-card">
	<h2>Important Keywords</h2>
	<p>
		The visuals on this page use the <strong>bag of words</strong> method. This involves breaking down
		a piece of text into individual words and counting the number of occurences of each word.
	</p>
	<BarGraph x={wo_x} y={wo_y} title="" label="Number of Occurances" />
</div>

<div class="mt-3 pt-visual-card">
	<h3>Word Cloud</h3>
	<p>
		A word cloud is a visual representation of text data that displays the most frequently occurring
		words in a larger font and size, while less frequent words appear in smaller fonts or are not
		displayed at all.
	</p>
	<p>
		In a word cloud, words are arranged in a random or artistic way, often with the most important
		words placed in the center or in a more prominent location. The overall effect is a "cloud" of
		words that gives an immediate visual representation of the most common words in a body of text.
	</p>
	<p>
		Word clouds are often used to summarize or highlight the main themes or ideas in a piece of
		text.
	</p>
	<WordCloud words={allWords} />
</div>

<div class="mt-3 pt-visual-card">
	<h2>Word Pairs</h2>
	<p>
		A bigram is a sequence of two adjacent words that appear together in a text. One common use of
		bigrams is to analyze the co-occurrence of words in a text and identify patterns or associations
		between them.
	</p>
	<BarGraph x={bigram_x} y={bigram_y} title="" label="Number of Occurances" left="160" />
</div>

<div class="mt-3 pt-visual-card">
	<h2>Word-Pair Network Plot</h2>
	<p>
		This visualization displays each word as a node, and the connections between the nodes represent
		the frequency of co-occurrence of the words in the text. Nodes corresponding to more frequently
		occurring words are represented by larger circles, while the thickness of the lines connecting
		the nodes reflects the strength of the relationship between the words. Additionally, the figure
		is interactive, allowing for zooming and manipulation.
	</p>
	<VisNetwork data={vis_data} />
</div>

<div class="my-3 pt-visual-card">
	<h2>Correlation Network Plot</h2>
	<p>
		A network correlation plot using the bag of words method is a visualization that shows the
		strength of the correlation between different words in a text corpus. In this plot, each word is
		represented as a node, and the edges between the nodes represent the correlation coefficient
		between the words. The strength of the correlation is indicated by the thickness of the edges or
		the weight of the connections.
	</p>
	<VisNetwork data={correlation_vis_data} type="correlation" />
</div>
