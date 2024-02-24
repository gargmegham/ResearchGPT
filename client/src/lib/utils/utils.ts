export async function wait_for_stuff(endpoint: string, callback: any, duration: number = 1000) {
	const interval_thing = setInterval(async () => {
		try {
			const req = await fetch(endpoint, {
				headers: { 'Content-Type': 'application/json' },
				method: 'post'
			});
			const data = await req.json();
			if (data.status === 'complete') {
				clearInterval(interval_thing);
				callback(data);
			}
		} catch (err) {
			clearInterval(interval_thing);
		}
	}, duration);
}

export function capitalizeSentence(sentence: string) {
	return sentence
		.toLowerCase()
		.split(' ')
		.map((word) => word.charAt(0).toUpperCase() + word.slice(1))
		.join(' ');
}

export function clickOutside(node: any) {
	const handleClick = (event: any) => {
		if (node && !node.contains(event.target) && !event.defaultPrevented) {
			node.dispatchEvent(new CustomEvent('click-outside', node));
		}
	};
	document.addEventListener('click', handleClick, true);
	return {
		destroy() {
			document.removeEventListener('click', handleClick, true);
		}
	};
}
