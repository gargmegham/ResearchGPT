<!-- ChatList.svelte -->
<script lang="ts">
	import type { Chatroom, OutgoingMessage } from '$lib/types/chatrooms';
	import { capitalizeSentence, clickOutside } from '$lib/utils/utils';
	import { deleteChatroom, updateChatroomName } from '$lib/apis/chatrooms';
	import { Zap, Wand2, Edit, Trash2, Loader, UserIcon, ExternalLink } from 'lucide-svelte';

	export let chatrooms: Chatroom[];
	export let refetchChatrooms: () => Promise<void>;
	export let switchChatroom: (id: number) => Promise<void>;
	export let currentChatroom: Chatroom;
	export let chatroomsLoading: boolean;
	export let chatroomLoading: boolean;
	export let sendMessage: (msg: OutgoingMessage) => void;
	export let isGPT4Active: boolean = true;

	let user_name: string = localStorage.getItem('user_name') || '';
	let user_photo: string = localStorage.getItem('user_photo') || '';
	let chatroomNameToEdit: string = '';
	let chatroomIdToEdit: number = 0;
	let editingChatroomName: boolean = false;
	let searchedChatroomsQuery: string = '';

	function toggleGPT4() {
		isGPT4Active = !isGPT4Active;
		sendMessage({
			chatroom_id: currentChatroom.id,
			msg: isGPT4Active ? '/changemodel gpt_4' : '/changemodel gpt_3_5_turbo'
		});
	}

	const editChatroomName = async () => {
		try {
			editingChatroomName = true;
			if (chatroomIdToEdit !== 0 && chatroomNameToEdit !== currentChatroom.name) {
				await updateChatroomName(chatroomIdToEdit, chatroomNameToEdit);
				refetchChatrooms();
			}
		} finally {
			chatroomIdToEdit = 0;
			editingChatroomName = false;
		}
	};
</script>

