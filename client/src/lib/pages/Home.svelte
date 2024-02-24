<script lang="ts">
	import Message from '$lib/components/Message.svelte';
	import uniqid from 'uniqid';
	import { wait_for_stuff } from '$lib/utils/utils';
	import { autocomplete, fEinit, search, url } from '$lib/apis/home';
	import type { MessageType, ViewDataType } from '$lib/types/vite-env';
	import { Search, MessageSquare } from 'lucide-svelte';
	import { onMount, afterUpdate } from 'svelte';
	import { scale } from 'svelte/transition';
	import Dots from '$lib/components/Dots.svelte';
	import GeneralVisualizations from '$lib/views/GeneralVisualizations.svelte';
	import AuthorInformation from '$lib/views/AuthorInformation.svelte';
	import Articles from '$lib/views/Articles.svelte';
	import Journals from '$lib/views/Journals.svelte';
	import ThemesTrends from '$lib/views/ThemesTrends.svelte';
	import Resources from '$lib/views/Resources.svelte';
	import Default from '$lib/views/Default.svelte';

	let msgs: MessageType[] = [];
	let query: string = '';
	let wiki: string = '';
	let chat: HTMLElement;
	let intro = true;
	let query_id = null;
	let view_type: string = null;
	let view_type_text: string = null;
	let data: ViewDataType;
	let are_dots_visible = false;
	let is_search_visible = true;
	let ac_options: any = [];
	let is_chat_open = true;
	let show_buttons = false;
	let active = false;
	let buttons = [
		{ name: 'general', redirect: false, button_text: 'General Visualizations' },
		{ name: 'authors', redirect: false, button_text: 'Author Information' },
		{ name: 'trends', redirect: false, button_text: 'Trends &amp; Themes' },
		{ name: 'articles', redirect: false, button_text: 'Articles' },
		{ name: 'journals', redirect: false, button_text: 'Journals' },
		{ name: 'resources', redirect: false, button_text: 'Resources' },
		{
			name: 'chatroom',
			redirect: true,
			button_text: 'Ask Your AI Companion'
		}
	];

	onMount(async () => {
		await fEinit();
		const urlParams = new URLSearchParams(window.location.search);
		if (urlParams.get('query_id') !== null) {
			query_id = urlParams.get('query_id');
			const localCache = JSON.parse(localStorage.getItem(query_id));
			if (localCache !== null) {
				is_search_visible = false;
				query = localCache.query;
				view_type = localCache.view_type;
				view_type_text = localCache.view_type_text;
				msgs = localCache.msgs;
				data = localCache.data;
				show_buttons = true;
				is_chat_open = false;
			} else {
				window.history.pushState('', '', '/v2/query');
			}
		}
	});

	async function handleSearch() {
		msgs = [...msgs, { id: uniqid(), msg: `Search for "${query}"`, side: 'right' }];
		is_search_visible = false;
		are_dots_visible = true;
		const trapped_query = query;

		wiki = await getWikiExtract(query);

		try {
			const response = await search(query);
			query_id = await response.queryid;
			// update query_id in the url
			window.history.pushState('', '', `?query_id=${encodeURIComponent(query_id)}`);
			wait_for_stuff(`${url}/v2/status/${response.queryid}`, async (data) => {
				msgs = [
					...msgs,
					{
						id: uniqid(),
						msg: `We found ${data.articles} articles on "${trapped_query}", what are you looking for?`,
						side: 'left'
					}
				];
				are_dots_visible = false;
				show_buttons = true;
			});
		} catch (error) {}
	}

	async function getWikiExtract(query) {
		const url = `https://en.wikipedia.org/w/api.php?origin=*&action=query&format=json&formatversion=2&prop=pageimages|pageterms|extracts&exintro&explaintext&redirects=1&piprop=thumbnail&pithumbsize=200&pilicense=any&titles=${encodeURIComponent(
			query
		)}`;

		try {
			const response = await fetch(url);
			const data = await response.json();
			const page = data.query.pages[0];

			let abstractHtml = '';

			if (page.extract) {
				if (page.thumbnail) {
					const imageUrl = page.thumbnail.source;
					abstractHtml += `<img class="float-right pl-8 pb-8" src="${imageUrl}" alt="${query} thumbnail" />`;
				}

				abstractHtml += page.extract;
			}

			active = data.batchcomplete;

			return abstractHtml;
		} catch (error) {
			console.error('Error:', error);
			return null;
		}
	}

	async function triggerAutocomplete() {
		if (query.length < 3) return;
		try {
			ac_options = await autocomplete(query);
		} catch (error) {}
	}

	async function get_views({ name, button_text, redirect }) {
		if (!!redirect) {
			if (name === 'chatroom') {
				let uri_to_navigate_to = `/v2/query/${name}/${encodeURIComponent(
					query_id
				)}/${encodeURIComponent(query)}`;
				window.location.href = uri_to_navigate_to;
			}
			return;
		}
		data = null;
		view_type = name;
		view_type_text = button_text;
		show_buttons = false;
		msgs = [
			...msgs,
			{
				id: uniqid(),
				msg: `Show me ${button_text}`,
				side: 'right'
			}
		];
		are_dots_visible = true;
		try {
			wait_for_stuff(`${url}/v2/${name}/${query_id}`, async (d) => {
				if (
					d.status === 'complete' &&
					msgs &&
					msgs.length > 0 &&
					msgs[msgs.length - 1].side === 'right'
				) {
					msgs = [
						...msgs,
						{
							id: uniqid(),
							msg: `All Done! If you'd like to see more visuals just let me know.`,
							side: 'left'
						}
					];
					are_dots_visible = false;
					show_buttons = true;
					is_chat_open = false;
				}
				data = d;
				localStorage.setItem(
					query_id,
					JSON.stringify({
						query,
						view_type,
						view_type_text,
						msgs,
						data
					})
				);
			});
		} catch (error) {
			console.log('spenser error', error);
		}
	}

	function autocomplete_select(option) {
		query = option.replace('<b>', '').replace('</b>', '');
		ac_options = [];
	}

	function restart() {
		query = '';
		view_type_text = '';
		query_id = null;
		data = null;
		msgs = [];
		ac_options = [];
		is_search_visible = true;
		show_buttons = false;
		intro = false;
		active = false;
		// remove query_id from the url
		window.history.pushState('', '', '/v2/query');
	}

	/* redo this less crappily later */
	afterUpdate(() => {
		chat.scrollTop = chat.scrollHeight;
	});
