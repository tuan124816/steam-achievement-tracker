import { writable } from 'svelte/store';

export type Friend = {
  steam_id: string;
  name?: string;
};

export const friends = writable<Friend[]>([]);
