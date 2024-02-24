import { fEinit } from '$lib/apis/home';
import jwtDecode from 'jwt-decode';

export const base = `https://${import.meta.env.VITE_PT_CHAT_SERVER}`;
export const webSocketBase = `wss://${import.meta.env.VITE_PT_CHAT_SERVER}`;

async function commonHeaders() {
	let headers = new Headers();
	headers.append('Content-Type', 'application/json');
	headers.append('Accept', 'application/json');
	let token: string = localStorage.getItem('token');
	const decodedToken: {
		exp: number;
	} = token ? jwtDecode(token) : { exp: 0 };
	// if token has expired, call fEinit to fetch a new token
	if (!token || decodedToken.exp < Date.now() / 1000) token = await fEinit();
	headers.append('Authorization', `Bearer ${token}`);
	return headers;
}

async function fetchChatrooms() {
	try {
		let myHeaders = await commonHeaders();
		let requestOptions = {
			method: 'GET',
			headers: myHeaders
		};
		const response = await fetch(`${base}/chatroom`, requestOptions);
		// handle 401
		if (response.status === 401) {
			console.log('401: Unauthorized');
			return [];
		}
		// handle 200
		return await response.json();
	} catch (error) {
		console.log(error);
	}
}

async function createChatroom(title: string, search: string, name: string) {
	try {
		let myHeaders = await commonHeaders();
		let requestOptions = {
			method: 'POST',
			headers: myHeaders,
			body: JSON.stringify({
				title,
				search,
				name
			})
		};
		const response = await fetch(`${base}/chatroom`, requestOptions);
		// handle 401
		if (response.status === 401) {
			console.log('401: Unauthorized');
			return [];
		}
		// handle 200
		return await response.json();
	} catch (error) {
		console.log(error);
	}
}

async function deleteChatroom(id: number) {
	try {
		let myHeaders = await commonHeaders();
		let requestOptions = {
			method: 'DELETE',
			headers: myHeaders
		};
		const response = await fetch(`${base}/chatroom/${id}`, requestOptions);
		// handle 401
		if (response.status === 401) {
			console.log('401: Unauthorized');
		}
		return null;
	} catch (error) {
		console.log(error);
	}
}

async function updateChatroomName(id: number, name: string) {
	try {
		let myHeaders = await commonHeaders();
		let requestOptions = {
			method: 'PUT',
			headers: myHeaders,
			body: JSON.stringify({
				name
			})
		};
		const response = await fetch(`${base}/chatroom/${id}`, requestOptions);
		// handle 401
		if (response.status === 401) {
			console.log('401: Unauthorized');
		}
		return null;
	} catch (error) {
		console.log(error);
	}
}

export { fetchChatrooms, createChatroom, deleteChatroom, updateChatroomName };
