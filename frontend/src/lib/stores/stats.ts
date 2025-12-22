import { writable } from 'svelte/store';

export type PlayerStats = {
  total: number;
  unlocked: number;
  percent: number;
};

export const stats = writable<Record<string, PlayerStats>>({});
