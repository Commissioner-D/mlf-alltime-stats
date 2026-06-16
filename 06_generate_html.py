"""
Step 6: HTML-Generator
=======================

Liest stats.json und schreibt index.html mit:
- Embedded Daten (kein separater Fetch noetig)
- Filter Overall / Regular / Postseason / Fantasy Bowl
- Sortierbare Tabellen
- Hash-Routing: #/ = Stats, #/h2h = Head-to-Head
- Fleaflicker Dark Mode Style
"""

import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
STATS_FILE = SCRIPT_DIR / "stats.json"
OUTPUT_FILE = SCRIPT_DIR / "index.html"


HTML = r"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MLF All-Time Stats</title>
<style>
:root {
  --bg: #1c1f24;
  --bg-elev: #23272d;
  --bg-row: #2a2f36;
  --bg-row-alt: #262b31;
  --bg-header: #20242a;
  --border: #2e333a;
  --text: #e8e8e8;
  --text-dim: #8b929b;
  --text-muted: #5a6168;
  --cyan: #5ec8e0;
  --cyan-bg: #1d3a44;
  --orange: #f5a623;
  --orange-bg: #4a3416;
  --green: #5ab92e;
  --green-bg: #2a4a1a;
  --red: #d4584c;
  --inactive: #707880;
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; background: var(--bg); color: var(--text); font: 13px/1.4 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; }
a { color: var(--cyan); text-decoration: none; }
a:hover { text-decoration: underline; }

header {
  background: var(--bg-header);
  border-bottom: 1px solid var(--border);
  padding: 14px 20px;
  display: flex;
  align-items: center;
  gap: 24px;
}
header h1 { margin: 0; font-size: 18px; font-weight: 600; }
header h1 .sub { color: var(--text-dim); font-weight: 400; margin-left: 8px; }
header nav { display: flex; gap: 4px; }
header nav a {
  padding: 6px 14px;
  border-radius: 4px;
  color: var(--text-dim);
  font-weight: 500;
}
header nav a.active, header nav a:hover {
  background: var(--bg-row);
  color: var(--text);
  text-decoration: none;
}
header .meta {
  margin-left: auto;
  color: var(--text-dim);
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 12px;
}
header .meta .last-update {
  background: var(--bg-row);
  border: 1px solid var(--border);
  padding: 4px 10px;
  border-radius: 3px;
  color: var(--text);
}
header .meta .last-update strong {
  color: var(--cyan);
  margin-left: 4px;
}

main { padding: 20px; max-width: 1400px; margin: 0 auto; }
.view { display: none; }
.view.active { display: block; }

section { margin-bottom: 32px; }
section h2 {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-dim);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 0 0 10px;
  padding-bottom: 6px;
}

.filter-bar {
  display: flex;
  gap: 4px;
  margin-bottom: 16px;
  border-bottom: 1px solid var(--border);
  padding-bottom: 0;
}
.filter-bar button {
  background: none;
  border: none;
  color: var(--text-dim);
  padding: 8px 16px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
  font-family: inherit;
}
.filter-bar button:hover { color: var(--text); }
.filter-bar button.active {
  color: var(--cyan);
  border-bottom-color: var(--cyan);
}

table.stat {
  width: 100%;
  border-collapse: collapse;
  background: var(--bg-elev);
  border-radius: 4px;
  overflow: hidden;
}
table.stat th {
  background: var(--bg-header);
  color: var(--text-dim);
  font-weight: 500;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  padding: 8px 10px;
  text-align: left;
  border-bottom: 1px solid var(--border);
  cursor: pointer;
  user-select: none;
  white-space: nowrap;
}
table.stat th:hover { color: var(--text); }
table.stat th.num { text-align: right; }
table.stat th.sorted { color: var(--cyan); }
table.stat th.sorted::after {
  content: ' \25BE';
  font-size: 10px;
}
table.stat th.sorted.asc::after { content: ' \25B4'; }
table.stat td {
  padding: 7px 10px;
  border-bottom: 1px solid rgba(255,255,255,0.03);
}
table.stat td.num { text-align: right; font-variant-numeric: tabular-nums; }
table.stat tbody tr:nth-child(odd) { background: var(--bg-row-alt); }
table.stat tbody tr:nth-child(even) { background: var(--bg-row); }
table.stat tbody tr:hover { background: var(--bg-header); }
table.stat tbody tr.inactive td { color: var(--inactive); }

