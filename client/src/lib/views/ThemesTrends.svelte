<script lang="ts">
	import type { ThemesTrends } from '$lib/types/themes-trends';
	import LineGraph from '$lib/components/Visuals/LineGraph.svelte';
	import VisNetwork from '$lib/components/Visuals/VisNetwork.svelte';
	import TopicGraphWithUmap from '$lib/components/Visuals/TopicGraphWithUmap.svelte';
	import RepresentativeArticlesTable from '$lib/components/RepresentativeArticlesTable.svelte';

	export let data: ThemesTrends;

	// Beta graph TPK thing
	const beta_graph = data.tpkplots;

	//Topic Network Plot
	const topic_vis_data = {
		nodes: data.nodes_topic,
		edges: data.edges_topic
	};

	//Topic Graph With Umap
	const umap_data = {
		umap_topic_graph: data.umap_topic_graph,
		topic_count_graph: data.topic_count_graph,
		umap_article_graph: data.umap_article_graph
	};

	//articles over time or whatever
	const topic_trend_graph = data.topic_trend_graph;

	let topic_trend_topics = {};
	let xl = [],
		yl = [],
		topics = [];

	// Make arrays to arrange the topic "num" by date
	topic_trend_graph.forEach((item: any) => {
		if (typeof topic_trend_topics[item.Topics] === 'undefined') {
			topic_trend_topics[item.Topics] = { x: [], y: [] };
		}
		topic_trend_topics[item.Topics].x.push(item.date2);
		topic_trend_topics[item.Topics].y.push(item.num);
	});

	Object.keys(topic_trend_topics).forEach((topic) => {
		topics.push(topic);
	});
	Object.values(topic_trend_topics).forEach((topic: { x: number[]; y: number[] }) => {
		xl.push(topic.x);
		yl.push(topic.y);
	});
</script>

<div class="pt-visual-card">
	<h2 class="text-5xl text-pub-blue-800">Themes and Trends</h2>
	<p>
		Topic modeling is a technique used in Natural Language Processing (NLP) to automatically
		identify the topics or themes that are present in a corpus of text. Topic modeling algorithms
		are designed to analyze the patterns of word usage in a text corpus and to identify groups of
		words that tend to co-occur frequently.
	</p>
	<RepresentativeArticlesTable data={data.representative_articles} />
</div>
<div class="mt-3 pt-visual-card">
	<h2>Beta Graph</h2>
	<p>This figure shows the keywords that best distinguish each topic.</p>
	<img src={beta_graph} alt="" class="bg-white p-6" />
</div>
<div class="mt-3 pt-visual-card">
	<h2>Topic Network Plot</h2>
	<p>
		This figure shows how each of the topics relates to one another. The node is the size of the
		topic, and the edge is the correlation between the topics.
	</p>
	<VisNetwork data={topic_vis_data} type="topics" />
</div>
<div class="mt-3 pt-visual-card">
	<h2>Topic Trends over Time</h2>
	<p>This figure shows how publication trends in these topics over time.</p>
	<LineGraph x={xl} y={yl} multiple={topics} />
	<TopicGraphWithUmap data={umap_data} />
</div>
