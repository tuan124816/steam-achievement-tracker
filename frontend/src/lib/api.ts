// // src/lib/api.ts
// const API_BASE = 'http://localhost:8000';

// export async function uploadConfig(file: File) {
// 	const formData = new FormData();
// 	formData.append('file', file);

// 	const res = await fetch(`${API_BASE}/api/config`, {
// 		method: 'POST',
// 		body: formData
// 	});

// 	if (!res.ok) {
// 		throw new Error('Failed to upload config');
// 	}

// 	return res.json();
// }

// export async function runTracker(configPath: string) {
// 	const res = await fetch(`${API_BASE}/api/run?config_path=${configPath}`, {
// 		method: 'POST'
// 	});

// 	if (!res.ok) {
// 		throw new Error('Failed to start tracker');
// 	}

// 	return res.json(); // { job_id }
// }

// export function connectLogs(jobId: string, onMessage: (msg: string) => void) {
// 	const ws = new WebSocket(`ws://localhost:8000/ws/logs/${jobId}`);

// 	ws.onmessage = (event) => {
// 		onMessage(event.data);
// 	};

// 	ws.onerror = () => {
// 		console.error('WebSocket error');
// 	};

// 	return ws;
// }


const API = 'http://localhost:8000';

export async function uploadConfig(file: File) {
  const fd = new FormData();
  fd.append('file', file);
  const res = await fetch(`${API}/api/config`, { method: 'POST', body: fd });
  if (!res.ok) throw new Error('Upload failed');
  return res.json();
}

export async function runJob(configPath = 'config.json') {
  const res = await fetch(`${API}/api/run?config_path=${encodeURIComponent(configPath)}`, {
    method: 'POST'
  });
  if (!res.ok) throw new Error('Run failed');
  return res.json();
}

export async function getJob(jobId: string) {
  const res = await fetch(`${API}/api/jobs/${jobId}`);
  if (!res.ok) throw new Error('Job fetch failed');
  return res.json();
}
export async function loadFriends() {
  const res = await fetch(`${API}/api/friends`);
  return res.json();
}

export async function addFriend(friend: { steam_id: string; name?: string }) {
  const res = await fetch(`${API}/api/friends`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(friend)
  });
  return res.json();
}

export async function removeFriend(steamId: string) {
  const res = await fetch(`${API}/api/friends/${steamId}`, {
    method: 'DELETE'
  });
  return res.json();
}

export async function loadStats(excelPath: string) {
  const res = await fetch(
    `${API}/api/stats?filename=${encodeURIComponent(excelPath)}`
  );
  return res.json();
}