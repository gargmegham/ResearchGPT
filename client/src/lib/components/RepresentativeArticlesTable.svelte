<script lang="ts">
	import { onMount, onDestroy } from 'svelte';

	export let data = [];

	let el1: HTMLElement, table1: any;

	let the_buttons = [
		{ extend: 'copy', text: 'Copy Table' },
		{ extend: 'csv', text: 'Save As CSV' },
		{ extend: 'excel', text: 'Save As Excel' },
		{ extend: 'pdf', text: 'Save As PDF' },
		{ extend: 'print', text: 'Print Table' }
	];
	let the_columns = [
		{ data: 'keywords' },
		{ data: 'put_in_tables' },
		{ data: 'summary' },
		{ data: 'date' },
		{ data: 'journal' }
	];

	onMount(() => {
		table1 = jQuery(el1).DataTable({
			order: [],
			dom: 'frtipB',
			columns: the_columns,
			buttons: the_buttons
		});
	});

	onDestroy(() => {
		table1.destroy();
	});
</script>

<h2>Most Representative Articles</h2>
<p>This table shows the articles that are most representative of the topics within your search.</p>

<div class="chart">
	<table bind:this={el1} class="display" style="width:100%">
		<thead>
			<tr>
				<th>Keywords</th>
				<th>Title</th>
				<th>Summary</th>
				<th>Date</th>
				<th>Journal</th>
			</tr>
		</thead>
		<tbody>
			{#each data as row}
				<tr>
					<td>{row.keywords}</td>
					<td>{@html row.put_in_tables}</td>
					<td>{row.summary}</td>
					<td>{row.date}</td>
					<td>{row.journal}</td>
				</tr>
			{/each}
		</tbody>
	</table>
</div>
