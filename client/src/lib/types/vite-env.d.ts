/// <reference types="svelte" />
/// <reference types="vite/client" />

export interface MessageType {
	id: string | number;
	msg: string;
	side?: 'left' | 'right';
}

export interface ViewDataType {
	queryid: string;
	status: 'complete' | 'start' | 'partial';
	bigram?: BigramType[];
	edges?: EdgeType[];
	nodes?: NodeType[];
	singlewordplot?: SingleWordPlotType[];
	most_collaborators?: MostCollaboratorsType[];
	top_authors?: TopAuthorsType[];
	top_authors_decade?: TopAuthorsDecadeType[];
	total_collaborators?: TotalCollaboratorsType[];
	review_articles?: ReviewArticlesType[];
	journal_count?: JournalCountType[];
	journals_by_year?: JournalsByYearType[];
}

export interface BigramType {
	bigram: string;
	n: number;
}

export interface EdgeType {
	color: string;
	from: string;
	to: string;
	title: string;
	value: number;
}

export interface NodeType {
	id: string;
	label: string;
	name: string;
	title: string;
	value: number;
}

export interface SingleWordPlotType {
	word: string;
	n: number;
}

export interface MostCollaboratorsType {
	authors: string;
	collabs: number;
}

export interface TopAuthorsType {
	authors: string;
	n: number;
}

export interface TopAuthorsDecadeType {
	authors: string;
	decade: string;
	n: number;
}

export interface TotalCollaboratorsType {
	authors: string;
	collab: string;
	weight: number;
}

export interface AllArticlesType {
	authors: string;
	data: string;
	journal: string;
	link: string;
}

export interface ReviewArticlesType {
	authors: string;
	data: string;
	journal: string;
	link: string;
}

export interface JournalCountType {
	count: number;
	name: string;
}

export interface JournalsByYearType {
	count: number;
	journal: string;
	year: number;
}
