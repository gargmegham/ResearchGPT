export const url = `https://${import.meta.env.VITE_PT_SERVER}`;

export async function autocomplete(query: string) {
	try {
		const req = await fetch(`${url}/api/autocompletes`, {
			headers: { 'Content-Type': 'application/json' },
			method: 'post',
			body: JSON.stringify({ query: query })
		});
		return await req.json();
	} catch (error) {}
}

export async function search(query: string) {
	try {
		const req = await fetch(`${url}/v2/search`, {
			headers: { 'Content-Type': 'application/json' },
			method: 'post',
			body: JSON.stringify({ search: query })
		});
		return await req.json();
	} catch (error) {}
}

export async function fEinit() {
	try {
		const response = await fetch(`${url}/v2/FEinit`, {
			headers: {
				'X-ResearchGPT-Microservice-Id': import.meta.env.VITE_PT_CHAT_SK
			}
		});
		const data: {
			token: string;
			user_id: number;
			user_name: string;
			user_photo: string;
		} = await response.json();
		localStorage.setItem('token', data.token);
		localStorage.setItem('user_id', String(data.user_id));
		localStorage.setItem('user_name', data.user_name);
		localStorage.setItem('user_photo', data.user_photo);
		return data.token;
	} catch (err) {
		console.log(err);
		return '';
	}
}
