<script lang="ts">
	import { onMount } from 'svelte';

	export let data: {
		topic_count_graph?: any;
		umap_topic_graph?: any;
		umap_article_graph?: any;
	} = {};

	let articles_per_topic_graph, umap_topic_graph, umap_article_graph;

	let umap_points = {},
		umap_trace = {};

	onMount(() => {
		getCharts();
	});

	function getCharts() {
		//Get Total Number of Articles Per Topic Data
		let art_per_topic_figure = data.topic_count_graph;

		//Sort By num
		art_per_topic_figure.sort((a, b) =>
			a.num < b.num ? 1 : a.num === b.num ? (a.labels < b.labels ? 1 : -1) : -1
		);

		let xl = [];
		let yl = [];
		let topics = [];

		//create arrays of x and y coords
		art_per_topic_figure.forEach((fig) => {
			yl.push(fig.labels.substring(fig.labels.indexOf(':') + 1));
			xl.push(fig.num);
			topics.push(fig.topic);
		});

		yl = yl.reverse();
		xl = xl.reverse();
		topics = topics.reverse();

		let art_per_topic_trace = {
			x: xl,
			y: yl,
			marker: {
				color: barColors(topics)
			},
			type: 'bar',
			orientation: 'h',
			textangle: 90
		};

		let art_per_topic_layout = {
			title: {
				text: 'Total number of articles per topic'
			},
			xaxis: {
				title: 'number of articles'
			},
			yaxis: {},
			margin: {
				l: 400,
				r: 20,
				pad: 5
			}
		};

		//Make an object that ties colors to topic id
		let colorIndex = art_per_topic_trace.marker.color.map((c, index) => ({
			color: c,
			topic: topics[index]
		}));

		const config = {
			responsive: true,
			displayModeBar: true
		};

		Plotly.plot(articles_per_topic_graph, [art_per_topic_trace], art_per_topic_layout, config);

		//NOW WE DO THE SCATTER PLOT
		let umap_figure = data.umap_topic_graph;

		//Sort results
		umap_figure.sort((a, b) => parseFloat(a.topic) - parseFloat(b.topic));

		//Get all x and y points plus tooltip text with line breaks
		umap_points = {
			xl: umap_figure.map((fig) => fig.X1),
			yl: umap_figure.map((fig) => fig.X2),
			topics: umap_figure.map((fig) => fig.topic),
			txt: umap_figure.map((fig) =>
				fig.labels
					.split(/((?:\w+ ){5})/g)
					.filter(Boolean)
					.join(`</br>`)
			),
			size: umap_figure.map((fig) => fig.n)
		};

		umap_trace = {
			x: umap_points.xl,
			y: umap_points.yl,
			mode: 'markers+text',
			type: 'scatter',
			text: umap_points.topics,
			customdata: umap_points.txt,
			name: 'Topics',
			hovertemplate: '%{customdata}<extra></extra>',
			textposition: 'right center',
			marker: {
				size: umap_points.size
			},
			showlegend: false
		};

		//Go to colorIndex and get the right color for each topic
		umap_trace.marker.color = umap_points.topics.map((topic) => {
			let colorObj = colorIndex.find((t) => `${t.topic}` == topic);
			if (colorObj) {
				return colorObj.color;
			} else {
				return '#000000';
			}
		});

		let umap_layout = {
			xaxis: {
				title: 'dimension 1'
			},
			yaxis: {
				title: 'dimension 2'
			},
			title: 'Clustering of topics',
			hovermode: 'closest',
			legend: {
				x: 0,
				y: -1
			}
		};

		Plotly.plot(umap_topic_graph, [umap_trace], umap_layout, config);

		//THE OTHER SCATTER PLOT

		let article_umap_figure = data.umap_article_graph;

		//Sort results
		article_umap_figure.sort((a, b) => parseFloat(a.V1) - parseFloat(b.V1));

		//Get all x and y points plus tooltip text with line breaks
		let article_umap_points = {
			xl: article_umap_figure.map((fig) => fig.V1),
			yl: article_umap_figure.map((fig) => fig.V2),
			topics: article_umap_figure.map((fig) => fig.topic),
			txt: article_umap_figure.map((fig) => {
				if (typeof fig.title === 'undefined') {
					return '';
				}
				return fig.title
					.split(/((?:\w+ ){5})/g)
					.filter(Boolean)
					.join(`</br>`);
			})
		};

		let article_umap_trace = {
			x: article_umap_points.xl,
			y: article_umap_points.yl,
			mode: 'markers',
			type: 'scatter',
			text: article_umap_points.txt,
			textposition: 'top center',
			marker: {
				size: 12
			}
		};

		//Go to colorIndex and get the right color for each topic
		article_umap_trace.marker.color = article_umap_points.topics.map((topic, index) => {
			let colorObj = colorIndex.find((t) => {
				return `${t.topic}` == topic;
			});

			if (typeof colorObj != 'undefined') {
				return colorObj.color;
			} else {
				return '#FF0000';
			}
		});

		let article_umap_layout = {
			xaxis: {
				title: 'dimension 1'
				//hoverformat: ''
			},
			yaxis: {
				title: 'dimension 2'
				//hoverformat: ''
			},
			title: 'Clustering of topics',
			hovermode: 'closest'
		};

		Plotly.plot(umap_article_graph, [article_umap_trace], article_umap_layout, config);
	}

	function barColors(yArr) {
		// let colors = [
		// 	"#0B78D0",
		// 	"#62A9E3",
		// 	"#075492",
		// 	"#F9A825",
		// 	"#FBC266",
		// 	"#C8871E",
		// 	"#30BFBA",
		// 	"#8BDFDC",
		// 	"#269995",
		// 	"#30C08B",
		// ];
		//clown jazz

		let colors = [
			'#2F4858',
			'#325082',
			'#2f0cc4',
			'#006abf',
			'#1db4f6',
			'#0cc49f',
			'#42e1c6',
			'#148471',
			'#1d1d35',
			'#6D4B9A',
			'#760cc4',
			'#B62A8F',
			'#e57ae8',
			'#EE005F',
			'#ff9696',
			'#FF0000',
			'#ffc396',
			'#e18042',
			'#ffc800',
			'#f9f871',
			'#f6ff96',
			'#9bde7e',
			'#4bbc8e',
			'#56f71b',
			'#3d8743'
		];

		const count = colors.length;
		const chunkSize = yArr.length >= count ? Math.floor(yArr.length / count) : 1;
		let iSequel = 0;
		let ci = 0;

		let barColorsArr;

		barColorsArr = yArr.map((v, index) => {
			if (iSequel < chunkSize) {
				iSequel++;
			} else {
				iSequel = 0;
				ci++;
			}
			return colors[ci];
		});

		return barColorsArr;
	}

	function barColorOne(count, index) {
		let tempArr = Array.from(Array(count).keys());
		let makeColors = barColors(tempArr);
		makeColors = makeColors.reverse();
		return makeColors[index];
	}
