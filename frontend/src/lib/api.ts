// src/lib/api.ts
const API_BASE = 'http://localhost:8000';

export async function uploadConfig(file: File) {
	const formData = new FormData();
	formData.append('file', file);

	const res = await fetch(`${API_BASE}/api/config`, {
		method: 'POST',
		body: formData
	});

	if (!res.ok) {
		throw new Error('Failed to upload config');
	}

	return res.json();
}

export async function runTracker(configPath: string) {
	const res = await fetch(`${API_BASE}/api/run?config_path=${configPath}`, {
		method: 'POST'
	});

	if (!res.ok) {
		throw new Error('Failed to start tracker');
	}

	return res.json(); // { job_id }
}

export function connectLogs(jobId: string, onMessage: (msg: string) => void) {
	const ws = new WebSocket(`ws://localhost:8000/ws/logs/${jobId}`);

	ws.onmessage = (event) => {
		onMessage(event.data);
	};

	ws.onerror = () => {
		console.error('WebSocket error');
	};

	return ws;
}
