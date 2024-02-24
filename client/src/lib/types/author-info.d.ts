/// <reference types="svelte" />
/// <reference types="vite/client" />

import type { ViewDataType, NodeType, EdgeType } from '$lib/types/vite-env';

export interface Author extends ViewDataType {
	collab_nodes: NodeType[];
	collab_edges: EdgeType[];
}
