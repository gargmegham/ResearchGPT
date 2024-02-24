/// <reference types="svelte" />
/// <reference types="vite/client" />

import type { ViewDataType } from '$lib/types/vite-env';

export interface ThemesTrends extends ViewDataType {
	tpkplots: any;
	nodes_topic: any;
	edges_topic: any;
	umap_topic_graph: any;
	topic_count_graph: any;
	umap_article_graph: any;
	topic_trend_graph: any;
	representative_articles: any;
}