</script>

<h2>Articles Per Topic</h2>

<p>This figure shows the number of articles per topic.</p>

<div class="chart">
	<div bind:this={articles_per_topic_graph} />
</div>

<h2>UMAP Topic Graph</h2>

<p>
	UMAP (Uniform Manifold Approximation and Projection) is a machine learning algorithm used for
	dimensionality reduction and data visualization. The algorithm takes high-dimensional data and
	reduces it to a lower-dimensional representation, while preserving the important relationships and
	structure in the data.
</p>

<p>In this figure, the size of the circle corresponds to the size of the topic.</p>

<div class="my-8">
	<div bind:this={umap_topic_graph} />

	{#if umap_trace.marker && umap_points.txt && umap_points.txt.length > 0}
		<ul class="flex flex-wrap bg-white p-4 text-sm">
			{#each umap_points.txt as txt, i}
				<li class="m-0 w-1/4 truncate p-0" title={txt}>
					<span
						class="mt-1 mr-2 inline-block h-3 w-3 rounded-full"
						style="background:{umap_trace.marker.color[i]}"
					/>
					{txt}
				</li>
			{/each}
		</ul>
	{/if}
</div>

<h2>UMAP Article Graph</h2>

<p>This figure shows how the articles are distributed according to UMAP.</p>

<div class="my-8">
	<div bind:this={umap_article_graph} />
</div>
