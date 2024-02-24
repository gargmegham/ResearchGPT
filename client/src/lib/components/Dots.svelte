<script lang="ts">
	export let showBlueDot: boolean = true;
</script>

<div class="msg-box -mb-9 flex items-end gap-2">
	{#if showBlueDot}
		<div class="h-[36px] w-[36px] flex-shrink-0 rounded-full bg-pub-orange-300">
			<img
				class="aspect-square h-full w-auto rounded-full object-cover"
				src="https://app.research-gpt.com/research-gpt.png"
				alt=""
			/>
		</div>
	{/if}
	<div class="w-fit rounded-2xl border-2 bg-transparent px-4 py-3 text-sm">
		<svg viewBox="0 0 340 140" width="45" height="15">
			<circle r="50" cx="50" cy="90" class=" circle transition-all" style="--delay: 0ms" />
			<circle r="50" cx="170" cy="90" class=" circle transition-all" style="--delay: 100ms" />
			<circle r="50" cx="290" cy="90" class=" circle transition-all" style="--delay: 200ms" />
		</svg>
	</div>
</div>

<style lang="postcss">
	.circle {
		@apply fill-pub-blue-300;
		animation: run 1000ms infinite forwards;
		animation-delay: var(--delay);
	}

	@keyframes run {
		0% {
			translate: 0 0;
			@apply fill-pub-blue-300;
		}

		50% {
			translate: 0px -40px;
			@apply fill-pub-orange-300;
		}

		100% {
			translate: 0 0;
			@apply fill-pub-blue-300;
		}
	}
</style>
