<!-- ChatBox.svelte -->
<script lang="ts">
	import type { Chatroom, OutgoingMessage, PreviousMessage } from '$lib/types/chatrooms';
	import { Eraser, UserIcon, StopCircleIcon } from 'lucide-svelte';
	import Dots from '$lib/components/Dots.svelte';
	import { afterUpdate } from 'svelte';

	export let currentChatroom: Chatroom;
	export let largeScreen: boolean;
	export let sendMessage: (msg: OutgoingMessage) => void;
	export let previousMessages: PreviousMessage[] = [];
	export let assistantTyping: boolean;

	let user_photo: string = localStorage.getItem('user_photo') || '';
	let input: string = '';

	export const onSendMessage = (msg: string = `/query ${input}`) => {
		if (!msg) return;
		try {
			const outgoingMessage: OutgoingMessage = {
				chatroom_id: currentChatroom.id,
				msg: msg
			};
			sendMessage(outgoingMessage);
		} finally {
			input = '';
		}
	};

	const formatUserMessage = (msg: string) => {
		if (msg.startsWith('please answer my question')) {
			try {
				let query = msg.split('\n')[1].split(':')[1].trim();
				query = query.substring(1, query.length - 1);
				return query;
			} catch {
				return msg;
			}
		}
		return msg;
	};

	const clearChat = () => {
		onSendMessage('/clear');
	};

	const scrollToBottom = () => {
		const chatBox = document.getElementById('chat-box');
		chatBox && chatBox.scrollTo(0, chatBox.scrollHeight);
	};

	afterUpdate(scrollToBottom);
</script>

<div id="chat-box" class="scroll scrollbar-w-none pt-flex mb-4 h-full flex-col overflow-x-auto">
	<div class="pt-flex h-full flex-col">
		<div class="grid grid-cols-12" class:gap-y-2={largeScreen} class:gap-y-12={!largeScreen}>
			{#if previousMessages && previousMessages.length === 0}
				<div class="col-start-1 col-end-8 rounded-lg p-2">
					<div class="pt-flex flex-row items-center">
						<div
							class="pt-flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full bg-orange-200"
						>
							<img
								class="s-qwpL0o84ZVgB aspect-square h-full w-auto rounded-full object-cover"
								src="https://app.research-gpt.com/research-gpt.png"
								alt=""
							/>
						</div>
						<div class="relative ml-3 rounded-xl bg-white px-3 py-2 text-sm shadow">
							<div>Hey how may i help you?</div>
						</div>
					</div>
				</div>
			{:else}
				{#each previousMessages as message}
					{#if !message.is_user}
						<div
							class="col-start-1 rounded-lg p-2"
							class:col-end-9={largeScreen}
							class:col-end-12={!largeScreen}
						>
							<div class="pt-flex flex-row">
								<div
									class="pt-flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full bg-orange-300"
								>
									<img
										class="s-qwpL0o84ZVgB aspect-square h-full w-auto rounded-full object-cover"
										src="https://app.research-gpt.com/research-gpt.png"
										alt=""
									/>
								</div>
								<div class="relative ml-3 w-full rounded-xl bg-white px-3 py-2 text-sm shadow">
									<pre class="whitespace-pre-line break-words">
										{message.content}
									</pre>
									{#if !assistantTyping}
										<div
											class="absolute bottom-0 left-0 -mb-5 mr-2 text-xs text-gray-500"
											class:-mb-10={!largeScreen}
											class:-mb-5={largeScreen}
										>
											{new Date(message.timestamp)['toGMTString']()}
										</div>
									{/if}
								</div>
							</div>
						</div>
					{:else}
						<div
							class=" 2 col-end-13 rounded-lg"
							class:col-start-6={largeScreen}
							class:col-start-3={!largeScreen}
						>
							<div class="pt-flex flex-row-reverse justify-start">
								<div
									class="pt-flex h-10 w-10 items-center justify-center rounded-full bg-orange-300"
								>
									{#if !user_photo}
										<UserIcon />
									{:else}
										<img
											class="s-qwpL0o84ZVgB aspect-square h-full w-auto rounded-full object-cover"
											src={user_photo}
											alt=""
										/>
									{/if}
								</div>
								<div class="relative mr-3 w-full rounded-xl bg-orange-100 px-3 py-2 text-sm shadow">
									<pre class="whitespace-pre-line break-words">
										{formatUserMessage(message.content)}
									</pre>
									<div
										class="absolute bottom-0 right-0 mr-2 text-xs text-gray-500"
										class:-mb-10={!largeScreen}
										class:-mb-5={largeScreen}
									>
										{new Date(message.timestamp)['toGMTString']()}
									</div>
								</div>
							</div>
						</div>
					{/if}
				{/each}
				{#if assistantTyping}
					<div class="col-start-1 col-end-9 items-center rounded-lg p-2">
						<div class="pt-flex flex-row items-center">
							<div class="pt-flex mr-3 h-10 w-10 flex-shrink-0 items-center justify-center" />
							<Dots showBlueDot={false} />
						</div>
					</div>
				{/if}
			{/if}
		</div>
	</div>
</div>
<div class="pt-flex h-32 w-full flex-row items-center rounded-xl bg-white px-3">
	<button
		type="button"
		class="pt-flex items-center justify-center text-gray-400 hover:text-gray-600"
		on:click={clearChat}
	>
		<Eraser />
	</button>
	<div class="ml-4 flex-grow">
		<div class="relative w-full">
			<textarea
				class="max-h-[250px] w-full resize-none rounded-md border border-gray-100 bg-gray-50 p-2 shadow-sm focus:outline-none focus:ring-1 focus:ring-orange-500"
				placeholder="Type your prompt here..."
				maxlength="10000"
				on:keydown={(e) => {
					if (e.key === 'Enter' && !e.shiftKey) {
						e.preventDefault();
						onSendMessage();
					}
				}}
				bind:value={input}
			/>
		</div>
	</div>
	<div class="ml-4">
		{#if assistantTyping}
			<button
				on:click={() => {
					onSendMessage('/stop');
				}}
				class="pt-flex h-full flex-shrink-0 items-center justify-center rounded-xl bg-red-400 px-3 py-3 text-white hover:bg-red-600"
			>
				{#if largeScreen}
					<span>Stop</span>{/if}
				<span class:ml-2={largeScreen}>
					<StopCircleIcon color="white" />
				</span>
			</button>
		{:else}
			<button
				on:click={() => {
					onSendMessage();
				}}
				class="pt-flex flex-shrink-0 items-center justify-center rounded-xl bg-orange-400 px-3 py-3 text-white hover:bg-orange-500"
			>
				{#if largeScreen}
					<span>Send</span>
				{/if}
				<span class:ml-2={largeScreen}>
					<svg
						class="-mt-px h-4 w-4 rotate-45 transform"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
						xmlns="http://www.w3.org/2000/svg"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
						/>
					</svg>
				</span>
			</button>
		{/if}
	</div>
</div>

<style lang="css" scoped>
	/* Hide scrollbar for Chrome,
	Safari and Opera */
	.scrollbar-w-none::-webkit-scrollbar {
		display: none;
	}

	/* Hide scrollbar for IE, Edge and Firefox */
	.scrollbar-w-none {
		-ms-overflow-style: none; /* IE and Edge */
		scrollbar-width: none; /* Firefox */
	}
	pre {
		font-family: Inter, system-ui, Avenir, Helvetica, Arial, sans-serif;
		font-weight: 400;
		font-size: 1rem;
		line-height: 1.5;
		color: #111827;
		letter-spacing: normal;
	}
</style>
