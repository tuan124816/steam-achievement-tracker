import { writable } from 'svelte/store';

export const jobId = writable<string | null>(null);
export const jobStatus = writable<'idle' | 'queued' | 'running' | 'done' | 'failed'>('idle');
export const jobLogs = writable<string[]>([]);
