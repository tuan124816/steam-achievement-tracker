import { jobLogs, jobStatus } from '$lib/stores/job';

export function connectLogs(jobId: string) {
	const ws = new WebSocket(`ws://localhost:8000/ws/logs/${jobId}`);

	ws.onmessage = (event) => {
		jobLogs.update((logs) => [...logs, event.data]);
	};

	ws.onopen = () => {
		jobStatus.set('running');
	};

	ws.onerror = () => {
		jobStatus.set('error');
	};

	ws.onclose = () => {
		jobStatus.set('done');
	};

	return ws;
}
