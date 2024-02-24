<!-- Main.svelte -->
<script lang="ts">
	import ChatList from '$lib/components/Chatroom/ChatList.svelte';
	import ChatBox from '$lib/components/Chatroom/ChatBox.svelte';
	import { fetchChatrooms, webSocketBase, createChatroom } from '$lib/apis/chatrooms';
	import type {
		Chatroom,
		OutgoingMessage,
		PreviousMessage,
		IncomingMessage
	} from '$lib/types/chatrooms.d.ts';
	import { Eraser } from 'lucide-svelte';
	import { onMount, onDestroy } from 'svelte';

	export let search: string;
	export let title: string;

	let webSocket: WebSocket;
	let maxReconnectAttempts = 5;
	let chatrooms: Chatroom[] = [];
	let currentChatroom: Chatroom = {} as Chatroom;
	let chatroomsLoading: boolean = false;
	let isGPT4Active: boolean = true;
	let chatroomLoading: boolean = false;
	let previousMessages: PreviousMessage[] = [];
	let sidebarOpen: boolean = true;
	$: largeScreen = innerWidth > 1000 ? true : false;
	let innerWidth = 0;
	let assistantTyping: boolean = false;

	const sendMessage = (msg: OutgoingMessage) => {
		try {
			if (msg.msg === '/stop') {
				webSocket && webSocket.readyState === webSocket.OPEN && webSocket.send('stop');
				return;
			}
			msg.msg.startsWith('/clear') && (previousMessages = []);
			msg.msg.startsWith('/query') &&
				previousMessages.push({
					content: msg.msg.split('/query ')[1],
					is_user: true,
					tokens: -1,
					timestamp: new Date().getTime(),
					model_name: 'gpt-4'
				});
			webSocket && webSocket.readyState === webSocket.OPEN && webSocket.send(JSON.stringify(msg));
		} catch (err) {
			console.log(err);
		}
	};

	const refetchChatrooms = async () => {
		chatroomsLoading = true;
		chatrooms = await fetchChatrooms();
		currentChatroom = chatrooms.find((chatroom) => chatroom.id === currentChatroom.id) as Chatroom;
		chatroomsLoading = false;
	};

	const toggleChatroomLoading = async (val: boolean = !chatroomLoading) => {
		chatroomLoading = val;
	};

	const parsePreviousMessages = (messages: string, model_name: string | null) => {
		if (!messages || !messages.includes('previous_chats')) return;
		const messagesJson = JSON.parse(messages);
		if (messagesJson && messagesJson.previous_chats) {
			previousMessages = messagesJson.previous_chats;
			model_name !== 'gpt-4' && (isGPT4Active = false);
		}
		toggleChatroomLoading(false);
	};

	const switchChatroom = async (id: number) => {
		toggleChatroomLoading(true);
		currentChatroom = chatrooms.find((chatroom) => chatroom.id === id) as Chatroom;
		// ping new chatroom
		pingSocket();
	};

	const pingSocket = () => {
		try {
			const pingMessage: OutgoingMessage = { msg: '/ping', chatroom_id: currentChatroom.id };
			webSocket &&
				webSocket.readyState === webSocket.OPEN &&
				webSocket.send(JSON.stringify(pingMessage));
		} catch (err) {
			console.log(err);
		}
	};

	const handleIncomingMessages = (eventJson: IncomingMessage) => {
		// assistant typing
		if (eventJson.msg === null) {
			assistantTyping = true;
			// add empty message to previousMessages
			previousMessages.push({
				content: '',
				is_user: false,
				tokens: -1,
				timestamp: new Date().getTime(),
				model_name: 'gpt-4'
			});
			return;
		}
		// assistant stopped typing
		if (eventJson.finish === true) {
			assistantTyping = false;
			return;
		}
		// append last message content from eventJson.msg
		if (assistantTyping && eventJson.finish === false && eventJson.msg !== null)
			previousMessages[previousMessages.length - 1].content += eventJson.msg;
		toggleChatroomLoading(false);
	};

	const createNewWebSocketConnection = () => {
		// websocket connection
		const token: string = localStorage.getItem('token');
		webSocket = new WebSocket(
			`${webSocketBase}/ws/chat?token=${token}&chatroom_id=${currentChatroom.id}`
		);
		// websocket event listeners
		webSocket.onopen = function () {
			console.log('WebSocket connection established...');
		};
		webSocket.onerror = function (error: Event) {
			console.log('WebSocket Error: ', error);
			try {
				if (webSocket.readyState === webSocket.OPEN) webSocket.close();
			} catch {}
		};
		webSocket.onclose = function () {
			maxReconnectAttempts--;
			console.log('WebSocket connection closed. Reconnecting.....');
			maxReconnectAttempts > 0 ? createNewWebSocketConnection() : window.close();
		};
		webSocket.onmessage = (event: MessageEvent) => {
			const eventJson: IncomingMessage = JSON.parse(event.data);
			if (eventJson.chatroom_id !== currentChatroom.id) {
				// ping pong
				pingSocket();
				return;
			}
			handleIncomingMessages(eventJson);
			// previous messages
			parsePreviousMessages(eventJson.msg, eventJson.model_name);
		};
	};

	onMount(async () => {
		toggleChatroomLoading(true);
		currentChatroom = await createChatroom(title, search, title);
		await refetchChatrooms();
		createNewWebSocketConnection();
		// close websocket connection on page refresh
		window.addEventListener('beforeunload', (event) => {
			event.preventDefault();
			try {
				if (webSocket.readyState === webSocket.OPEN) {
					webSocket.close();
					console.log('WebSocket connection closed due to page refresh');
				}
			} catch {}
		});
	});

	onDestroy(() => {
		try {
			if (webSocket.readyState === webSocket.OPEN) webSocket.close();
		} catch {}
	});
