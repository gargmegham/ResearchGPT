<script lang="ts">
	import type { Author } from '$lib/types/author-info';
	import BarGraph from '$lib/components/Visuals/BarGraph.svelte';
	import LineGraph from '$lib/components/Visuals/LineGraph.svelte';
	import VisNetwork from '$lib/components/Visuals/VisNetwork.svelte';

	export let data: Author;

	// Get the author data
	const rawFigure = data.top_authors;

	// Sort array from most to least
	const figure = [...rawFigure].sort((a, b) =>
		a.n < b.n ? 1 : a.n === b.n ? (a.authors < b.authors ? 1 : -1) : -1
	);

	// Get the first 15 of the figure array
	const slicedFigure = [...figure].slice(0, 15);

	// Generate Graph x and y arrays
	const y = slicedFigure.map(({ authors }) => authors).reverse();
	const x = slicedFigure.map(({ n }) => n).reverse();

	//Top Authors by decade
	const byDecade = data.top_authors_decade;
	let decadesSorted = {};
	let decades = [];

	//rearrange the data for multiple graphs by decade
	byDecade.forEach((d) => {
		if (typeof decadesSorted[d.decade] === 'undefined') {
			decadesSorted[d.decade] = [];
		}
		decadesSorted[d.decade].push({
			decade: d.decade,
			n: d.n,
			authors: d.authors
		});
	});

	//sort the data in each decade w/ graph data
	Object.values(decadesSorted).forEach(
		(d: Array<{ decade?: number; n?: number; authors?: string }>) => {
			const figure = [...d].sort((a, b) =>
				a.n < b.n ? 1 : a.n === b.n ? (a.authors < b.authors ? 1 : -1) : -1
			);
			const slicedFigure = [...figure].slice(0, 8);

			let decade: {
				decade?: number;
				x?: number[];
				y?: string[];
			} = {};

			decade.decade = slicedFigure[0].decade;
			decade.y = slicedFigure.map(({ authors }) => authors).reverse();
			decade.x = slicedFigure.map(({ n }) => n).reverse();

			decades.push(decade);
		}
	);

	// Get the collaborators data
	const rawCollabFigure = data.total_collaborators;
	let authorCounts = {};
	let collabCount = [];

	// Make arrays to count how many collaborators each author has
	rawCollabFigure.forEach((f) => {
		if (typeof authorCounts[f.authors] === 'undefined') {
			authorCounts[f.authors] = [];
		}
		authorCounts[f.authors].push(f.collab);
	});

	Object.values(authorCounts).forEach((d: any) => {
		collabCount.push(d.length);
	});

	const counts = {};
	for (const num of collabCount) {
		counts[num] = counts[num] ? counts[num] + 1 : 1;
	}

	// Generate Graph x and y arrays
	const collab_y = Object.keys(counts);
	const collab_x = Object.values(counts);

	// Network Visualization Data
	const collaborator_vis_data = {
		nodes: data.collab_nodes,
		edges: data.collab_edges
	};
</script>

<div class="pt-visual-card">
	<h2>Top Authors</h2>
	<p>These authors have the most publications within the search parameters.</p>
	<BarGraph {x} {y} title="" label="Number of Articles" />
</div>

{#if decades.length > 1}
	<div class="mt-3 pt-visual-card">
		<h2>Top Authors by Decade</h2>
		{#each decades as decade}
			<BarGraph
				x={decade.x}
				y={decade.y}
				title={decade.decade}
				label="Number of Articles"
				height={300}
			/>
		{/each}
	</div>
{/if}

<div class="mt-3 pt-visual-card">
	<h2>Number of collaborators</h2>

	<p>
		This figure shows the number of collaborators that authors have within the search parameters.
	</p>

	<LineGraph
		x={collab_x}
		y={collab_y}
		title=""
		x_label="Number of Collaborators"
		y_label="Number of Authors"
		left={100}
		logScale={true}
	/>
</div>

<div class="mt-3 pt-visual-card">
	<h2>Collaboration Network</h2>
	<p>
		An author collaboration network graph is a visualization that shows the relationships between
		authors who have collaborated on academic publications or other research projects. This type of
		graph is created by representing each author as a node, and connecting the nodes with edges that
		represent co-authorship of publications.
	</p>
	<p>
		In an author collaboration network graph, each node represents an author, and the edges between
		the nodes represent collaborations between the authors. The strength of the collaboration can be
		indicated by the weight of the edges, which can be based on the number of co-authored
		publications.
	</p>
	<p>
		The author collaboration network graph can be useful for visualizing the patterns of
		collaboration in a research field, identifying the most prolific or influential authors, and
		detecting clusters or communities of authors who frequently collaborate with each other.
		Additionally, it can provide insights into the structure and dynamics of research networks and
		can be used to identify potential collaborators or research partners.
	</p>
	<p>Additionally, the figure is interactive, allowing for zooming and manipulation.</p>
	<VisNetwork data={collaborator_vis_data} type="collab" />
</div>
