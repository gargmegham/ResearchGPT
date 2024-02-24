<script lang="ts">
	import { onMount } from 'svelte';

	export let words = [];

	let div: HTMLElement;

	onMount(() => {
		const biggest = Math.max(...words.map(({ size }) => size));

		// Init Word Cloud
		const layout = d3.layout
			.cloud()
			.size([600, 500])
			.words(words)
			.padding(0.5)
			.rotate(0)
			.font('Roboto')
			.fontWeight('bold')
			.fontSize(function (d) {
				//map font sizes 8px - 64px based on range in this word cloud
				return ((d.size - 1) * (64 - 8)) / (biggest - 1) + 8;
			})
			.on('end', draw);

		layout.start();

		function draw(word_data) {
			d3.select(div)
				.append('svg')
				.attr('width', layout.size()[0])
				.attr('height', layout.size()[1])
				.attr('viewBox', '0 0 ' + layout.size()[0] + ' ' + layout.size()[1])
				.append('g')
				.attr('transform', 'translate(' + layout.size()[0] / 2 + ',' + layout.size()[1] / 2 + ')')
				.selectAll('text')
				.data(word_data)
				.enter()
				.append('text')
				.style('font-size', function (d) {
					return d.size + 'px';
				})
				.style('font-family', 'Roboto')
				.style('font-weight', 'bold')
				.style('fill', function (d) {
					return barColorOne(words.length, d.index);
				})
				.attr('text-anchor', 'middle')
				.attr('transform', function (d) {
					return 'translate(' + [d.x, d.y] + ')rotate(' + d.rotate + ')';
				})
				.text(function (d) {
					return d.text;
				});
		}
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
