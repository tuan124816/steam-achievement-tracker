<!-- <script lang="ts">
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
</pre> -->





<!-- <script lang="ts">
	import { jobId, jobLogs, jobStatus } from '$lib/stores/job';
	import { connectLogs } from '$lib/ws';

	let ws: WebSocket | null = null;

	async function runTracker() {
		jobLogs.set([]);
		jobStatus.set('queued');

		const res = await fetch('http://localhost:8000/api/run', {
			method: 'POST'
		});

		const data = await res.json();
		jobId.set(data.job_id);

		ws = connectLogs(data.job_id);
	}
</script>

<button on:click={runTracker}>
	Run Tracker
</button>

<p>Status: {$jobStatus}</p>

<pre class="logs">
{#each $jobLogs as log}
{log}
{/each}
</pre>

<style>
.logs {
	background: #111;
	color: #0f0;
	padding: 1rem;
	height: 300px;
	overflow-y: auto;
	font-family: monospace;
}
</style> -->






<!-- <script lang="ts">
	import { jobId, jobStatus, jobLogs, } from '$lib/stores';
	import { uploadConfig, runJob, getJob } from '$lib/api';
	import { connectLogs } from '$lib/ws';
	import { friends } from '$lib/stores';
	import { loadFriends, addFriend, removeFriend } from '$lib/api';
	import { onMount } from 'svelte';
	import { stats } from '$lib/stores';
	import { loadStats } from '$lib/api';
  
	let file: File | null = null;
	let ws: WebSocket | null = null;
	let steamId = '';
	let name = '';
  
	async function start() {
	  if (!file) return;
  
	  jobStatus.set('queued');
	  jobLogs.set([]);
  
	  await uploadConfig(file);
	  const { job_id } = await runJob('config.json');
  
	  jobId.set(job_id);
	  jobStatus.set('running');
  
	  ws = connectLogs(job_id);
  
	  const poll = setInterval(async () => {
		const job = await getJob(job_id);
		jobStatus.set(job.status);
		if (job.status === 'done' || job.status === 'failed') {
		  clearInterval(poll);
		  ws?.close();
		}
	  }, 1500);
	}

	onMount(async () => {
		friends.set(await loadFriends());
	});

	async function add() {
		friends.set(await addFriend({ steam_id: steamId, name }));
		steamId = '';
		name = '';
	}

	async function remove(id: string) {
		friends.set(await removeFriend(id));
	}
  </script>
  
  <h1>Steam Achievement Tracker</h1>
  
  <input type="file" accept=".json" on:change={(e) => file = e.target.files?.[0] ?? null} />
  <button on:click={start}>Start Tracking</button>

  <h2>Friends</h2>

  <input placeholder="Steam ID" bind:value={steamId} />
  <input placeholder="Name (optional)" bind:value={name} />
  <button on:click={add}>Add</button>

  <ul>
    {#each $friends as f}
      <li>
		{f.name ?? 'Unknown'} ({f.steam_id})
		<button on:click={() => remove(f.steam_id)}>x</button>
	  </li>
	{/each}
  </ul>
  
  <p>Status: {$jobStatus}</p>
  
  {#if $jobStatus === 'running'}
	<progress />
  {/if}
  
  <pre>
  {#each $jobLogs as line}
  {line}
  {/each}
  </pre>
  
  {#if $jobStatus === 'done'}
  <h2>Comparison</h2>

  {#each $friends as f}
    <div>
      <strong>{f.name ?? f.steam_id}</strong>
      <progress value="70" max="100"></progress>
    </div>
  {/each}
	<a href="http://localhost:8000/api/download?filename=game_achievements_friends.xlsx">
	  Download Excel
	</a>
  {/if}
   -->






<script lang="ts">
  import { onMount } from 'svelte';

  /* -----------------------------
   * Stores
   * ----------------------------- */
  import { jobId, jobStatus, jobLogs, friends, stats } from '$lib/stores';

  /* -----------------------------
   * API / WS
   * ----------------------------- */
  import {
    uploadConfig,
    runJob,
    getJob,
    loadFriends,
    addFriend,
    removeFriend,
    loadStats
  } from '$lib/api';

  import { connectLogs } from '$lib/ws';

  /* -----------------------------
   * Local state
   * ----------------------------- */
  let file: File | null = null;
  let ws: WebSocket | null = null;

  let steamId = '';
  let name = '';

  /* -----------------------------
   * Tracker start
   * ----------------------------- */
  async function start() {
    if (!file) return;

    jobStatus.set('queued');
    jobLogs.set([]);
    stats.set({});

    await uploadConfig(file);
    const { job_id } = await runJob('config.json');

    jobId.set(job_id);
    jobStatus.set('running');

    ws = connectLogs(job_id);

    const poll = setInterval(async () => {
      const job = await getJob(job_id);
      jobStatus.set(job.status);

      if (job.status === 'done' || job.status === 'failed') {
        clearInterval(poll);
        ws?.close();

        if (job.status === 'done') {
          // Load parsed Excel stats (Step 7)
          const data = await loadStats('game_achievements_friends.xlsx');
          stats.set(data);
        }
      }
    }, 1500);
  }

  /* -----------------------------
   * Friends management
   * ----------------------------- */
  onMount(async () => {
    friends.set(await loadFriends());
  });

  async function add() {
    friends.set(await addFriend({ steamid: steamId, name }));
    steamId = '';
    name = '';
  }

  async function remove(id: string) {
    friends.set(await removeFriend(id));
  }
</script>

<style>
  h1, h2 {
    color: #e5e7eb;
  }

  section {
    margin-bottom: 24px;
    padding: 16px;
    background: #1b2838;
    border-radius: 8px;
  }

  button {
    background: #4f46e5;
    color: white;
    border: none;
    padding: 6px 12px;
    border-radius: 4px;
    cursor: pointer;
  }

  button:hover {
    background: #4338ca;
  }

  input {
    margin-right: 6px;
    padding: 4px;
  }

  .bar {
    background: #374151;
    height: 14px;
    width: 320px;
    border-radius: 4px;
    overflow: hidden;
  }

  .fill {
    background: #4f46e5;
    height: 100%;
  }

  pre {
    background: #020617;
    color: #9ca3af;
    padding: 12px;
    max-height: 240px;
    overflow-y: auto;
  }
</style>

<!-- =============================
     HEADER
     ============================= -->
<h1>Steam Achievement Tracker</h1>

<!-- =============================
     CONFIG & RUN
     ============================= -->
<section>
  <h2>Run Tracker</h2>

  <input
    type="file"
    accept=".json"
    on:change={(e) => (file = e.target.files?.[0] ?? null)}
  />

  <button on:click={start}>Start Tracking</button>

  <p>Status: <strong>{$jobStatus}</strong></p>

  {#if $jobStatus === 'running'}
    <progress></progress>
  {/if}
</section>

<!-- =============================
     FRIENDS
     ============================= -->
<section>
  <h2>Friends</h2>

  <input placeholder="Steam ID" bind:value={steamId} />
  <input placeholder="Name (optional)" bind:value={name} />
  <button on:click={add}>Add</button>

  <ul>
    {#each $friends as f}
      <li>
        {f.name ?? 'Unknown'} ({f.steamid})
        <button on:click={() => remove(f.steamid)}>✕</button>
      </li>
    {/each}
  </ul>
</section>

<!-- =============================
     LIVE LOGS
     ============================= -->
<section>
  <h2>Live Logs</h2>
  <pre>
{#each $jobLogs as line}
{line}
{/each}
  </pre>
</section>

<!-- =============================
     RESULTS & COMPARISON
     ============================= -->
{#if $jobStatus === 'done'}
<section>
  <h2>Achievement Comparison</h2>

  {#each Object.entries($stats) as [player, s]}
    <div style="margin-bottom: 12px">
      <strong>{player}</strong>

      <div class="bar">
        <div class="fill" style="width: {s.percent}%"></div>
      </div>

      <small>{s.unlocked}/{s.total} ({s.percent}%)</small>
    </div>
  {/each}

  <a
    href="http://localhost:8000/api/download?filename=game_achievements_friends.xlsx"
    target="_blank"
  >
    Download Excel
  </a>
</section>
{/if}
