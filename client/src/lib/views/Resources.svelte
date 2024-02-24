<script lang="ts">
	import type { ViewDataType } from '$lib/types/vite-env';

	export let data: ViewDataType;
</script>

<div class="pt-visual-card">
	<h2>Resources</h2>
	<h3>Community Commons</h3>
	<p>
		<a href="https://www.communitycommons.org" target="_blank">The Community Commons</a> is an online
		platform that provides tools, resources, and a virtual community to support collaboration and innovation
		among individuals and organizations working towards social change. If your search term yield any
		resources, they will be found below.
	</p>
	<div class="m-auto max-w-screen-2xl" id="cc_data">
		{@html data.cccontent}
	</div>
</div>

<div class="mt-3 pt-visual-card">
	<h3>Community Tool Box</h3>
	<p>
		These results are from the <a href="https://ctb.ku.edu/en/" target="_blank"
			>Community Tool Box</a
		>. <a href={data.ctblink} class="underline" target="_blank">See more results &nearr;</a>
	</p>

	<div id="ctb_data">
		{@html data.ctbcontent}
	</div>
</div>

<style lang="postcss">
	/* Community Toolbox embed */

	#ctb_data {
		background: #fff;
		padding: 10px;
	}

	#ctb_data .search-result {
		padding: 0 10px 10px;
	}

	#ctb_data .search-snippet {
		font-size: 14px;
	}

	#ctb_data h3 {
		font-family: var(--baseFont);
		text-transform: uppercase;
		font-size: 18px;
		line-height: 1.3;
		margin: 10px 0;
		text-decoration: underline;
		margin-bottom: 0;
	}
	#ctb_data h3 a:hover {
		@apply text-pub-blue-300;
	}
	#ctb_data p {
		margin: 10px 0;
	}
</style>
