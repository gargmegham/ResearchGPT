const config = {
	content: ['./src/**/*.{html,js,svelte,ts}'],
	theme: {
		extend: {
			colors: {
				'pub-orange': {
					DEFAULT: '#FFA629',
					50: '#FFF2E1',
					100: '#FFEACC',
					200: '#FFD9A3',
					300: '#FFC87B',
					400: '#FFB752',
					500: '#FFA629',
					600: '#F08C00',
					700: '#B86B00',
					800: '#804B00',
					900: '#482A00'
				},
				'pub-blue': {
					DEFAULT: '#0D99FF',
					50: '#C5E6FF',
					100: '#B0DEFF',
					200: '#87CDFF',
					300: '#5FBBFF',
					400: '#36AAFF',
					500: '#0D99FF',
					600: '#007BD4',
					700: '#005A9C',
					800: '#003A64',
					900: '#00192C'
				},
				'pub-green': {
					DEFAULT: '#14AE5C',
					50: '#88F1B9',
					100: '#76EFAF',
					200: '#51EB99',
					300: '#2DE784',
					400: '#18D36F',
					500: '#14AE5C',
					600: '#0E7C41',
					700: '#084927',
					800: '#03170C',
					900: '#000000'
				},
				'pub-pomegranate': {
					DEFAULT: '#F24822',
					50: '#FCD8CF',
					100: '#FBC8BC',
					200: '#F9A896',
					300: '#F7886F',
					400: '#F46849',
					500: '#F24822',
					600: '#D0300C',
					700: '#9B2409',
					800: '#661706',
					900: '#310B03'
				},
				dark: '#30363F',
				navy: '#002739',
				light: '#EFEFE1'
			}
		},
		fontFamily: {
			fancy: ['Jubilat', 'serif'],
			sans: ['Inter', 'system-ui', 'Avenir', 'Helvetica', 'Arial', 'sans-serif']
		}
	}
};

module.exports = config;
