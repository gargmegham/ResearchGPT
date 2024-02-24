module.exports = {
	root: true,
	extends: [
		'eslint:recommended',
		'prettier',
		'plugin:@typescript-eslint/eslint-recommended',
		'plugin:@typescript-eslint/recommended'
	],
	plugins: ['@typescript-eslint', 'svelte3'],
	overrides: [
		{ files: ['*.svelte'], processor: 'svelte3/svelte3' },
		{ files: ['*.spec.js', '*.spec.cjs'], env: { jest: true } }
	],
	parserOptions: {
		sourceType: 'module',
		ecmaVersion: 2020
	},
	env: {
		browser: true,
		es2017: true,
		node: true
	},
	parser: '@typescript-eslint/parser',
	rules: {}
};
