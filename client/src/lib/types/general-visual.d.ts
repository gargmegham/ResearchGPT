/// <reference types="svelte" />
/// <reference types="vite/client" />

import type {
	SingleWordPlotType,
	ViewDataType,
	BigramType,
	EdgeType,
	NodeType
} from '$lib/types/vite-env';

export interface Words {
	word: string;
	n: number;
}

export interface AllWords {
	text: string;
	size: number;
	index: number;
}

export interface General extends ViewDataType {
	correlation_nodes?: NodeType[];
	correlation_edges?: EdgeType[];
}
