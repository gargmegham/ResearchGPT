import preprocess from 'svelte-preprocess';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

export default {
	preprocess: [
		vitePreprocess(),
		preprocess({
			postcss: true
		})
	]
};
