import type { CollectionEntry } from 'astro:content';

export type Block = CollectionEntry<'sider'>['data']['blocks'][number];
export type BlockOf<T extends Block['type']> = Extract<Block, { type: T }>;