<div class="pt-flex h-full w-80 flex-shrink-0 flex-col bg-dark px-6 py-8">
	<div class="pt-flex h-20 w-full flex-row items-center justify-center rounded-lg bg-gray-50 py-4">
		<div class="h-15 pt-flex w-10 items-center justify-center rounded-2xl bg-orange-300">
			<img
				class="s-qwpL0o84ZVgB aspect-square h-full w-auto rounded-full object-cover"
				src="https://app.research-gpt.com/research-gpt.png"
				alt="research-gpt-logo"
			/>
		</div>
		<div class="ml-2 text-2xl font-bold">ResearchGPT</div>
	</div>
	{#if !chatroomLoading && currentChatroom && currentChatroom.id}
		<div
			class="pt-flex mt-4 w-full flex-col items-center rounded-lg border border-gray-200 bg-orange-50 py-6"
		>
			<div class="h-20 w-20 overflow-hidden rounded-full border bg-orange-300">
				{#if user_photo}
					<img src={user_photo} alt="Avatar" class="h-full w-full" />
				{:else}
					<UserIcon class="h-full w-full" color="white" />
				{/if}
			</div>
			<div class="text-md mt-2 font-semibold">{@html user_name}</div>
			<div class="text-sm text-gray-500">
				{@html capitalizeSentence(currentChatroom.name).slice(0, 20)}...
			</div>
			<div class="pt-flex mt-3 flex-row items-center">
				<label for="isGPT4Active" class="pt-flex mb-0 mr-2 cursor-pointer items-center">
					<div class="relative">
						<input
							bind:checked={isGPT4Active}
							type="checkbox"
							id="isGPT4Active"
							class="sr-only"
							on:click={toggleGPT4}
						/>
						<div
							class="block h-5 w-8 rounded-full"
							class:bg-orange-300={isGPT4Active}
							class:bg-gray-300={!isGPT4Active}
						/>
						<div class="dot absolute left-1 top-1 h-3 w-3 rounded-full bg-white transition" />
					</div>
				</label>
				{#if isGPT4Active}
					<Wand2 size="14" color="orange" strokeWidth="2" />
					<div class="ml-1 text-xs leading-none">GPT-4</div>
				{:else}
					<Zap size="14" color="orange" strokeWidth="2" />
					<div class="ml-1 text-xs leading-none">GPT-3.5</div>
				{/if}
			</div>
		</div>
	{:else}
		<div role="status">
			<div class="pt-flex mb-10 mt-10 animate-pulse items-center">
				<svg
					class="h-14 w-14 text-gray-200 dark:text-gray-300"
					aria-hidden="true"
					fill="currentColor"
					viewBox="0 0 20 20"
					xmlns="http://www.w3.org/2000/svg"
					><path
						fill-rule="evenodd"
						d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-6-3a2 2 0 11-4 0 2 2 0 014 0zm-2 4a5 5 0 00-4.546 2.916A5.986 5.986 0 0010 16a5.986 5.986 0 004.546-2.084A5 5 0 0010 11z"
						clip-rule="evenodd"
					/></svg
				>
				<div class="p-2">
					<div class="mb-2 h-2.5 w-32 rounded-full bg-gray-200 dark:bg-gray-400" />
					<div class="w-30 h-5 rounded-full bg-gray-200 dark:bg-gray-400" />
				</div>
			</div>
		</div>
	{/if}
	<div class="pt-flex mt-4 flex-col">
		{#if chatroomsLoading}
			<div role="status" class="mt-5">
				<div class="pt-flex mb-5 animate-pulse items-center justify-between pl-2 pr-5">
					<div>
						<div class="mb-2.5 h-2.5 w-24 rounded-full bg-gray-300 dark:bg-gray-400" />
						<div class="h-2 w-32 rounded-full bg-gray-200 dark:bg-gray-300" />
					</div>
					<div class="h-2.5 w-12 rounded-full bg-gray-300 dark:bg-gray-300" />
				</div>
				<div class="pt-flex items-center justify-between pl-2 pr-5">
					<div>
						<div class="mb-2.5 h-2.5 w-24 rounded-full bg-gray-300 dark:bg-gray-400" />
						<div class="h-2 w-32 rounded-full bg-gray-200 dark:bg-gray-300" />
					</div>
					<div class="h-2.5 w-12 rounded-full bg-gray-300 dark:bg-gray-300" />
				</div>
			</div>
		{:else if chatrooms && chatrooms.length > 0}
			<div class="relative">
				<div class="pt-flex pointer-events-none absolute inset-y-0 left-0 items-center pl-3">
					<svg
						aria-hidden="true"
						class="h-5 w-5 text-gray-500"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
						xmlns="http://www.w3.org/2000/svg"
						><path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
						/></svg
					>
				</div>
				<input
					bind:value={searchedChatroomsQuery}
					id="chatroom-search"
					class="block w-full rounded-lg bg-gray-50 py-3 pl-10 text-sm text-gray-900 focus:outline-orange-200"
					placeholder="Search by name...."
				/>
			</div>
			<div class="list-card pt-flex">
				{#each chatrooms.filter((chatroom) => chatroom.name
						.toLowerCase()
						.includes(searchedChatroomsQuery.toLowerCase())) as chatroom (chatroom.id)}
					{#if !editingChatroomName && chatroomIdToEdit === chatroom.id}
						<div class="relative">
							<input
								bind:value={chatroomNameToEdit}
								type="text"
								id={`${chatroom.id}`}
								class="block w-full rounded-lg border border-gray-300 bg-gray-50 p-3 text-sm text-gray-900 focus:outline-none dark:border-gray-600 dark:bg-gray-400 dark:text-white dark:placeholder-gray-400 dark:focus:outline-none"
								placeholder={chatroom.name}
								required
								use:clickOutside
								on:click-outside={editChatroomName}
								on:keypress={(e) => {
									if (e.key === 'Enter') editChatroomName();
								}}
							/>
						</div>
					{:else}
						<button
							disabled={chatroom.id === currentChatroom.id}
							class="pt-flex flex-row items-center rounded-xl bg-gray-50 p-2 hover:bg-gray-200"
						>
							<div
								class="pt-flex char-pill items-center justify-center rounded-full bg-orange-200 font-semibold"
							>
								{@html chatroom.name[0].toUpperCase()}
							</div>
							<div
								class="text-sm font-semibold"
								on:click={() => {
									switchChatroom(chatroom.id);
								}}
								on:keydown={(e) => {
									if (e.key === 'Enter') switchChatroom(chatroom.id);
								}}
							>
								<span class="ml-2">{@html capitalizeSentence(chatroom.name).slice(0, 20)}...</span>
							</div>
							<!-- spacer -->
							<div class="flex-1" />
							<button class="mr-2">
								<a
									href={`/v2/query?query_id=${chatroom.search}`}
									target="_parent"
									class=" text-orange-300 hover:text-orange-500"
								>
									<ExternalLink size="14" strokeWidth="2" />
								</a>
							</button>
							{#if chatroom.id === currentChatroom.id}
								<button
									on:click={() => {
										chatroomNameToEdit = chatroom.name;
										chatroomIdToEdit = chatroom.id;
									}}
								>
									{#if editingChatroomName}
										<Loader size="14" color="black" strokeWidth="2" />
									{:else}
										<Edit size="14" color="black" strokeWidth="2" />
									{/if}
								</button>
							{:else}
								<button
									on:click={async () => {
										await deleteChatroom(chatroom.id);
										refetchChatrooms();
									}}
								>
									<Trash2 size="14" color="red" strokeWidth="2" />
								</button>
							{/if}
						</button>
					{/if}
				{/each}
			</div>
		{/if}
	</div>
</div>

<style lang="css">
	.char-pill {
		width: 2rem;
		height: 2rem;
	}
	.list-card {
		flex-direction: column;
		display: flex;
		margin-top: 16px;
		max-height: 30vh;
		row-gap: 0.5rem;
		overflow-y: scroll;
	}
	/* Hide scrollbar for Chrome,
	Safari and Opera */
	.list-card::-webkit-scrollbar {
		display: none;
	}
	/* Hide scrollbar for IE, Edge and Firefox */
	.list-card {
		-ms-overflow-style: none; /* IE and Edge */
		scrollbar-width: none; /* Firefox */
	}
	input:checked ~ .dot {
		transform: translateX(100%);
	}
</style>
