<script lang="ts">
	import { onMount } from 'svelte';

	export let data: {
		nodes?: Array<{ id: string; label: string }>;
		edges?: Array<{ from: string; to: string }>;
	} = {};
	export let type = 'default';

	let div: HTMLElement;

	onMount(() => {
		const options = {
			autoResize: true,
			height: '800px',
			width: '100%',
			nodes: {
				shape: 'dot',
				physics: true,
				color: { background: '#FBC266', border: '#504b47' },
				scaling: { min: 6, max: 40 },
				font: { size: 24 }
			},
			manipulation: { enabled: false },
			edges: {
				smooth: false,
				color: '#504b47',
				arrows: 'to'
			},
			physics: { stabilization: true },
			interaction: {
				navigationButtons: true,
				zoomView: false
			},
			layout: { improvedLayout: true }
		};

		if (type === 'collab') {
			options.nodes = {
				shape: 'dot',
				physics: true,
				color: { background: '#14AE5C', border: '#504b47' },
				scaling: { min: 6, max: 10 },
				font: { size: 16 }
			};

			options.edges = {
				smooth: false,
				color: '#504b47',
				arrows: {
					to: false,
					from: false
				},
				width: 1,
				scaling: {
					min: 1,
					max: 1
					/*
					customScalingFunction: function (min,max,total,value) {
	  					if (max === min) {
	    					return 0.5;
	  					} else {
	    					let scale = 1 / (max - min);
	    					return Math.max(0,(value - min)*scale);
	  					}
					}
					*/
				}
			};
		}

		if (type == 'correlation') {
			options.nodes = {
				shape: 'dot',
				physics: true,
				color: { background: '#14AE5C', border: '#504b47' },
				scaling: { min: 1, max: 2 },
				font: { size: 16 }
			};

			options.edges = {
				smooth: false,
				color: '#504b47',
				arrows: {
					to: false,
					from: false
				},
				width: 1,
				scaling: { min: 1, max: 1 }
			};
		}

		if (type == 'topics') {
			options.nodes = {
				shape: 'dot',
				physics: true,
				color: { background: '#14AE5C', border: '#504b47' },
				scaling: { min: 4, max: 20 },
				font: { size: 12 }
			};

			options.edges = {
				smooth: false,
				color: '#504b47',
				arrows: {
					to: false,
					from: false
				},
				width: 1,
				scaling: { min: 1, max: 1 }
			};
		}

		const network = new vis.Network(div, data, options);
	});
</script>

<div class="chart">
	<div class="m-auto max-w-5xl">
		<div bind:this={div} />
	</div>
</div>