</script>

<main class="mx-auto md:grid md:gap-3">
	<div class="relative h-full bg-dark">
		<section
			class="bg-dark"
			id="chat-column"
			class:active={is_chat_open}
			class:aopen={ac_options.length}
			bind:this={chat}
		>
			<div class="chat-window">
				<div>
					{#if intro}
						<div out:scale={{ duration: 200 }}>
							<Message>
								Welcome to ResearchGpt Choose your own Adventure! To Start Search Any Subject.
							</Message>
						</div>
					{/if}
					{#if is_search_visible}
						<form
							action="POST"
							class="relative mb-9 pl-10"
							on:submit|preventDefault={handleSearch}
							in:scale={{ duration: 600, delay: 300 }}
						>
							<input
								title="Search input"
								type="search"
								class=" w-full rounded-2xl border-2 border-neutral-500 p-2 focus:outline-orange-500"
								placeholder="Search"
								bind:value={query}
								on:keyup={triggerAutocomplete}
							/>
							<button
								title="Submit Search"
								type="submit"
								class="absolute right-3 top-1/2 flex h-[30px] w-[30px] -translate-y-1/2 items-center justify-center rounded-full bg-orange-300 text-orange-900"
								><Search size={20} /></button
							>
							{#if ac_options.length}
								<ul class="absolute left-5 w-full border-2 border-neutral-500" id="autocompletes">
									{#each ac_options as option}
										<li class="p-2">
											<button class="w-full text-left" on:click={() => autocomplete_select(option)}
												>{@html option}</button
											>
										</li>
									{/each}
								</ul>
							{/if}
						</form>
					{/if}
					{#each msgs as msg (msg.id)}
						<Message side={msg.side}>{@html msg.msg}</Message>
					{/each}
					{#if are_dots_visible}
						<Dots />
					{/if}
					{#if show_buttons}
						<div class="flex flex-wrap justify-center gap-2">
							{#each buttons.filter((btn) => btn.button_text !== view_type_text) as butt, index}
								<button
									in:scale={{ duration: 400, delay: 50 * index + 300 }}
									class="block rounded-xl bg-orange-300
									 p-2 text-xs font-bold text-white hover:bg-orange-400"
									on:click={() => get_views(butt)}
								>
									{@html butt.button_text}
								</button>
							{/each}
							<button
								in:scale={{ duration: 400, delay: 50 * buttons.length + 300 }}
								class="block rounded-xl bg-pub-blue-500 p-2 text-xs font-bold text-white hover:bg-pub-blue-600"
								on:click={() => restart()}
							>
								New Search
							</button>
						</div>
					{/if}
				</div>
			</div>
		</section>
	</div>
	<button class="toggle-chat" on:click={() => (is_chat_open = !is_chat_open)}>
		<MessageSquare color="white" size={30} />
	</button>
	<section class="px-3 pt-5">
		<div class="m-auto max-w-7xl">
			{#if view_type === 'general' && data && data.status == 'complete'}
				<GeneralVisualizations {data} />
			{:else if view_type === 'authors' && data && data.status == 'complete'}
				<AuthorInformation {data} />
			{:else if view_type === 'articles' && data && data.status == 'complete'}
				<Articles {data} />
			{:else if view_type === 'journals' && data && data.status == 'complete'}
				<Journals {data} />
			{:else if view_type === 'trends' && data && data.status == 'complete'}
				<ThemesTrends {data} />
			{:else if view_type === 'resources' && data && data.status == 'complete'}
				<Resources {data} />
			{:else}
				<Default {query} {wiki} {active} />
			{/if}
		</div>
	</section>
</main>

<style lang="postcss">
	main {
		grid-template-columns: 450px 1fr;
		align-items: start;
	}
	#chat-column {
		height: calc(100vh - 60px);
		width: calc(100% - 32px);
		transform: translateX(calc(-100% - 30px));
		@apply fixed inset-4 z-30 flex flex-col overflow-auto  overflow-y-auto rounded-md px-3 py-16 shadow-lg transition-all;

		@media screen(md) {
			@apply sticky left-0 top-3 mt-3 translate-x-0 rounded-none shadow-none;
			height: calc(100vh - 104px);
		}

		&.active {
			@apply translate-x-0;
		}

		&.aopen {
			padding-bottom: 230px;
		}
	}
	#autocompletes {
		width: 90%;
		top: 93%;
		max-height: 200px;
		overflow-y: auto;
		background: white;
		li:nth-of-type(odd) {
			background: #ddd;
		}
		li {
			cursor: pointer;
			&:hover {
				background: #cdf;
			}
		}
	}
	/* Hide scrollbar for Chrome,
	Safari and Opera */
	#chat-column::-webkit-scrollbar {
		display: none;
	}
	/* Hide scrollbar for IE, Edge and Firefox */
	#chat-column {
		-ms-overflow-style: none; /* IE and Edge */
		scrollbar-width: none; /* Firefox */
	}
	.toggle-chat {
		@apply fixed bottom-4 right-4 z-40 flex h-[55px] w-[55px] items-center justify-center rounded-full bg-orange-400 transition-all md:hidden;
	}
	/* hide cancel in search input */
	input[type='search']::-webkit-search-cancel-button {
		-webkit-appearance: none;
	}
</style>
