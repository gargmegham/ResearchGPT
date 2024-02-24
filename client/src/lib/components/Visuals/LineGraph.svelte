<script lang="ts">
	import { onMount } from 'svelte';

	export let x,
		y,
		title = '',
		x_label = '',
		y_label = '',
		left = 20,
		multiple: boolean | Array<string> = false,
		height = false,
		logScale = false;

	let div: HTMLElement;

	onMount(() => {
		let data = [];

		if (multiple && Array.isArray(x)) {
			x.forEach((xl, i) => {
				let trace = {
					x: x[i],
					y: y[i],
					line: {},
					name: multiple[i],
					mode: 'lines+markers'
				};
				//trace.marker.color = barColors(x);
				data.push(trace);
			});
		} else {
			let trace = {
				x: x,
				y: y,
				marker: {},
				mode: 'lines+markers'
			};
			//trace.marker.color = barColors(trace.y);
			data.push(trace);
		}

		// Plotly Layout Options
		let layout: {
			title: { text: string; pad?: number };
			xaxis: { title: string; type?: string; autorange?: boolean };
			yaxis: { title: string };
			margin: { l: number; r: number; pad: number };
			showlegend?: boolean;
			legend?: { xanchor: string; yanchor: string; x: number; y: number };
			height?: number | boolean;
			hovermode?: string;
		} = {
			title: {
				text: title
			},
			xaxis: {
				title: x_label
			},
			yaxis: {
				title: y_label
			},
			margin: {
				l: left,
				r: 20,
				pad: 5
			}
		};

		if (multiple) {
			layout.showlegend = true;
			layout.legend = {
				xanchor: 'center',
				yanchor: 'top',
				x: 0.2,
				y: -0.2
			};
			layout.height = 600;
			layout.hovermode = 'closest';
		}

		if (height) {
			layout.height = height;
		}

		if (logScale) {
			layout.xaxis.type = 'log';
			layout.xaxis.autorange = true;
		}

		// Plotly Config Options
		let config = {
			responsive: true,
			displayModeBar: true
		};

		// Init Plotly
		let plotly_plot = Plotly.plot(div, data, layout, config);
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
