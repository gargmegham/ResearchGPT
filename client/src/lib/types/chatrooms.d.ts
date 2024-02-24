/// <reference types="svelte" />
/// <reference types="vite/client" />

export interface Chatroom {
	id: number;
	name: string;
	title: string;
	search: string;
}

export interface IncomingMessage {
	msg: string;
	finish: boolean;
	chatroom_id: number;
	is_user: boolean;
	init: boolean;
	model_name: string | null;
}

export interface OutgoingMessage {
	chatroom_id: number;
	msg: string;
}

export interface PreviousMessage {
	is_user: boolean;
	content: string;
	tokens: number;
	timestamp: number;
	model_name: string | null;
}
