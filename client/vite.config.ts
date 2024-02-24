import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';
import basicSsl from '@vitejs/plugin-basic-ssl';

export default defineConfig({
	base: 'https:/research-gpt.com',
	plugins: [svelte(), basicSsl()],
	resolve: {
		alias: {
			$lib: '/src/lib'
		}
	}
});