.rank {
  display: inline-block;
  background: var(--cyan-bg);
  color: var(--cyan);
  width: 22px;
  height: 22px;
  line-height: 22px;
  text-align: center;
  border-radius: 3px;
  font-size: 12px;
  font-weight: 600;
  margin-right: 8px;
}

.team-cell { display: flex; align-items: center; gap: 8px; }
.team-name { font-weight: 500; }
.team-owner { color: var(--text-dim); font-size: 11px; margin-left: 6px; }
.team-badge {
  display: inline-block;
  width: 20px; height: 20px;
  border-radius: 50%;
  text-align: center;
  font-size: 10px;
  line-height: 20px;
  font-weight: 700;
  color: rgba(0,0,0,0.7);
  flex-shrink: 0;
}

.win-pill {
  background: var(--green-bg);
  color: var(--green);
  padding: 2px 8px;
  border-radius: 3px;
  font-size: 11px;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

.pct { color: var(--text-dim); font-size: 11px; }

.subtab {
  display: flex; gap: 4px; margin: 0 0 10px;
}
.subtab button {
  background: var(--bg-header);
  border: 1px solid var(--border);
  color: var(--text-dim);
  padding: 4px 12px;
  font-size: 12px;
  cursor: pointer;
  border-radius: 3px;
  font-family: inherit;
}
.subtab button:hover { color: var(--text); }
.subtab button.active {
  background: var(--cyan-bg);
  color: var(--cyan);
  border-color: var(--cyan);
}

/* H2H */
.h2h-controls {
  display: flex;
  align-items: center;
  gap: 16px;
  background: var(--bg-elev);
  padding: 16px;
  border-radius: 4px;
  margin-bottom: 20px;
}
.h2h-controls select {
  background: var(--bg-header);
  color: var(--text);
  border: 1px solid var(--border);
  padding: 8px 12px;
  font-size: 14px;
  font-family: inherit;
  border-radius: 3px;
  min-width: 240px;
  flex: 1;
}
.h2h-controls .vs {
  color: var(--text-dim);
  font-weight: 600;
}

.h2h-summary {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 24px;
  background: var(--bg-elev);
  padding: 24px;
  border-radius: 4px;
  margin-bottom: 20px;
  align-items: center;
}
.h2h-side { text-align: center; }
.h2h-side.left { text-align: right; }
.h2h-side.right { text-align: left; }
.h2h-team {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 6px;
}
.h2h-record {
  font-size: 32px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  color: var(--text);
}
.h2h-record.win { color: var(--green); }
.h2h-record.loss { color: var(--red); }
.h2h-vs {
  font-size: 11px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 1px;
}
.h2h-points {
  font-size: 12px;
  color: var(--text-dim);
  margin-top: 6px;
}

.h2h-empty {
  background: var(--bg-elev);
  padding: 40px;
  text-align: center;
  color: var(--text-dim);
  border-radius: 4px;
}

td .score-winner { color: var(--green); font-weight: 600; }
td .score-loser  { color: var(--text); }
td .score-tie    { color: var(--orange); font-weight: 600; }

.tag {
  display: inline-block;
  font-size: 10px;
  padding: 1px 6px;
  border-radius: 2px;
  background: var(--bg-header);
  color: var(--text-dim);
  text-transform: uppercase;
  margin-left: 6px;
  letter-spacing: 0.3px;
}
.tag.po { background: var(--orange-bg); color: var(--orange); }
.tag.fb { background: var(--cyan-bg); color: var(--cyan); }

.game-link {
  display: inline-block;
  text-decoration: none;
  font-size: 11px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 3px;
  white-space: nowrap;
  letter-spacing: 0.2px;
  transition: all 0.15s;
}
.game-link.nfl  { color: #e74948; }
.game-link.flea { color: var(--cyan); }
.game-link:hover {
  text-decoration: underline;
  background: var(--bg-header);
}
</style>
</head>
<body>

<header>
  <h1>MLF <span class="sub">All-Time Stats</span></h1>
  <nav>
    <a href="#/" data-route="stats">Stats</a>
    <a href="#/h2h" data-route="h2h">Head-to-Head</a>
  </nav>
  <div class="meta" id="meta"></div>
</header>

<main>
  <div id="view-stats" class="view active">

    <div class="filter-bar" id="main-filter">
      <button data-filter="overall" class="active">Overall</button>
      <button data-filter="regular_season">Regular Season</button>
      <button data-filter="postseason">Postseason</button>
      <button data-filter="fantasy_bowl">Fantasy Bowl</button>
    </div>

    <section>
      <h2>Team Stats</h2>
      <table class="stat" id="main-table">
        <thead><tr id="main-head"></tr></thead>
        <tbody id="main-body"></tbody>
      </table>
    </section>

    <section>
      <h2>Postseason Performance</h2>
      <table class="stat" id="po-perf-table">
        <thead><tr id="po-perf-head"></tr></thead>
        <tbody id="po-perf-body"></tbody>
      </table>
    </section>

    <section>
      <h2>Most Points per Game (Top 10)</h2>
      <table class="stat">
        <thead><tr>
          <th>#</th><th>Team</th><th class="num">Score</th><th>Opponent</th><th class="num">Opp.</th>
          <th class="num">Season</th><th class="num">Week</th><th>Type</th><th></th>
        </tr></thead>
        <tbody id="top-scores-body"></tbody>
      </table>
    </section>

    <section>
      <h2>Champions History</h2>
      <table class="stat">
        <thead><tr>
          <th>Season</th><th>Champion</th><th class="num">Score</th><th>Runner-Up</th><th></th>
        </tr></thead>
        <tbody id="champions-body"></tbody>
      </table>
    </section>

    <section>
      <h2>Records</h2>
      <div class="subtab" id="records-tabs">
        <button data-record="highest" class="active">Highest Score</button>
        <button data-record="lowest">Lowest Score</button>
        <button data-record="blowouts">Biggest Blowouts</button>
        <button data-record="closest">Closest Games</button>
      </div>
      <table class="stat">
        <thead id="records-head"></thead>
        <tbody id="records-body"></tbody>
      </table>
    </section>

    <section>
      <h2>Streaks</h2>
      <div class="subtab" id="streaks-tabs">
        <button data-streak="win" class="active">Longest Win Streak</button>
        <button data-streak="loss">Longest Loss Streak</button>
      </div>
      <table class="stat">
        <thead><tr><th>#</th><th>Team</th><th class="num">Streak</th><th>Period</th></tr></thead>
        <tbody id="streaks-body"></tbody>
      </table>
    </section>

  </div>

  <div id="view-h2h" class="view">
    <section>
      <h2>Head-to-Head</h2>
      <div class="h2h-controls">
        <select id="h2h-a"></select>
        <span class="vs">VS</span>
        <select id="h2h-b"></select>
      </div>
      <div id="h2h-result"></div>
    </section>
  </div>
</main>

<script>
const DATA = __DATA__;

// ============== Utilities ==============
function teamColor(name) {
  let h = 0;
  for (let i = 0; i < name.length; i++) h = (h * 31 + name.charCodeAt(i)) | 0;
  const hue = Math.abs(h) % 360;
  return `hsl(${hue}, 55%, 65%)`;
}
function teamInitials(name) {
  return name.split(/\s+/).filter(Boolean).slice(0, 2).map(s => s[0].toUpperCase()).join('');
}
function teamCell(name, owner) {
  const ownerHtml = owner ? `<span class="team-owner">${escape(owner)}</span>` : '';
  return `<div class="team-cell">
    <span class="team-name">${escape(name)}</span>
    ${ownerHtml}
  </div>`;
}
function escape(s) {
  return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

const NFL_LEAGUE_ID = 3075160;
const FLEA_LEAGUE_ID = 338210;

function gameLink(season, week, type, team_id, game_id) {
  if (!season) return null;
  if (season <= 2022) {
    if (type === 'postseason') {
      return { href: `https://fantasy.nfl.com/league/${NFL_LEAGUE_ID}/history/${season}/playoffs`,
               platform: 'nfl', label: 'NFL.com Playoffs' };
    }
    if (team_id) {
      return { href: `https://fantasy.nfl.com/league/${NFL_LEAGUE_ID}/history/${season}/teamgamecenter?teamId=${team_id}&week=${week}`,
               platform: 'nfl', label: 'NFL.com Game Center' };
    }
    return { href: `https://fantasy.nfl.com/league/${NFL_LEAGUE_ID}/history/${season}/schedule?gameType=REG&week=${week || ''}`,
             platform: 'nfl', label: 'NFL.com' };
  } else {
    if (game_id) {
      return { href: `https://www.fleaflicker.com/nfl/leagues/${FLEA_LEAGUE_ID}/scores/${game_id}`,
               platform: 'flea', label: 'Fleaflicker Game' };
    }
    return { href: `https://www.fleaflicker.com/nfl/leagues/${FLEA_LEAGUE_ID}/scores?season=${season}&scoring_period=${week || 17}`,
             platform: 'flea', label: 'Fleaflicker' };
  }
}

function gameLinkIcon(season, week, type, team_id, game_id) {
  const link = gameLink(season, week, type, team_id, game_id);
  if (!link) return '';
  const text = link.platform === 'nfl' ? 'Game Center' : 'Box Score';
  return `<a class="game-link ${link.platform}" href="${link.href}" target="_blank" rel="noopener">${text} ↗</a>`;
}
function fmt(n, d = 0) {
  if (n === null || n === undefined) return '';
  return Number(n).toLocaleString('de-AT', { minimumFractionDigits: d, maximumFractionDigits: d });
}
function pct(n) {
  return (n * 100).toFixed(1) + '%';
}
function typeTag(type, round) {
  if (type === 'regular') return '';
  if (round && /championship|super bowl/i.test(round)) return '<span class="tag fb">Fantasy Bowl</span>';
  return '<span class="tag po">Postseason</span>';
}
function ownerOf(name) {
  const t = DATA.teams.find(x => x.name === name);
  return t ? t.owner : '';
}

// ============== Sortable Tables ==============
function renderSortable(headEl, bodyEl, columns, rows, state) {
  headEl.innerHTML = columns.map((c, i) => {
    const cls = (c.num ? 'num ' : '') + (state.sort === c.key ? 'sorted ' + (state.asc ? 'asc' : '') : '');
    return `<th data-col="${c.key}" class="${cls.trim()}">${c.label}</th>`;
  }).join('');

  // Sort
  const sorted = rows.slice();
  if (state.sort) {
    const col = columns.find(c => c.key === state.sort);
    sorted.sort((a, b) => {
      let va = a[state.sort], vb = b[state.sort];
      if (typeof va === 'string') return state.asc ? va.localeCompare(vb) : vb.localeCompare(va);
      return state.asc ? (va - vb) : (vb - va);
    });
  }

  bodyEl.innerHTML = sorted.map((r, idx) => {
    const cls = r.active === false ? 'inactive' : '';
    const tds = columns.map(c => {
      if (c.render) return `<td class="${c.num ? 'num' : ''}">${c.render(r, idx)}</td>`;
      const v = r[c.key];
      return `<td class="${c.num ? 'num' : ''}">${c.format ? c.format(v, r) : escape(v ?? '')}</td>`;
    }).join('');
    return `<tr class="${cls}">${tds}</tr>`;
  }).join('');

  headEl.querySelectorAll('th').forEach(th => {
    th.addEventListener('click', () => {
      const col = th.dataset.col;
      if (state.sort === col) state.asc = !state.asc;
      else { state.sort = col; state.asc = !!columns.find(c => c.key === col)?.defaultAsc; }
      renderSortable(headEl, bodyEl, columns, rows, state);
    });
  });
}

// ============== Main Stats Table ==============
const mainColumns = [
  { key: 'team', label: 'Team', render: (r, i) => `<div class="team-cell"><span class="rank">${i + 1}</span><span class="team-name">${escape(r.team)}</span></div>`, defaultAsc: true },
  { key: 'seasons', label: 'Seasons', num: true },
  { key: 'games', label: 'Games', num: true },
  { key: 'wins', label: 'W', num: true },
  { key: 'losses', label: 'L', num: true },
  { key: 'ties', label: 'T', num: true },
  { key: 'pct', label: 'Pct', num: true, format: v => fmt(v, 3) },
  { key: 'points', label: 'Points', num: true, format: v => fmt(v, 2) },
  { key: 'avg_pg', label: 'AvgPpG', num: true, format: v => fmt(v, 2) },
  { key: 'avg_ps', label: 'AvgPpS', num: true, format: v => fmt(v, 2) },
];
const mainState = { sort: 'wins', asc: false };
let mainFilter = 'overall';
function renderMain() {
  renderSortable(
    document.getElementById('main-head'),
    document.getElementById('main-body'),
    mainColumns,
    DATA.stats[mainFilter] || [],
    mainState
  );
}
document.querySelectorAll('#main-filter button').forEach(b => {
  b.addEventListener('click', () => {
    document.querySelectorAll('#main-filter button').forEach(x => x.classList.remove('active'));
    b.classList.add('active');
    mainFilter = b.dataset.filter;
    renderMain();
  });
});

// ============== Postseason Performance ==============
const poPerfColumns = [
  { key: 'team', label: 'Team', render: (r, i) => `<div class="team-cell"><span class="rank">${i + 1}</span><span class="team-name">${escape(r.team)}</span></div>`, defaultAsc: true },
  { key: 'seasons', label: 'Seasons', num: true },
  { key: 'playoffs', label: 'Playoffs', num: true, format: (v, r) => `${v} <span class="pct">${pct(r.playoffs_pct)}</span>` },
  { key: 'division_titles', label: 'Div Titles', num: true, format: (v, r) => `${v} <span class="pct">${pct(r.division_titles_pct)}</span>` },
  { key: 'first_bye', label: '1st Round Bye', num: true, format: (v, r) => `${v} <span class="pct">${pct(r.first_bye_pct)}</span>` },
  { key: 'first_overall', label: '1st Overall', num: true, format: (v, r) => `${v} <span class="pct">${pct(r.first_overall_pct)}</span>` },
];
const poPerfState = { sort: 'playoffs', asc: false };
renderSortable(
  document.getElementById('po-perf-head'),
  document.getElementById('po-perf-body'),
  poPerfColumns,
  DATA.postseason_perf,
  poPerfState
);

// ============== Top Scores ==============
document.getElementById('top-scores-body').innerHTML = DATA.top_scores.map((s, i) => `
  <tr>
    <td><span class="rank">${i + 1}</span></td>
    <td>${teamCell(s.team)}</td>
    <td class="num"><span class="win-pill">${fmt(s.score, 2)}</span></td>
    <td>${teamCell(s.opponent)}</td>
    <td class="num">${fmt(s.opp_score, 2)}</td>
    <td class="num">${s.season}</td>
    <td class="num">Wk ${s.week}</td>
    <td>${typeTag(s.type, s.round)}</td>
    <td>${gameLinkIcon(s.season, s.week, s.type, s.team_id, s.game_id)}</td>
  </tr>
`).join('');

// ============== Champions ==============
document.getElementById('champions-body').innerHTML = DATA.champions.map(c => {
  const score = c.score ? `<span class="win-pill">${fmt(c.score[0], 2)}</span> – ${fmt(c.score[1], 2)}` : '';
  return `<tr>
    <td><strong>${c.season}</strong></td>
    <td>${c.champion ? teamCell(c.champion) : '?'}</td>
    <td class="num">${score}</td>
    <td>${c.runner_up ? teamCell(c.runner_up) : '?'}</td>
    <td>${gameLinkIcon(c.season, null, 'postseason')}</td>
  </tr>`;
}).join('');

// ============== Records ==============
const recordHeaders = {
  highest: ['#','Team','Score','Opponent','Opp.','Season','Week','Type',''],
  lowest:  ['#','Team','Score','Opponent','Opp.','Season','Week','Type',''],
  blowouts:['#','Winner','Score','Loser','Score','Margin','Season','Week','Type',''],
  closest: ['#','Team A','Score','Team B','Score','Margin','Season','Week','Type',''],
};
function renderRecords(kind) {
  const NUMERIC_HEADERS = new Set(['Score','Opp.','Margin','Season','Week']);
  document.getElementById('records-head').innerHTML = '<tr>' +
    recordHeaders[kind].map(h => `<th${NUMERIC_HEADERS.has(h) ? ' class="num"' : ''}>${h}</th>`).join('') + '</tr>';
  const rows = DATA.records[kind] || [];
  const body = document.getElementById('records-body');
  if (kind === 'highest' || kind === 'lowest') {
    body.innerHTML = rows.map((r, i) => `<tr>
      <td><span class="rank">${i + 1}</span></td>
      <td>${teamCell(r.team)}</td>
      <td class="num"><span class="win-pill">${fmt(r.score, 2)}</span></td>
      <td>${teamCell(r.opponent)}</td>
      <td class="num">${fmt(r.opp_score, 2)}</td>
      <td class="num">${r.season}</td>
      <td class="num">Wk ${r.week}</td>
      <td>${typeTag(r.type, r.round)}</td>
      <td>${gameLinkIcon(r.season, r.week, r.type, r.team_id, r.game_id)}</td>
    </tr>`).join('');
  } else if (kind === 'blowouts' || kind === 'closest') {
    body.innerHTML = rows.map((r, i) => {
      const a = kind === 'blowouts' ? r.winner : (r.winner || r.team_a);
      const b = kind === 'blowouts' ? r.loser : (r.loser || r.team_b);
      const as = r.winner_score ?? r.score_a;
      const bs = r.loser_score ?? r.score_b;
      return `<tr>
        <td><span class="rank">${i + 1}</span></td>
        <td>${teamCell(a)}</td>
        <td class="num"><span class="win-pill">${fmt(as, 2)}</span></td>
        <td>${teamCell(b)}</td>
        <td class="num">${fmt(bs, 2)}</td>
        <td class="num">${fmt(r.margin, 2)}</td>
        <td class="num">${r.season}</td>
        <td class="num">Wk ${r.week}</td>
        <td>${typeTag(r.type, r.round)}</td>
        <td>${gameLinkIcon(r.season, r.week, r.type, r.winner_id || r.team_a_id, r.game_id)}</td>
      </tr>`;
    }).join('');
  }
}
document.querySelectorAll('#records-tabs button').forEach(b => {
  b.addEventListener('click', () => {
    document.querySelectorAll('#records-tabs button').forEach(x => x.classList.remove('active'));
    b.classList.add('active');
    renderRecords(b.dataset.record);
  });
});

// ============== Streaks ==============
function renderStreaks(kind) {
  document.getElementById('streaks-body').innerHTML = DATA.streaks[kind].map((s, i) => `<tr>
    <td><span class="rank">${i + 1}</span></td>
    <td>${teamCell(s.team)}</td>
    <td class="num"><span class="win-pill">${s.streak}</span></td>
    <td>${escape(s.from)} – ${escape(s.to)}</td>
  </tr>`).join('');
}
document.querySelectorAll('#streaks-tabs button').forEach(b => {
  b.addEventListener('click', () => {
    document.querySelectorAll('#streaks-tabs button').forEach(x => x.classList.remove('active'));
    b.classList.add('active');
    renderStreaks(b.dataset.streak);
  });
});

// ============== H2H ==============
function buildH2HSelectors() {
  const teams = DATA.teams.map(t => t.name).sort();
  const optHtml = teams.map(t => `<option value="${escape(t)}">${escape(t)}</option>`).join('');
  const a = document.getElementById('h2h-a');
  const b = document.getElementById('h2h-b');
  a.innerHTML = optHtml;
  b.innerHTML = optHtml;
  a.value = teams[0];
  b.value = teams[1] || teams[0];
  a.addEventListener('change', renderH2H);
  b.addEventListener('change', renderH2H);
}
function renderH2H() {
  const a = document.getElementById('h2h-a').value;
  const b = document.getElementById('h2h-b').value;
  const out = document.getElementById('h2h-result');
  if (a === b) {
    out.innerHTML = `<div class="h2h-empty">Bitte zwei verschiedene Teams waehlen.</div>`;
    return;
  }
  const h = DATA.h2h[a]?.[b];
  if (!h || h.games.length === 0) {
    out.innerHTML = `<div class="h2h-empty">${escape(a)} und ${escape(b)} haben nie gegeneinander gespielt.</div>`;
    return;
  }

  const aWins = h.wins, aLosses = h.losses, aTies = h.ties;
  const bSide = DATA.h2h[b]?.[a] || { pf: 0, pa: 0 };

  // Summary header
  let html = `<div class="h2h-summary">
    <div class="h2h-side left">
      <div class="h2h-team">${teamCell(a, ownerOf(a))}</div>
      <div class="h2h-record ${aWins > aLosses ? 'win' : (aWins < aLosses ? 'loss' : '')}">${aWins}</div>
      <div class="h2h-points">${fmt(h.pf, 2)} Pkt total / ${fmt(h.pf / h.games.length, 2)} avg</div>
    </div>
    <div class="h2h-vs">VS<br><span style="font-size:11px">${h.games.length} Spiele${aTies ? ' / ' + aTies + ' T' : ''}</span></div>
    <div class="h2h-side right">
      <div class="h2h-team">${teamCell(b, ownerOf(b))}</div>
      <div class="h2h-record ${aLosses > aWins ? 'win' : (aLosses < aWins ? 'loss' : '')}">${aLosses}</div>
      <div class="h2h-points">${fmt(h.pa, 2)} Pkt total / ${fmt(h.pa / h.games.length, 2)} avg</div>
    </div>
  </div>`;

  // Game list
  html += `<table class="stat">
    <thead><tr>
      <th class="num">Season</th><th class="num">Week</th><th class="num">${escape(a)}</th>
      <th></th><th class="num">${escape(b)}</th><th>Type</th><th></th>
    </tr></thead><tbody>`;
  for (const g of h.games) {
    let aClass = 'score-loser', bClass = 'score-loser', sep = '–';
    if (g.sf > g.sa) { aClass = 'score-winner'; }
    else if (g.sf < g.sa) { bClass = 'score-winner'; }
    else { aClass = bClass = 'score-tie'; }
    html += `<tr>
      <td>${g.season}</td>
      <td>Wk ${g.week}</td>
      <td class="num"><span class="${aClass}">${fmt(g.sf, 2)}</span></td>
      <td class="num" style="color:var(--text-muted)">${sep}</td>
      <td class="num"><span class="${bClass}">${fmt(g.sa, 2)}</span></td>
      <td>${typeTag(g.type, g.round)}</td>
      <td>${gameLinkIcon(g.season, g.week, g.type, g.team_id, g.game_id)}</td>
    </tr>`;
  }
  html += '</tbody></table>';
  out.innerHTML = html;
}

// ============== Hash Routing ==============
function handleRoute() {
  const hash = (location.hash || '#/').replace(/^#/, '');
  const isH2H = hash.startsWith('/h2h');
  document.getElementById('view-stats').classList.toggle('active', !isH2H);
  document.getElementById('view-h2h').classList.toggle('active', isH2H);
  document.querySelectorAll('header nav a').forEach(a => {
    a.classList.toggle('active', (a.dataset.route === 'h2h') === isH2H);
  });
  if (isH2H) renderH2H();
}
window.addEventListener('hashchange', handleRoute);

// ============== Init ==============
document.getElementById('meta').innerHTML =
  `<span>${DATA.meta.seasons[0]}–${DATA.meta.seasons[DATA.meta.seasons.length - 1]} \u00b7 ${DATA.meta.total_games.toLocaleString('de-AT')} Spiele</span>` +
  `<span class="last-update">Last update: <strong>${DATA.meta.generated.slice(0, 16).replace('T', ' ')}</strong></span>`;
renderMain();
renderRecords('highest');
renderStreaks('win');
buildH2HSelectors();
handleRoute();
</script>
</body>
</html>"""


def main():
    if not STATS_FILE.exists():
        print(f"❌ {STATS_FILE.name} nicht gefunden – zuerst 05_aggregate.py laufen lassen")
        return

    stats = json.loads(STATS_FILE.read_text(encoding='utf-8'))
    data_json = json.dumps(stats, ensure_ascii=False, separators=(',', ':'))
    html = HTML.replace('__DATA__', data_json)
    OUTPUT_FILE.write_text(html, encoding='utf-8')
    size_kb = OUTPUT_FILE.stat().st_size / 1024
    print(f"index.html geschrieben ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
