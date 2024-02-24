<script lang="ts">
	import { onMount } from 'svelte';

	export let x: Array<any>,
		y: Array<any>,
		title = '',
		label = '',
		left = 100,
		height: boolean | number = false;

	let div: HTMLElement;

	onMount(() => {
		// Plotly Trace Option
		let trace = {
			x: x,
			y: y,
			marker: {
				color: barColors(y)
			},
			type: 'bar',
			orientation: 'h'
		};

		// Plotly Layout Options
		let layout: {
			title: { text: string; pad: number };
			xaxis: { title: string };
			margin: { l: number; r: number; pad: number };
			height?: number | boolean;
		} = {
			title: {
				text: title,
				pad: 20
			},
			xaxis: {
				title: label
			},
			margin: {
				l: left,
				r: 20,
				pad: 5
			}
		};

		if (height) {
			layout.height = height;
		}

		// Plotly Config Options
		let config = {
			responsive: true,
			displayModeBar: true
		};

		// Init Plotly
		let plotly_plot = Plotly.plot(div, [trace], layout, config);
	});

	function barColors(yArr) {
		let colors = [
			'#0B78D0',
			'#62A9E3',
			'#075492',
			'#F9A825',
			'#FBC266',
			'#C8871E',
			'#30BFBA',
			'#8BDFDC',
			'#269995',
			'#30C08B'
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

<div class="chart">
	<div bind:this={div} />
</div>
