<script lang="ts">
	import { fly } from 'svelte/transition';
	import { UserIcon } from 'lucide-svelte';

	export let side: 'left' | 'right' = 'left';

	const user_photo = localStorage.getItem('user_photo') || '';
</script>

<div
	class="msg-box mb-9 flex items-start gap-2"
	class:justify-end={side === 'right'}
	transition:fly={{ y: 100 }}
>
	{#if side === 'left'}
		<div class="h-[36px] w-[36px] flex-shrink-0 rounded-full bg-pub-orange-300">
			<img
				class="aspect-square h-full w-auto rounded-full object-cover"
				src="https://app.research-gpt.com/research-gpt.png"
				alt=""
			/>
		</div>
	{/if}
	<div
		class="msg-bubble max-w-xl rounded-2xl px-4 py-2 text-sm"
		class:rounded-tl-lg={side === 'left'}
		class:rounded-tr-lg={side === 'right'}
		class:bg-orange-300={side === 'right'}
		class:bg-white={side === 'left'}
		class:text-white={side === 'right'}
	>
		<slot>No Message Content</slot>
	</div>
	{#if side === 'right'}
		<div class="pp avatar-pub h-[36px] w-[36px] flex-shrink-0 rounded-full bg-pub-orange-300">
			{#if user_photo}
				<img
					class="aspect-square h-full w-auto rounded-full object-cover"
					src={user_photo}
					alt=""
				/>
			{:else}
				<UserIcon color="white" class="h-full w-auto rounded-full object-cover" />
			{/if}
		</div>
	{/if}
</div>

<style lang="postcss">
	.avatar::before {
		@apply absolute rounded-full bg-white;
		content: '';
		position: absolute;
		top: 30%;
		left: 50%;
		width: 12px;
		height: 12px;
		transform: translate(-50%, -50%);
	}
	.avatar::after {
		@apply absolute rounded-full bg-white;
		content: '';
		top: 80%;
		left: 50%;
		width: 20px;
		height: 20px;
		transform: translate(-50%, -50%);
	}
</style>
