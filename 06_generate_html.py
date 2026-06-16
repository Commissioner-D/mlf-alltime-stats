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
header .logo { height: 32px; width: auto; opacity: 0.9; }
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
  <img src="data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz4KPHN2ZyBpZD0iRWJlbmVfMSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiB2ZXJzaW9uPSIxLjEiIHZpZXdCb3g9IjAgMCA3MDUuOTggNDAwLjU2Ij4KICA8IS0tIEdlbmVyYXRvcjogQWRvYmUgSWxsdXN0cmF0b3IgMzAuNS4xLCBTVkcgRXhwb3J0IFBsdWctSW4gLiBTVkcgVmVyc2lvbjogMi4xLjQgQnVpbGQgMykgIC0tPgogIDxkZWZzPgogICAgPHN0eWxlPgogICAgICAuc3QwIHsKICAgICAgICBmaWxsOiBub25lOwogICAgICAgIHN0cm9rZTogIzAwMDsKICAgICAgICBzdHJva2UtbWl0ZXJsaW1pdDogMTA7CiAgICAgIH0KCiAgICAgIC5zdDEgewogICAgICAgIGZpbGw6ICNiMDhmMjY7CiAgICAgIH0KCiAgICAgIC5zdDIgewogICAgICAgIGZpbGw6ICNmZmY7CiAgICAgIH0KCiAgICAgIC5zdDMgewogICAgICAgIGZpbGw6ICNkNGFmMTQ7CiAgICAgIH0KCiAgICAgIC5zdDQgewogICAgICAgIGZpbGw6ICNkYWIyMDA7CiAgICAgIH0KICAgIDwvc3R5bGU+CiAgPC9kZWZzPgogIDxwYXRoIGQ9Ik0yMTUuNiwzNzYuODJjNy41OS0uNTgsMTEuMy0uODUsMTguODktMS4zNSw3LjktLjUyLDE0Ljg3LTQuMTcsMTkuNzYtOS42Nyw1LjI3LDQuNzYsMTIuMTcsNy40OCwxOS40NCw3LjQ4LjQyLDAsLjgzLDAsMS4yNS0uMDMsOC4yLS4zNSwxMi4yLS41LDIwLjQxLS43Niw4Ljg5LS4yOCwxNi43My00LjU0LDIxLjg1LTExLjAzLDUuMzIsNi4yMywxMy4yMywxMC4xNywyMi4wNSwxMC4xN2guMjFjNS4zNS0uMDQsOC42Ni0uMDUsMTIuMjItLjA1LDIuNDEsMCw0Ljk2LDAsOC4xMS4wMmguMTJsMjIuMjkuMjRjOC43MS4xNiwxMi45NC4yNiwyMS41NS41My4zMSwwLC42MS4wMS45Mi4wMSwxMi4zOSwwLDIzLjQ2LTcuODksMjcuNDYtMTkuNy40LTEuMTkuNzgtMi4zMiwxLjE1LTMuMzkuNywyLjAxLDEuNDUsNC4xNywyLjMsNi42LDMuODMsMTAuOTMsMTMuNzksMTguNTQsMjUuMzUsMTkuMzUsOC44NS42MiwxMy4xNS45NSwyMS45MSwxLjcuODMuMDcsMS42NS4xMSwyLjQ4LjExLDQuNzYsMCw5LjQtMS4xOCwxMy41Mi0zLjM2LDguOTcsNS4xMywxOS4yLDguNDgsMzAuMzEsOS44Niw0LjczLjU5LDkuMDkuODcsMTMuMzMuODcsMTUuOTcsMCwyOS4zNi00LjIyLDM5Ljc4LTEyLjUzLDIuNjEtMi4wOCw1LTQuMzgsNy4xNi02Ljg1di41N2MtLjIzLDE0LjEzLDkuNzYsMjYuMzcsMjMuNjQsMjguOTgsOC4xNSwxLjUzLDEyLjEyLDIuMzEsMjAuMjIsMy45NywxLjkzLjQsMy44OC41OSw1LjgyLjU5LDYuNTYsMCwxMi45OS0yLjIzLDE4LjE5LTYuNDIsNi43NC01LjQzLDEwLjctMTMuNTgsMTAuOC0yMi4yMi4xNy0xMy42OS4zMy0yNy4zOC40OS00MS4wOCw3LjMtMTIuMTgsMTQuNTUtMjQuNDYsMjEuNTktMzYuNCwzLjkyLTYuNjQsNy44My0xMy4yOCwxMS43Ni0xOS45MSw0LjkyLTguMzEsNS4zOS0xOC41MiwxLjI0LTI3LjI0cy0xMi4zNi0xNC44MS0yMS45MS0xNi4yM2MtOC4yNy0xLjIzLTEyLjgyLTEuOTEtMjEuMDktMy4xLDIuMzgtNy45NSwxLjMxLTE2LjcxLTMuMzQtMjMuOThsLTEzLjk1LTIxLjc1LDEwLjctOS40MWM3Ljk3LTcuMDEsMTEuNDgtMTcuODIsOS4xNC0yOC4xNy0yLjM0LTEwLjM1LTEwLjE1LTE4LjYtMjAuMzYtMjEuNS0xLjQ3LS40Mi0zNi42NC0xMC4zMy05NS40LTIwLjI3LS41Mi0uMDktMS4wMy0uMTQtMS41NS0uMiwyLjMzLTEuMjQsNC44NS0yLjU3LDcuNzQtNC4wOSwxMS4yLTUuOSwxNy4yOS0xOC4zOCwxNS4wMy0zMC44NC0yLjI2LTEyLjQ2LTEyLjM0LTIyLjAxLTI0LjktMjMuNi01LjUtLjctOS45NS0xLjI0LTE0LjE5LTEuNzQtLjg5LTMuNzYtMS44NC03Ljc0LTMuMDEtMTIuNi0yLjktMTIuMDMtMTMuMTEtMjAuOS0yNS40My0yMi4wOC0uOTMtLjA5LTEuODYtLjEzLTIuNzgtLjEzLTExLjI3LDAtMjEuNjQsNi41Ny0yNi4zOCwxNi45OC0yLjA3LDQuNTQtMy43Niw4LjI3LTUuMzUsMTEuOC00LjI0LS4zMS04LjcxLS42Mi0xNC4yMy0uOTgtLjY0LS4wNC0xLjI3LS4wNi0xLjkxLS4wNi0uMTcsMC0uMzQuMDItLjUxLjAyLS44My0uMTItMS42Ni0uMjItMi41LS4yNy01LjUyLS4zNC05Ljk4LS42MS0xNC4yMi0uODQtMS4xMi0zLjY5LTIuMzItNy42LTMuOC0xMi4zNy0zLjY1LTExLjgzLTE0LjQxLTIwLjAzLTI2Ljc4LTIwLjQzLS4zMSwwLS42MiwwLS45MywwLTEyLDAtMjIuODEsNy40MS0yNy4xLDE4LjY5LTEuNzcsNC42Ni0zLjIyLDguNDktNC41OCwxMi4xLTQuMjUtLjA0LTguNzEtLjA3LTE0LjIzLS4wOGgtLjA1Yy0uODIsMC0xLjYzLjA0LTIuNDQuMTEtLjc0LS4wNi0xLjQ4LS4xLTIuMjQtLjExaC0uMThjLTUuNTIsMC05Ljk5LjAzLTE0LjIzLjA3LTEuMzUtMy42Mi0yLjgtNy40NC00LjU3LTEyLjExLTQuMjktMTEuMjgtMTUuMS0xOC43LTI3LjEtMTguNy0uMzEsMC0uNjEsMC0uOTIsMC0xMi4zNy4zOS0yMy4xMyw4LjU5LTI2Ljc5LDIwLjQxLTEuNDcsNC43Ny0yLjY4LDguNjgtMy44LDEyLjM3LTQuMjQuMjMtOC43LjQ5LTE0LjIyLjgzLS45NS4wNi0xLjg5LjE4LTIuODEuMzMtLjMyLDAtLjY0LS4wMy0uOTctLjAzaC0uNzZjLS40OCwwLS45NS4wNC0xLjQzLjA3LTUuMzkuMzUtOS43OC42NS0xMy45NS45Ni0xLjU5LTMuNTItMy4yOC03LjI1LTUuMzUtMTEuOC00Ljc0LTEwLjQxLTE1LjExLTE2Ljk4LTI2LjM4LTE2Ljk4LS45MiwwLTEuODUuMDQtMi43OC4xMy0xMi4zMiwxLjE4LTIyLjUzLDEwLjA1LTI1LjQzLDIyLjA4LTEuMTcsNC44NS0yLjEyLDguODQtMy4wMSwxMi42LTQuMjQuNS04LjY4LDEuMDUtMTQuMTksMS43NC0xMi41NiwxLjU5LTIyLjY0LDExLjE0LTI0LjksMjMuNi0yLjI2LDEyLjQ2LDMuODMsMjQuOTQsMTUuMDMsMzAuODQsMi44OCwxLjUxLDUuMzksMi44NCw3LjcxLDQuMDgtLjcuMDgtMS4zOS4xNy0yLjA3LjMtNTguNDMsOS45LTkzLjM5LDE5Ljc2LTk0Ljg1LDIwLjE3LTEwLjIxLDIuOS0xOC4wMiwxMS4xNS0yMC4zNiwyMS41czEuMTYsMjEuMTYsOS4xNCwyOC4xN2wxMC43LDkuNDEtMTMuOTUsMjEuNzVjLTQuNDEsNi44OC01LjYxLDE1LjExLTMuNywyMi43MS03LjQsMS41Mi0xNC43MSwzLjExLTIxLjk4LDQuNzgtMTMuMTgsMy4wOC0yMi41MiwxNC44MS0yMi41MiwyOC4zMnYxMTMuMjJjMCw4LjU4LDMuODIsMTYuNzIsMTAuNCwyMi4yMyw1LjI2LDQuNCwxMS44Niw2Ljc2LDE4LjYxLDYuNzYsMS43LDAsMy40LS4xNSw1LjEtLjQ1LDguMzctMS40OSwxMi40NS0yLjIsMjAuNzctMy41OSwxMC4xNy0xLjcsMTguMzQtOC41NiwyMi4wNS0xNy42MS4xLjEyLjE5LjI0LjI5LjM1LDUuNTUsNi40NSwxMy42LDEwLjA4LDIxLjk4LDEwLjA4LDEuMzQsMCwyLjY5LS4wOSw0LjA1LS4yOCw4Ljc3LTEuMjQsMTMuMDYtMS44MSwyMS44MS0yLjk0LDExLjYtMS40OSwyMS4xNi05LjgsMjQuMjYtMjEuMDguNjgtMi40OCwxLjM3LTQuOTksMi4wNy03LjUzLjUyLDEuMywxLjA4LDIuNjcsMS42OCw0LjE1LDQuNDYsMTEuMDMsMTUuMTYsMTguMTIsMjYuODcsMTguMTIuOTIsMCwxLjg1LS4wNCwyLjc4LS4xMyw4Ljg1LS44NSwxMy4xOC0xLjIzLDIyLjAzLTEuOTdsMTAuODctLjg3aC0uMDJaIi8+CiAgPHBhdGggY2xhc3M9InN0MCIgZD0iTTIyNy4zOCw3NS40NCIvPgogIDxnPgogICAgPHBhdGggY2xhc3M9InN0MSIgZD0iTTEwMC4wMiwxNzUuNTJsLTI3LjQxLDQyLjczczM1LjI0LTEwLjk1LDkyLjgtMjAuNzFsLTM5LjctNDEuOTMsMzcuMi0yNS41MmMtNTcuODcsOS43OC05Mi4zMSwxOS41Ny05Mi4zMSwxOS41N2wyOS40MSwyNS44NmgwWiIvPgogICAgPHBhdGggY2xhc3M9InN0MSIgZD0iTTYwNS4wMiwxNzUuNTJsMjcuNDEsNDIuNzNzLTM1LjI0LTEwLjk1LTkyLjgtMjAuNzFsMzkuNy00MS45My0zNy4yLTI1LjUyYzU3Ljg3LDkuNzgsOTIuMzEsMTkuNTcsOTIuMzEsMTkuNTdsLTI5LjQxLDI1Ljg2aC0uMDFaIi8+CiAgICA8cGF0aCBjbGFzcz0ic3QzIiBkPSJNMTI1LjcxLDIxNS40MnMyMDcuMjYtNDAuMjEsNDUzLjY5LDB2LTU5LjhjLTI0Ni40NC00MC4yMS00NTMuNjksMC00NTMuNjksMHY1OS44aDBaIi8+CiAgPC9nPgogIDxnPgogICAgPHBhdGggY2xhc3M9InN0NCIgZD0iTTMwNC41MywyOS4wM2M0LjczLDEyLjQ1LDcuMDUsMTguNjksMTEuNiwzMS4xOCwxMy43NC0uMzMsMjAuNjEtLjQyLDM0LjM1LS40NC0xMS4xMSw3LjgtMTYuNTksMTEuNzUtMjcuNCwxOS43Niw0LjQ0LDEyLjUxLDYuNjIsMTguNzgsMTAuODgsMzEuMzItMTAuODQtNy42NS0xNi4zMy0xMS40Mi0yNy40NS0xOC44Ni0xMC42Myw4LjEyLTE1Ljg4LDEyLjI0LTI2LjIxLDIwLjU1LDMuNDctMTIuNzksNS4yNC0xOS4xOCw4Ljg5LTMxLjk0LTExLjMtNy4zMS0xNy4wMi0xMC45MS0yOC42LTE3Ljk5LDEzLjcyLS44NSwyMC41OS0xLjE5LDM0LjMyLTEuNzIsMy43Ni0xMi43NSw1LjY4LTE5LjEyLDkuNjItMzEuODVoMFoiLz4KICAgIDxwYXRoIGNsYXNzPSJzdDQiIGQ9Ik00MDEuMjgsMjkuMDVjMy45MywxMi43Myw1Ljg1LDE5LjEsOS42LDMxLjg2LDEzLjczLjU0LDIwLjYuODgsMzQuMzIsMS43NC0xMS41OCw3LjA4LTE3LjMxLDEwLjY4LTI4LjYxLDE3Ljk4LDMuNjQsMTIuNzcsNS40MiwxOS4xNiw4Ljg4LDMxLjk1LTEwLjMzLTguMzItMTUuNTctMTIuNDMtMjYuMi0yMC41Ni0xMS4xMyw3LjQzLTE2LjYyLDExLjItMjcuNDYsMTguODUsNC4yNy0xMi41NCw2LjQ1LTE4LjgsMTAuOS0zMS4zMS0xMC44MS04LjAxLTE2LjI5LTExLjk2LTI3LjM5LTE5Ljc3LDEzLjc0LjAzLDIwLjYxLjEyLDM0LjM1LjQ2LDQuNTYtMTIuNDksNi44OC0xOC43MiwxMS42Mi0zMS4xOHYtLjAyWiIvPgogICAgPHBhdGggY2xhc3M9InN0NCIgZD0iTTQ5Ny44OSwzNS4yMmMzLjEyLDEyLjk1LDQuNjMsMTkuNDMsNy41NywzMi40LDEzLjY5LDEuNDEsMjAuNTIsMi4xOSwzNC4xOCwzLjkyLTEyLjAzLDYuMzMtMTcuOTcsOS41NS0yOS43MywxNi4xMiwyLjgzLDEyLjk3LDQuMiwxOS40Niw2Ljg0LDMyLjQ1LTkuOC04Ljk2LTE0Ljc3LTEzLjQtMjQuODgtMjIuMTktMTEuNTksNi43MS0xNy4zMSwxMC4xMy0yOC42MiwxNy4wNiw1LjA2LTEyLjI1LDcuNjMtMTguMzYsMTIuODctMzAuNTYtMTAuMjktOC42OC0xNS41MS0xMi45OC0yNi4xLTIxLjQ3LDEzLjcyLjksMjAuNTgsMS40MywzNC4yOCwyLjY0LDUuMzUtMTIuMTcsOC4wNi0xOC4yNSwxMy41OS0zMC4zOGgwWiIvPgogICAgPHBhdGggY2xhc3M9InN0NCIgZD0iTTIwNy4xNSwzNS4yMmM1LjUyLDEyLjEzLDguMjQsMTguMiwxMy41OSwzMC4zOCwxMy43LTEuMjEsMjAuNTYtMS43NCwzNC4yOC0yLjY0LTEwLjU5LDguNS0xNS44MSwxMi43OS0yNi4xLDIxLjQ3LDUuMjQsMTIuMiw3LjgxLDE4LjMxLDEyLjg3LDMwLjU2LTExLjMxLTYuOTQtMTcuMDQtMTAuMzUtMjguNjItMTcuMDYtMTAuMSw4Ljc5LTE1LjA4LDEzLjIzLTI0Ljg4LDIyLjE5LDIuNjUtMTIuOTgsNC4wMS0xOS40Nyw2Ljg0LTMyLjQ1LTExLjc2LTYuNTctMTcuNy05Ljc5LTI5LjczLTE2LjEyLDEzLjY2LTEuNzMsMjAuNS0yLjUxLDM0LjE4LTMuOTIsMi45NC0xMi45Nyw0LjQ1LTE5LjQ1LDcuNTctMzIuNGgwWiIvPgogIDwvZz4KICA8ZyBmaWxsPSIjZThlOGU4Ij4KICAgIDxwYXRoIGQ9Ik0xNDguNjMsMTk4LjIzYy0yLjU5LTEwLjMzLTMuODktMTUuNDUtNi41LTI1LjU3djI4LjczYzAsMS41OS0uMzUsMi44My0xLjA0LDMuNzItLjY5Ljg5LTEuNjEsMS40MS0yLjc2LDEuNTctMS4xMS4xNS0yLjAyLS4xMS0yLjcyLS43OS0uNzEtLjY4LTEuMDYtMS44MS0xLjA2LTMuNHYtMzIuNTZjMC0xLjguNDYtMy4xLDEuMzktMy45Mi45My0uODIsMi4xOC0xLjM5LDMuNzUtMS43LDEuMDItLjIsMS41My0uMzEsMi41NS0uNTEsMS41My0uMywyLjY0LS4zNywzLjM0LS4yMnMxLjIuNTcsMS41MywxLjI1LjcxLDEuODIsMS4xMywzLjQyYzIuMzUsOC43NywzLjUzLDEzLjE5LDUuODcsMjIuMSwyLjM0LTkuNiwzLjUyLTE0LjQzLDUuODUtMjQuMTMuNDItMS43Ny44LTMuMDYsMS4xMi0zLjg3LjMzLS44MS44NC0xLjQyLDEuNTItMS44Mi42OC0uNCwxLjc4LS43MywzLjMtLjk4LDEuMDEtLjE2LDEuNTEtLjI0LDIuNTEtLjQsMS41NS0uMjUsMi43Ny0uMTEsMy42OC40LjkxLjUxLDEuMzYsMS43MSwxLjM2LDMuNTl2MzMuOThjMCwxLjY0LS4zNCwyLjkxLTEuMDIsMy44Mi0uNjguOTEtMS42LDEuNDMtMi43NCwxLjU3LTEuMDcuMTQtMS45Ni0uMTYtMi42NS0uODktLjY5LS43My0xLjA0LTEuOTEtMS4wNC0zLjU0di0yOS40OWMtMi41NywxMS4yOC0zLjg2LDE2LjkxLTYuNDQsMjguMDktLjQyLDEuODItLjc2LDMuMTUtMS4wMyw0LjAxLS4yNi44Ni0uNzYsMS42Ny0xLjQ3LDIuNDRzLTEuNywxLjI0LTIuOTcsMS40Yy0uOTUuMTMtMS43Ni4wMi0yLjQyLS4zMnMtMS4xOC0uODItMS41NC0xLjQ0Yy0uMzctLjYyLS42Ni0xLjMyLS44Ny0yLjEtLjIxLS43OC0uNDMtMS42LS42NS0yLjQ0aC4wMloiLz4KICAgIDxwYXRoIGQ9Ik0yMDcuMSwxOTIuNDdjLS43NS0yLjEtMS4xMy0zLjE1LTEuODgtNS4yNC02LjQxLjctOS42MywxLjA3LTE2LjA4LDEuODUtLjc2LDIuMzEtMS4xNCwzLjQ3LTEuODksNS43Ny0uNzQsMi4yNS0xLjM3LDMuNzktMS45LDQuNjEtLjUyLjgyLTEuMzgsMS4zLTIuNTgsMS40NC0xLjAxLjEyLTEuOTEtLjE3LTIuNjktLjg4cy0xLjE3LTEuNTctMS4xNy0yLjU5YzAtLjU5LjA5LTEuMjEuMjctMS44Ni4xOC0uNjUuNDgtMS41Ni45LTIuNzMsNC4wNy0xMS43MSw2LjExLTE3LjU5LDEwLjE2LTI5LjM1LjI5LS44NC42NC0xLjg2LDEuMDQtMy4wNC40MS0xLjE4Ljg0LTIuMTgsMS4zLTIuOTkuNDYtLjgxLDEuMDYtMS40OSwxLjgxLTIuMDQuNzUtLjU2LDEuNjctLjksMi43Ny0xLjA0LDEuMTItLjE0LDIuMDUsMCwyLjc5LjM2Ljc0LjM4LDEuMzUuOSwxLjgsMS41OC40Ni42OC44NCwxLjQyLDEuMTYsMi4yMi4zMS44LjcxLDEuODgsMS4yLDMuMjIsNC4xMiwxMC43NCw2LjE4LDE2LjEyLDEwLjI5LDI2LjkuOCwyLjA1LDEuMjEsMy41NiwxLjIxLDQuNTJzLS4zOCwxLjk3LTEuMTQsMi44OGMtLjc2LjkyLTEuNjgsMS40My0yLjc1LDEuNTUtLjYzLjA3LTEuMTYsMC0xLjYxLS4ycy0uODItLjQ5LTEuMTMtLjg5Yy0uMy0uMzktLjYzLTEuMDEtLjk4LTEuODUtLjM1LS44NC0uNjUtMS41OC0uOS0yLjIzdi4wM1pNMTkxLjI1LDE4Mi4yNGM0Ljc0LS41Nyw3LjEtLjg1LDExLjgxLTEuMzgtMi4zOC02LjktMy41Ny0xMC4zNC01Ljk1LTE3LjIxLTIuMzQsNy40NC0zLjUxLDExLjE2LTUuODYsMTguNTloMFoiLz4KICAgIDxwYXRoIGQ9Ik0yNDQuMTgsMTU1LjI3djIyLjU2YzAsMS45Ni0uMDgsMy42My0uMjMsNS4wMS0uMTUsMS4zOC0uNDksMi44LTEuMDMsNC4yNi0uODksMi40NC0yLjM1LDQuNDItNC40LDUuOTItMi4wNCwxLjUxLTQuNTMsMi40LTcuNDcsMi42Ny0yLjY1LjI1LTQuODYsMC02LjY0LS43NS0xLjc3LS43NS0zLjIxLTIuMTEtNC4yOS00LjA3LS41Ny0xLjA1LTEuMDMtMi4yNy0xLjM5LTMuNjgtLjM2LTEuNC0uNTQtMi43Ni0uNTQtNC4wNiwwLTEuMzguMzUtMi40NywxLjA0LTMuMjcuNy0uOCwxLjU5LTEuMjUsMi42OC0xLjM2LDEuMDUtLjEsMS44NS4xNiwyLjM4Ljc4cy45NSwxLjYyLDEuMjMsMy4wMmMuMywxLjQ5LjYxLDIuNjcuOTEsMy41NXMuODEsMS42MSwxLjUyLDIuMTksMS43My44MSwzLjA0LjY5YzMuNTEtLjMyLDUuMjYtMy4zMSw1LjI2LTguOTl2LTIzLjg5YzAtMS43Ny4zNS0zLjEyLDEuMDUtNC4wNnMxLjY2LTEuNDUsMi44Ni0xLjU0YzEuMjMtLjA5LDIuMi4yOCwyLjkyLDEuMTIuNzIuODMsMS4wOCwyLjEzLDEuMDgsMy44OWguMDJaIi8+CiAgICA8cGF0aCBkPSJNMjY5Ljg4LDE0OC41NWM0LjAzLS4xOCw3LjUuNTgsMTAuMzksMi4yNXM1LjA4LDQuMTIsNi41Nyw3LjMzYzEuNDksMy4yMSwyLjIzLDcuMDEsMi4yMywxMS40MiwwLDMuMjUtLjQxLDYuMjMtMS4yMiw4LjkzLS44MSwyLjctMi4wMyw1LjA3LTMuNjYsNy4xMi0xLjYzLDIuMDUtMy42MywzLjY2LTYsNC44NHMtNS4wOSwxLjg4LTguMTUsMi4wOWMtMy4wNC4yMS01Ljc3LS4xNC04LjE4LTEuMDRzLTQuNDItMi4yNy02LjAzLTQuMTJjLTEuNjEtMS44NS0yLjgzLTQuMTItMy42Ni02LjgzLS44Mi0yLjcxLTEuMjQtNS42OC0xLjI0LTguOXMuNDMtNi4zNiwxLjI5LTkuMTZjLjg2LTIuODEsMi4xLTUuMjMsMy43My03LjI1LDEuNjMtMi4wMywzLjYxLTMuNjEsNS45NS00Ljc1czQuOTktMS43OCw3Ljk3LTEuOTF2LS4wMlpNMjgxLjA4LDE2OS44NGMwLTMuMS0uNDYtNS43Ni0xLjM4LTcuOTgtLjkyLTIuMjMtMi4yMy0zLjg5LTMuOTQtNC45OHMtMy42Ny0xLjU5LTUuODgtMS40OGMtMS41OC4wOC0zLjAzLjQ3LTQuMzcsMS4xOXMtMi40OSwxLjczLTMuNDUsMy4wM2MtLjk3LDEuMy0xLjczLDIuOTMtMi4yOCw0LjktLjU2LDEuOTctLjg0LDQuMTYtLjg0LDYuNTdzLjI4LDQuNjEuODQsNi41NCwxLjM1LDMuNSwyLjM2LDQuNzJjMS4wMiwxLjIyLDIuMTksMi4xMSwzLjUxLDIuNjZzMi43Ny43Nyw0LjM0LjY3YzIuMDItLjEzLDMuODctLjgsNS41Ni0xLjk5czMuMDMtMi45Nyw0LjAzLTUuMzEsMS41LTUuMTgsMS41LTguNTNoMFoiLz4KICAgIDxwYXRoIGQ9Ik0zMDYuNCwxNzJjLTEuMTEuMDMtMS42Ni4wNS0yLjc2LjA5djEzLjQyYzAsMS43Ny0uMzYsMy4wOC0xLjA5LDMuOTVzLTEuNjcsMS4zMy0yLjg0LDEuMzhjLTEuMjYuMDYtMi4yMy0uMzQtMi45Mi0xLjE4cy0xLjA0LTIuMTEtMS4wNC0zLjgxdi0zMi4yNmMwLTEuODMuMzgtMy4xNywxLjE0LTQuMDFzMS45OS0xLjI4LDMuNjktMS4zMmM1LjEzLS4xMiw3LjctLjE2LDEyLjg0LS4yNCwxLjc3LS4wMywzLjI5LjAzLDQuNTUuMThzMi40LjQ4LDMuNDEuOTNjMS4yLjU0LDIuMzEsMS4zLDMuMjUsMi4zMXMxLjY2LDIuMTgsMi4xNSwzLjUyYy40OSwxLjM0LjczLDIuNzYuNzMsNC4yNiwwLDMuMDgtLjgyLDUuNTYtMi40Nyw3LjQzLTEuNjQsMS44Ny00LjE0LDMuMjItNy40Nyw0LjA3LDEuNC43NiwyLjc0LDEuOSw0LjAyLDMuNDJzMi40MiwzLjE0LDMuNDIsNC44NiwxLjc5LDMuMjcsMi4zNSw0LjY2Ljg0LDIuMzUuODQsMi44Ny0uMTYsMS4wOS0uNDksMS42M2MtLjMzLjU0LS43OC45OC0xLjM1LDEuM3MtMS4yMy40OS0xLjk3LjUxYy0uODkuMDItMS42My0uMTgtMi4yNC0uNjEtLjYtLjQzLTEuMTItLjk3LTEuNTYtMS42NHMtMS4wMy0xLjY1LTEuNzctMi45NWMtMS4yNy0yLjIxLTEuOS0zLjMxLTMuMTctNS41Mi0xLjEzLTIuMDMtMi4xNS0zLjU3LTMuMDUtNC42Mi0uOS0xLjA1LTEuOC0xLjc3LTIuNzMtMi4xNC0uOTItLjM3LTIuMDgtLjU0LTMuNDgtLjQ5aC4wMVpNMzEwLjkyLDE1NC4zOGMtMi45MS4wNi00LjM3LjA5LTcuMjguMTZ2MTEuNDhjMi44My0uMDgsNC4yNC0uMTIsNy4wNy0uMTksMS45LS4wNSwzLjQ5LS4yNiw0Ljc5LS42NCwxLjI5LS4zOCwyLjI4LS45OSwyLjk3LTEuODQuNjgtLjg1LDEuMDMtMi4wMSwxLjAzLTMuNDgsMC0xLjE1LS4yOC0yLjE2LS44My0zLjAzcy0xLjMyLTEuNTEtMi4yOS0xLjkzYy0uOTItLjQtMi43NC0uNTgtNS40NS0uNTJoLS4wMVoiLz4KICAgIDxwYXRoIGQ9Ik0zNTYuNTMsMTUyLjF2MjkuOTVjNi40NiwwLDkuNjcuMDQsMTYuMDguMTQsMS4yOC4wMiwyLjI2LjM2LDIuOTQsMS4wM3MxLjAyLDEuNSwxLjAyLDIuNS0uMzQsMS44My0xLjAxLDIuNDUtMS42Ni45MS0yLjk1Ljg5Yy03LjYzLS4xMy0xMS40Ni0uMTYtMTkuMTYtLjE2LTEuNzQsMC0yLjk4LS40LTMuNzQtMS4yLS43Ni0uOC0xLjE0LTIuMS0xLjE0LTMuOXYtMzEuNjljMC0xLjY4LjM2LTIuOTUsMS4wOS0zLjc5LjcyLS44NCwxLjY4LTEuMjYsMi44Ni0xLjI2czIuMTcuNDIsMi45MSwxLjI1LDEuMTEsMi4xLDEuMTEsMy44aDBaIi8+CiAgICA8cGF0aCBkPSJNNDA3LjIzLDE1NC44MmMtNy4wNC0uMTktMTAuNTctLjI2LTE3LjY0LS4zOHYxMC4xOWM2LjUxLjEzLDkuNzYuMjIsMTYuMjUuNDIsMS4xOS4wNCwyLjA4LjM2LDIuNjcuOTYuNTkuNi44OCwxLjM4Ljg4LDIuMzNzLS4yOSwxLjcyLS44NywyLjMtMS40Ny44NS0yLjY4LjhjLTYuNDktLjIyLTkuNzMtLjMyLTE2LjI1LS40N3YxMS44YzcuMzIuMjEsMTAuOTYuMzMsMTguMjUuNjQsMS4yMy4wNSwyLjE1LjQsMi43OCwxLjA1LjYyLjY1LjkzLDEuNDkuOTMsMi41MnMtLjMxLDEuNzgtLjkzLDIuMzctMS41NS44Ni0yLjc4LjhjLTguNS0uMzktMTIuNzUtLjU1LTIxLjI5LS43OS0xLjcxLS4wNS0yLjk0LS40OS0zLjY5LTEuMzEtLjc1LS44My0xLjEzLTIuMTQtMS4xMy0zLjk1di0zMS4xYzAtMS4yLjE3LTIuMTkuNS0yLjk0LjM0LS43Ni44Ni0xLjMxLDEuNTgtMS42NS43MS0uMzQsMS42My0uNSwyLjc0LS40OSw4LjMuMSwxMi40My4xNywyMC42OC4zNiwxLjI1LjAzLDIuMTcuMzUsMi43OC45N3MuOTEsMS40MS45MSwyLjM4LS4zLDEuNzgtLjkxLDIuMzZjLS42LjU4LTEuNTMuODYtMi43OC44MmgwWiIvPgogICAgPHBhdGggZD0iTTQ0Mi40MywxODcuMzhjLS43NC0yLjE5LTEuMTEtMy4yOS0xLjg0LTUuNDgtNi4yNy0uNDEtOS40LS42LTE1LjY3LS45NC0uNzQsMi4xMy0xLjEsMy4xOS0xLjg0LDUuMzItLjcyLDIuMDctMS4zMywzLjQ2LTEuODQsNC4xNy0uNTEuNzEtMS4zNCwxLjAzLTIuNS45Ny0uOTgtLjA1LTEuODUtLjQ5LTIuNi0xLjMyLS43NS0uODItMS4xMy0xLjczLTEuMTMtMi43MiwwLS41Ny4wOS0xLjE2LjI2LTEuNzYuMTctLjYuNDYtMS40NC44Ny0yLjUxLDMuOTQtMTAuNzMsNS45MS0xNi4xMiw5Ljg1LTI2Ljk0LjI4LS43OC42Mi0xLjcxLDEuMDEtMi44cy44MS0xLjk5LDEuMjYtMi43MWMuNDUtLjcxLDEuMDMtMS4yOCwxLjc2LTEuNzEuNzMtLjQyLDEuNjMtLjYxLDIuNjktLjU3LDEuMDkuMDUsMS45OS4zMSwyLjcyLjhzMS4zMiwxLjEsMS43NiwxLjgzYy40NS43NC44MywxLjUyLDEuMTMsMi4zNi4zMS44NC43LDEuOTYsMS4xNywzLjM2LDQuMDQsMTEuMiw2LjA1LDE2Ljg0LDEwLjEsMjguMTkuNzksMi4xNiwxLjE5LDMuNzIsMS4xOSw0LjY4cy0uMzcsMS44Ny0xLjEyLDIuNjVjLS43NS43Ny0xLjY1LDEuMTEtMi43LDEuMDMtLjYyLS4wNS0xLjE0LS4yMS0xLjU4LS40OC0uNDQtLjI4LS44MS0uNjMtMS4xMS0xLjA3cy0uNjItMS4xLS45Ni0xLjk5LS42NC0xLjY3LS44OC0yLjM1aDBaTTQyNi45NiwxNzQuNjRjNC42MS4yNCw2LjkxLjM3LDExLjUyLjY1LTIuMzMtNy4xNy0zLjQ5LTEwLjc0LTUuODItMTcuODUtMi4yOCw2LjktMy40MiwxMC4zNC01LjcsMTcuMjFoMFoiLz4KICAgIDxwYXRoIGQ9Ik00OTAuNzIsMTc4Ljg2djguMzFjMCwxLjExLS4wOSwxLjk4LS4yOSwyLjYycy0uNTYsMS4yLTEuMDgsMS42OGMtLjUzLjQ4LTEuMi45Mi0yLjAyLDEuMzMtMi4zNywxLjE4LTQuNjQsMS45OS02LjgyLDIuNDMtMi4xOC40NC00LjU2LjUzLTcuMTIuMjktMi45OS0uMjgtNS43MS0xLjA0LTguMTYtMi4yNy0yLjQ1LTEuMjMtNC41NC0yLjg5LTYuMjctNC45Ny0xLjczLTIuMDgtMy4wNS00LjUyLTMuOTgtNy4zNS0uOTMtMi44Mi0xLjM5LTUuOTMtMS4zOS05LjMycy40NC02LjM2LDEuMzQtOS4wNywyLjIxLTQuOTgsMy45NS02Ljc5YzEuNzQtMS44MiwzLjg2LTMuMTYsNi4zNy00LDIuNS0uODUsNS4zNS0xLjE1LDguNTMtLjg5LDIuNjIuMjEsNC45NC44LDYuOTcsMS43NSwyLjAyLjk2LDMuNjcsMi4wOSw0LjkzLDMuMzksMS4yNywxLjMsMi4yMiwyLjY1LDIuODYsNC4wMy42NCwxLjM4Ljk2LDIuNTkuOTcsMy42MiwwLDEuMTEtLjM3LDIuMDEtMS4xMSwyLjcycy0xLjYzLDEuMDEtMi42Ni45MWMtLjU3LS4wNS0xLjEyLS4yNS0xLjY0LS42LS41My0uMzUtLjk2LS44LTEuMzItMS4zNy0uOTgtMS43OS0xLjgtMy4xNC0yLjQ4LTQuMDctLjY4LS45My0xLjU4LTEuNzQtMi43My0yLjQzLTEuMTQtLjY5LTIuNi0xLjExLTQuMzctMS4yNS0xLjgyLS4xNS0zLjQ1LjA3LTQuODguNjZzLTIuNjUsMS41LTMuNjYsMi43NS0xLjc5LDIuODEtMi4zMiw0LjY5Yy0uNTQsMS44OC0uOCwzLjk4LS44LDYuMzEsMCw1LjA1LDEuMDUsOS4wMiwzLjE0LDExLjkyLDIuMDksMi45LDUuMDEsNC41Miw4Ljc2LDQuODYsMS44Mi4xNywzLjU0LjA2LDUuMTQtLjMyczMuMjMtLjk4LDQuODktMS44di03LjA0Yy0yLjQ1LS4yNC0zLjY4LS4zNS02LjEyLS41OC0xLjQ3LS4xMy0yLjU4LS40OC0zLjMzLTEuMDRzLTEuMTMtMS40My0xLjEzLTIuNjFjMC0uOTYuMzEtMS43My45NC0yLjMxczEuNDgtLjgxLDIuNTYtLjcyYzMuNTguMzIsNS4zOC40OSw4Ljk3LjgzLDEuMS4xMSwyLjA0LjMxLDIuOC42Ljc2LjI5LDEuMzkuODQsMS44NiwxLjY0cy43MSwxLjk1LjcxLDMuNDR2LjAyWiIvPgogICAgPHBhdGggZD0iTTQ5OC4zNiwxNzkuMzdjMC04LjM1LDAtMTIuNTItLjAyLTIwLjg3LDAtMS43OC4zNi0zLjA3LDEuMDktMy44OHMxLjY4LTEuMTUsMi44Ny0xLjAxYzEuMjQuMTQsMi4yMi43LDIuOTUsMS42N3MxLjEsMi4zNSwxLjEsNC4xMmMwLDguNTMsMCwxMi44LjAyLDIxLjMzLDAsMi40My4yNSw0LjQ4Ljc1LDYuMTYuNSwxLjY4LDEuMzgsMy4wNCwyLjY0LDQuMDksMS4yNiwxLjA0LDMuMDMsMS42OSw1LjMyLDEuOTYsMy4xNS4zNyw1LjM5LS4yNyw2LjctMS45MiwxLjMxLTEuNjYsMS45Ni00LjMyLDEuOTYtOC4wMSwwLTguNTYsMC0xMi44NC0uMDEtMjEuNCwwLTEuNzkuMzYtMy4wNywxLjA5LTMuODQuNzMtLjc3LDEuNzEtMS4wNywyLjkzLS44OSwxLjIyLjE4LDIuMjIuNzYsMi45OCwxLjc0Ljc2Ljk4LDEuMTQsMi4zNiwxLjE0LDQuMTQsMCw4LjI3LDAsMTIuNC4wMSwyMC42NiwwLDMuMzYtLjMsNi4xMi0uOTIsOC4yOS0uNjEsMi4xNy0xLjc3LDQuMDEtMy40Nyw1LjQ5LTEuNDUsMS4yNy0zLjE2LDIuMTItNS4wOSwyLjU2LTEuOTMuNDQtNC4xOS41MS02Ljc2LjIxLTMuMDYtLjM2LTUuNjktMS4wMS03Ljg5LTEuOThzLTMuOTktMi4yOC01LjM3LTMuOTQtMi40LTMuNzEtMy4wNS02LjEzYy0uNjUtMi40My0uOTctNS4yOC0uOTctOC41NmgwWiIvPgogICAgPHBhdGggZD0iTTU2Ny44NywxNzAuOWMtNy42Mi0xLjQyLTExLjM5LTIuMDgtMTguODctMy4zMXYxMC40MWM2Ljg5LDEuMDYsMTAuMzUsMS42MywxNy4zNiwyLjgyLDEuMjkuMjIsMi4yNS42NywyLjg5LDEuMzZzLjk2LDEuNDkuOTYsMi40My0uMzEsMS42NS0uOTQsMi4xNC0xLjYuNjMtMi45LjQyYy03LTEuMTMtMTAuNDctMS42Ny0xNy4zNS0yLjY5djEyLjA2YzcuNzMsMS4wNiwxMS42MywxLjYxLDE5LjUxLDIuNzYsMS4zMy4xOSwyLjMzLjY1LDMuMDEsMS4zNS42OC43MSwxLjAxLDEuNTcsMS4wMSwyLjU4cy0uMzQsMS43Mi0xLjAxLDIuMjNjLS42OC41Mi0xLjY4LjY4LTMuMDEuNS05LjE5LTEuMjUtMTMuNzMtMS44NS0yMi43Mi0zLjAxLTEuOC0uMjMtMy4wOS0uODEtMy44OC0xLjc1LS43OS0uOTMtMS4xOC0yLjM0LTEuMTgtNC4yLDAtMTIuODQtLjAxLTE5LjI2LS4wMi0zMi4xLDAtMS4yNC4xNy0yLjIzLjUzLTIuOTYuMzUtLjczLjktMS4yMSwxLjY1LTEuNDUuNzUtLjI0LDEuNzEtLjI2LDIuODgtLjA2LDguNzQsMS40NiwxMy4xNSwyLjI2LDIyLjA4LDQsMS4zNS4yNiwyLjM1Ljc2LDMuMDEsMS40OC42Ni43Mi45OSwxLjU2Ljk5LDIuNTFzLS4zMywxLjY5LS45OSwyLjE2LTEuNjYuNTctMy4wMS4zMmgwWiIvPgogIDwvZz4KICA8Zz4KICAgIDxwYXRoIGNsYXNzPSJzdDIiIGQ9Ik0yOS4wMSwzNzEuNTdjMC0zNy43NCwwLTc1LjQ4LS4wMS0xMTMuMjIsMjIuMTktNS4wOSw0NC40NC05LjM1LDY2LjkyLTEyLjk5LjMsNy43Mi40NiwxMS42Ljc2LDE5LjM2LTE2LjExLDIuNDQtMzIuMTYsNS4zMi00OC4xMyw4LjU2LjE4LDEwLjc4LjI2LDE2LjE4LjQ0LDI2Ljk3LDE0LjAzLTIuNjMsMjguMDctNS4wNiw0Mi4xNi03LjMxLjI5LDcuNzguNDMsMTEuNjguNzIsMTkuNDYtMTQuMjIsMi4yMS0yOC40LDQuNTgtNDIuNTcsNy4xMy4yNiwxNi4xMy41MywzMi4yNi43OSw0OC4zOS04LjQxLDEuNDEtMTIuNjMsMi4xNC0yMS4wOCwzLjY1WiIvPgogICAgPHBhdGggY2xhc3M9InN0MiIgZD0iTTIwMi4zMywzNDguNzljLTguOTUuNzQtMTMuNDMsMS4xNC0yMi4zOSwyLTQuMDItOS45My02LjA0LTE0Ljk1LTEwLjA4LTI1LjAxLTEzLjczLDEuMzUtMjcuNDQsMi44Ny00MS4xMyw0LjU2LTIuNDQsOS4wMS00LjksMTguMDItNy4zNywyNy4wMy04Ljg1LDEuMTQtMTMuMjgsMS43My0yMi4xNiwyLjk4LDExLjktNDAuMDEsMjMuMzQtODAuMTUsMzUuMDUtMTIwLjIyLDguNzctMS4wNCwxMy4xOC0xLjUyLDIyLjAzLTIuNDIsMTUuNjIsMzYuOTEsMzAuNzcsNzQuMDIsNDYuMDUsMTExLjA3aDBaTTE2Mi4zMywzMDYuOTVjLTUuMzUtMTMuNzgtMTAuNzEtMjcuNTYtMTYuMDktNDEuMzMtNC4wMiwxNC44MS04LjAzLDI5LjYzLTEyLjAzLDQ0LjQ1LDkuMzYtMS4xNCwxOC43NC0yLjE3LDI4LjEyLTMuMTJoMFoiLz4KICAgIDxwYXRoIGNsYXNzPSJzdDIiIGQ9Ik0yMTMuMzgsMzQ3LjkxYy0xLjM2LTM4LjE4LTIuNjgtNzYuMzUtNC4wNC0xMTQuNTMsOC4yMy0uNTMsMTIuMzYtLjc3LDIwLjYxLTEuMiwxNS4yMSwyNC41OSwyOS45NCw0OS40NSw0NC41Miw3NC40Mi0uNS0yNS4zOS0xLTUwLjc5LTEuNTItNzYuMTgsNy44OS0uMjQsMTEuODMtLjM0LDE5LjctLjUxLjYxLDM3Ljg3LDEuMTksNzUuNzUsMS44LDExMy42Mi04LjMuMjYtMTIuNDUuNDItMjAuNzQuNzgtMTQuNDctMjQuMTQtMjguODEtNDguMzYtNDMuNC03Mi40NC43NiwyNC44OSwxLjUxLDQ5Ljc5LDIuMjgsNzQuNjgtNy42OC41MS0xMS41Mi43OC0xOS4yLDEuMzdoLS4wMVoiLz4KICAgIDxwYXRoIGNsYXNzPSJzdDIiIGQ9Ik0zMzkuMjYsMzQyLjY0Yy0uMzItMzEuNDgtLjYzLTYyLjk3LS45NC05NC40NS0xMC4yNS4wNi0yMC41LjE4LTMwLjc0LjM3LS4xLTcuNjUtLjE1LTExLjQ1LS4yNS0xOC45NSwyNy4zNy0uMzgsNTQuNzItLjQ4LDgyLjA4LjE0LjA1LDcuNDMuMDgsMTEuMjEuMTQsMTguODMtMTAuMTctLjI3LTIwLjM2LS40MS0zMC41My0uNDQuMywzMS40OS42LDYyLjk3LjkxLDk0LjQ2LTguMjQtLjAzLTEyLjM5LS4wMy0yMC42Ni4wM2gtLjAxWiIvPgogICAgPHBhdGggY2xhc3M9InN0MiIgZD0iTTQ4NS4zMiwzNDguMDhjLTguOTQtLjc3LTEzLjQxLTEuMTEtMjIuMzYtMS43NC0zLjUzLTEwLjA5LTUuMzEtMTUuMjktOC44Ny0yNS43Ny0xMy42OC0uOS0yNy4zNy0xLjYxLTQxLjA3LTIuMTQtMy4zNSwxMC4xMy01LjAyLDE1LjE2LTguMzQsMjQuOTgtOC43Ny0uMjgtMTMuMTYtLjM4LTIxLjk0LS41NCwxMy4yLTM3LjI4LDI1Ljc5LTc0Ljc4LDM5LjUxLTExMS44OCw4LjkuNDMsMTMuMzUuNjcsMjIuMjcsMS4yMiwxNC4xNywzOC40MiwyNy4xNSw3Ny4yNyw0MC44MSwxMTUuODdoLS4wMVpNNDQ3LjQ1LDMwMC44NWMtNC43MS0xNC40NS05LjQ1LTI4Ljg5LTE0LjI1LTQzLjMxLTQuNjksMTMuOTMtOS4zMSwyNy44OC0xMy45MSw0MS44NCw5LjM5LjQsMTguNzguODksMjguMTYsMS40OGgwWiIvPgogICAgPHBhdGggY2xhc3M9InN0MiIgZD0iTTQ5MS4yOCwzMTIuMTJjOC4xMi0uMTUsMTIuMTctLjIsMjAuMjktLjI1LDEuOCwxMi42MSw4LjkzLDIyLjYyLDIyLjA2LDI0LjIzLDYuMjMuNzYsMTEuMTktLjA5LDE0LjgyLTIuNThzNS40OS01Ljk0LDUuNTctMTAuMzdjLjA1LTIuNjEtLjU0LTQuOTEtMS43Ni02LjkxLTEuMjItMS45OS0zLjEtMy43NC01LjY1LTUuMjRzLTguNzItNC4yNy0xOC41NS04LjEyYy04Ljc5LTMuNDUtMTUuMjYtNi43Ni0xOS4zNC0xMC4wNHMtNy4zMi03LjM3LTkuNy0xMi4yNmMtMi4zOS00Ljg5LTMuNTYtMTAuMDEtMy41LTE1LjMyLjA2LTYuMTksMS42OC0xMS41Nyw0Ljg4LTE2LjEzLDMuMTktNC41Niw3LjU4LTcuNzYsMTMuMTQtOS42NXMxMi43OS0yLjY5LDIwLjUxLTEuNTVjOS44NywxLjQ2LDIwLjYzLDQuMzIsMjguMjksMTEuNzIsNi4zNiw2LjE1LDEwLjY5LDE3Ljc2LDEwLjMxLDI2LjY2LTguMy0uNjUtMTIuNDctLjk2LTIwLjgtMS41NC0uODEtNi4yNi0yLjcxLTEwLjc0LTUuNy0xMy40OXMtNy4zLTQuNDMtMTIuOTEtNS4wM2MtNS42Mi0uNi05Ljk3LDAtMTMuMDQsMS43OHMtNC42Myw0LjI0LTQuNjcsNy4zOGMtLjA0LDMuMDksMS4zMSw1LjgzLDQuMDMsOC4yNCwyLjczLDIuNDEsOS4wNiw1LjM4LDE4Ljg3LDkuMDgsMTAuMzksMy45MiwxNy44OSw3Ljg0LDIyLjQ4LDExLjUyLDQuNTgsMy42OCw4LjA1LDguMTUsMTAuNDEsMTMuMzhzMy40NywxMS4zNSwzLjM1LDE4LjI3Yy0uMTgsMTAuMDEtMy42OSwxNy45My0xMC40NywyMy4zMy04LjUzLDYuOC0yMS4xMyw2LjgzLTMxLjQ2LDUuNTUtMjMuNjMtMi45My0zOS40LTE4LjYtNDEuNDUtNDIuNjdoMFoiLz4KICAgIDxwYXRoIGNsYXNzPSJzdDIiIGQ9Ik02MTguNDEsMzY2LjExYy4yNi0xNi4xOS41Mi0zMi4zNy43Ni00OC41Ni0xMS43Ni0yNC4yMS0yMy42NC00OC4zNC0zNi4yMS03Mi4xNSw5LjY4LDEuMiwxNC41LDEuODIsMjQuMSwzLjA4LDcuOTUsMTYuMjIsMTUuNiwzMi41NiwyMy4xMyw0OC45OCw3LjkxLTE0LjE4LDE1Ljc3LTI4LjM5LDIzLjg0LTQyLjQ5LDkuMjQsMS4zMywxMy44NCwyLjAxLDIyLjk3LDMuMzctMTIuNDMsMjAuOTctMjQuNzIsNDIuMDItMzcuMzEsNjIuOS0uMTksMTYuMzEtLjM4LDMyLjYxLS41OCw0OC45Mi04LjI4LTEuNy0xMi40Mi0yLjUxLTIwLjY5LTQuMDZoMFoiLz4KICA8L2c+Cjwvc3ZnPg==" alt="MLF Logo" class="logo">
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
const genDate = new Date(DATA.meta.generated);
const localStr = genDate.toLocaleString('de-AT', { day:'2-digit', month:'2-digit', year:'numeric', hour:'2-digit', minute:'2-digit' });
const tz = genDate.toLocaleString('de-AT', { timeZoneName:'short' }).split(' ').pop();
document.getElementById('meta').innerHTML =
  `<span>${DATA.meta.seasons[0]}–${DATA.meta.seasons[DATA.meta.seasons.length - 1]} \u00b7 ${DATA.meta.total_games.toLocaleString('de-AT')} Spiele</span>` +
  `<span class="last-update">Last update: <strong>${localStr} ${tz}</strong></span>`;
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