</script>

<svelte:window bind:innerWidth />

<div class="pt-h-screen pt-flex text-gray-800 antialiased">
	<div class="pt-flex h-full w-full flex-row overflow-x-hidden">
		{#if !largeScreen}
			<button
				on:click={() => (sidebarOpen = !sidebarOpen)}
				type="button"
				class="pt-flex fixed bottom-[50%] right-4 z-40 h-[40px] w-[40px] items-center justify-center rounded-full bg-orange-400 transition-all"
			>
				<svg
					class="h-6 w-6"
					aria-hidden="true"
					fill="white"
					viewBox="0 0 20 20"
					xmlns="http://www.w3.org/2000/svg"
				>
					<path
						clip-rule="evenodd"
						fill-rule="evenodd"
						d="M2 4.75A.75.75 0 012.75 4h14.5a.75.75 0 010 1.5H2.75A.75.75 0 012 4.75zm0 10.5a.75.75 0 01.75-.75h7.5a.75.75 0 010 1.5h-7.5a.75.75 0 01-.75-.75zM2 10a.75.75 0 01.75-.75h14.5a.75.75 0 010 1.5H2.75A.75.75 0 012 10z"
					/>
				</svg>
			</button>
			{#if sidebarOpen}
				<aside class="fixed left-0 z-40 h-screen w-64 translate-x-0 transition-transform">
					<ChatList
						{chatrooms}
						{sendMessage}
						{currentChatroom}
						{refetchChatrooms}
						{chatroomsLoading}
						{switchChatroom}
						{isGPT4Active}
						{chatroomLoading}
					/>
				</aside>
			{/if}
		{:else}
			<ChatList
				{chatrooms}
				{sendMessage}
				{currentChatroom}
				{refetchChatrooms}
				{chatroomsLoading}
				{switchChatroom}
				{isGPT4Active}
				{chatroomLoading}
			/>
		{/if}
		<div
			class="pt-flex h-full flex-auto flex-col pt-4 md:px-4 md:pb-4 lg:px-4 lg:pb-4 xl:px-4 xl:pb-4"
		>
			<div class="pt-flex h-full flex-auto flex-shrink-0 flex-col rounded-2xl bg-gray-100 p-3">
				<!-- skeleton loader -->
				{#if chatroomLoading}
					<div
						class="scroll scrollbar-w-none pt-flex mb-6 h-full animate-pulse flex-row overflow-x-auto"
					>
						<div class="pt-flex flex-col">
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
						</div>
						<div class="pt-flex w-80 flex-col">
							<div class="pt-flex mt-2 h-6 w-11/12 flex-row rounded-md bg-gray-300" />
							<div class="pt-flex mt-2 h-6 w-10/12 flex-row rounded-md bg-gray-300" />
							<div class="pt-flex mt-2 h-6 w-9/12 flex-row rounded-md bg-gray-300" />
							<div class="pt-flex mt-2 h-6 w-9/12 flex-row rounded-md bg-gray-300" />
						</div>
					</div>
					<div
						class="scroll scrollbar-w-none pt-flex mb-4 h-full animate-pulse flex-row-reverse overflow-x-auto"
					>
						<div class="pt-flex flex-col">
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
						</div>
						<div class="pt-flex w-80 flex-col">
							<div class="pt-flex mt-2 h-6 w-11/12 flex-row rounded-md bg-gray-300" />
							<div class="pt-flex mt-2 h-6 w-10/12 flex-row rounded-md bg-gray-300" />
							<div class="pt-flex mt-2 h-6 w-9/12 flex-row rounded-md bg-gray-300" />
							<div class="pt-flex mt-2 h-6 w-9/12 flex-row rounded-md bg-gray-300" />
						</div>
					</div>
					<div class="pt-flex h-36 w-full flex-row items-center rounded-xl bg-white p-4 px-4">
						<button
							disabled
							type="button"
							class=" pt-flex items-center justify-center text-gray-400"
						>
							<Eraser />
						</button>
						<div class="ml-4 flex-grow">
							<div class="relative w-full">
								<textarea
									aria-disabled="true"
									disabled
									class="max-h-[200px] w-full resize-none rounded-md border border-gray-100 bg-gray-50 p-2 shadow-sm focus:outline-none"
									placeholder="Type your prompt here..."
								/>
							</div>
						</div>
						<div class="ml-4">
							<button
								disabled
								class="pt-flex flex-shrink-0 items-center justify-center rounded-xl bg-gray-500 px-4 py-1 text-white hover:bg-gray-600"
							>
								{#if largeScreen}
									<span>Send</span>
								{/if}
								<span class="ml-2">
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
						</div>
					</div>
				{:else if currentChatroom && currentChatroom.id}
					<ChatBox
						{largeScreen}
						{currentChatroom}
						{sendMessage}
						{previousMessages}
						{assistantTyping}
					/>
				{/if}
			</div>
		</div>
	</div>
</div>

<style lang="css">
	.pt-h-screen {
		height: calc(100vh - 60px);
	}
	@media (min-width: 1000px) {
		.pt-h-screen {
			height: calc(100vh - 80px);
		}
	}
</style>
