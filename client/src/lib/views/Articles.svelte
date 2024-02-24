<script lang="ts">
	import type { ViewDataType } from '$lib/types/vite-env';
	import { onMount, onDestroy } from 'svelte';

	export let data: ViewDataType;

	let el1: HTMLElement, el2: HTMLElement, el3: HTMLElement, table1: any, table2: any, table3: any;

	let the_buttons = [
		{ extend: 'copy', text: 'Copy Table' },
		{ extend: 'csv', text: 'Save As CSV' },
		{ extend: 'excel', text: 'Save As Excel' },
		{ extend: 'pdf', text: 'Save As PDF' },
		{ extend: 'print', text: 'Print Table' }
	];
	let the_columns = [{ data: 'link' }, { data: 'authors' }, { data: 'date' }, { data: 'journal' }];

	onMount(() => {
		table1 = jQuery(el1).DataTable({
			order: [],
			dom: 'frtipB',
			columns: the_columns,
			buttons: the_buttons
		});

		if (data.review_articles.length > 0) {
			table2 = jQuery(el2).DataTable({
				order: [],
				dom: 'frtipB',
				columns: the_columns,
				buttons: the_buttons
			});
		}

		if (data.open_access_articles.length > 0) {
			table3 = jQuery(el3).DataTable({
				order: [],
				dom: 'frtipB',
				columns: the_columns,
				buttons: the_buttons
			});
		}
	});

	onDestroy(() => {
		table1.destroy();
		if (data.review_articles.length > 0) {
			table2.destroy();
		}
		if (data.open_access_articles.length > 0) {
			table3.destroy();
		}
	});
</script>

<div class="pt-visual-card">
	<h2>All Articles</h2>
	<p>These are all the articles returned by your search term.</p>
	<div class="chart">
		<table bind:this={el1} class="display" style="width:100%">
			<thead>
				<tr>
					<th>Title</th>
					<th>Authors</th>
					<th>Date</th>
					<th>Journal</th>
				</tr>
			</thead>
			<tbody>
				{#each data.all_articles as row}
					<tr>
						<td>{@html row.link}</td>
						<td>{row.authors}</td>
						<td>{row.date}</td>
						<td>{row.journal}</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
</div>

{#if data.review_articles.length > 0}
	<div class="pt-visual-card mt-3">
		<h2>Review Articles</h2>
		<p>
			Review articles are a type of academic publication that provide a comprehensive summary and
			analysis of the existing literature on a particular research topic. Review articles are
			written by experts in the field, and they typically provide an overview of the current state
			of knowledge on the topic, identify gaps or inconsistencies in the literature, and propose
			directions for future research.
		</p>
		<p>
			Review articles can take different forms and serve different purposes. For example, some
			review articles provide a systematic and quantitative synthesis of the existing literature,
			using meta-analysis or other statistical methods to combine the results of multiple studies.
			Other review articles provide a narrative and qualitative synthesis of the literature, using a
			thematic or conceptual framework to organize and interpret the findings.
		</p>
		<p>
			Review articles are often published in academic journals, and they are highly valued by
			researchers and practitioners in many fields. Review articles are useful because they can
			provide a comprehensive and authoritative overview of the current state of knowledge on a
			topic, saving readers time and effort in searching and synthesizing the literature themselves.
			Additionally, review articles can help to identify gaps and inconsistencies in the literature,
			and suggest directions for future research, making them a valuable resource for researchers
			who want to stay up-to-date with the latest developments in their field.
		</p>
		<div class="chart">
			<table bind:this={el2} class="display" style="width:100%">
				<thead>
					<tr>
						<th>Title</th>
						<th>Authors</th>
						<th>Date</th>
						<th>Journal</th>
					</tr>
				</thead>
				<tbody>
					{#each data.review_articles as row}
						<tr>
							<td>{@html row.link}</td>
							<td>{row.authors}</td>
							<td>{row.date}</td>
							<td>{row.journal}</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	</div>
{/if}

{#if data.open_access_articles.length > 0}
	<div class="pt-visual-card mt-3">
		<h2 class="text-center">Open Access Articles</h2>
		<div class="chart">
			<table bind:this={el3} class="display" style="width:100%">
				<thead>
					<tr>
						<th>Title</th>
						<th>Authors</th>
						<th>Date</th>
						<th>Journal</th>
					</tr>
				</thead>
				<tbody>
					{#each data.open_access_articles as row}
						<tr>
							<td>{@html row.link}</td>
							<td>{row.authors}</td>
							<td>{row.date}</td>
							<td>{row.journal}</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	</div>
{/if}
