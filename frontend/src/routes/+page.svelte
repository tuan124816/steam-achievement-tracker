<script lang="ts">
	import { uploadConfig, runTracker, connectLogs } from '$lib/api';

	let file: File | null = null;
	let logs: string[] = [];
	let status = 'Idle';
	let jobId: string | null = null;

	async function handleUpload() {
		if (!file) return;

		status = 'Uploading config...';
		const res = await uploadConfig(file);
		status = 'Config uploaded';

		// Start tracker
		status = 'Starting tracker...';
		const run = await runTracker(file.name);
		jobId = run.job_id;

		status = `Running (job ${jobId})`;
		startLogs(jobId);
	}

	function startLogs(id: string) {
		connectLogs(id, (msg) => {
			logs = [...logs, msg];
		});
	}
</script>

<h1>Steam Achievement Tracker v2.0</h1>

<input
	type="file"
	accept=".json"
	on:change={(e) => (file = (e.target as HTMLInputElement).files?.[0] ?? null)}
/>

<button on:click={handleUpload} disabled={!file}>
	Run Tracker
</button>

<p><strong>Status:</strong> {status}</p>

<h2>Live Logs</h2>
<pre style="background:#111; color:#0f0; padding:10px; height:300px; overflow:auto;">
{logs.join('\n')}
</pre>
