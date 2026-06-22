"""
Step 3: Fleaflicker Daten fetchen
==================================

Holt alle Saisons von der Fleaflicker API.
Cache: data/fleaflicker/{year}.json

Output-Struktur identisch zum NFL-Parser:
  {season, teams, regular_season[], postseason[], champion_id, runner_up_id}
"""

import urllib.request
import urllib.error
import json
import time
from pathlib import Path

LEAGUE_ID = 338210
SPORT = "NFL"
SCRIPT_DIR = Path(__file__).parent
FLEA_DIR = SCRIPT_DIR / "data" / "fleaflicker"
API_BASE = "https://www.fleaflicker.com/api"
RATE_LIMIT = 0.5

# Auto-Season: erkennt automatisch welche Saisons geholt werden.
# NFL-Saison startet im September. Ab August wird das aktuelle Jahr
# als laufende Saison behandelt und bei jedem Lauf neu gefetcht.
# Aeltere Saisons kommen aus dem Cache.
FIRST_SEASON = 2023
FORCE_REFRESH_CURRENT = True

from datetime import datetime, timezone
_now = datetime.now(timezone.utc)
CURRENT_SEASON = _now.year if _now.month >= 8 else _now.year - 1
SEASONS = list(range(FIRST_SEASON, CURRENT_SEASON + 1))


def fetch_api(endpoint, **params):
    params['sport'] = SPORT
    query = '&'.join(f"{k}={v}" for k, v in params.items())
    url = f"{API_BASE}/{endpoint}?{query}"
    req = urllib.request.Request(url, headers={'User-Agent': 'mlf-stats/1.0'})
    with urllib.request.urlopen(req, timeout=30) as r:
        time.sleep(RATE_LIMIT)
        return json.loads(r.read().decode('utf-8'))


def g(obj, *keys):
    """Get value trying multiple key names (camelCase/snake_case)."""
    if not obj:
        return None
    for k in keys:
        if isinstance(obj, dict) and k in obj:
            return obj[k]
    return None


def get_score(side_score):
    """Extract numerischen Score aus FantasyLineScore."""
    s = g(side_score, 'score')
    if not s:
        return None
    v = g(s, 'value')
    return float(v) if v is not None else None


def classify_round(game, week, first_playoff_week, last_playoff_week):
    """Bestimme Round-Name. Returns None wenn nicht 'Weg zum Finale'."""
    if g(game, 'isConsolation', 'is_consolation'):
        return None
    if g(game, 'isThirdPlaceGame', 'is_third_place_game'):
        return None
    is_playoff = g(game, 'isPlayoffs', 'is_playoffs')
    if not is_playoff:
        return None
    if g(game, 'isChampionshipGame', 'is_championship_game'):
        return 'Championship'
    # Bei 3 Playoff-Wochen: erste = QF, zweite = SF, dritte = Final
    if first_playoff_week is None:
        return 'Playoff'
    offset = week - first_playoff_week
    if offset == 0:
        return 'Quarterfinal'
    elif offset == 1:
        return 'Semifinal'
    else:
        return 'Championship'


def fetch_season(season):
    cache = FLEA_DIR / f"{season}.json"
    if cache.exists() and not (FORCE_REFRESH_CURRENT and season == CURRENT_SEASON):
        print(f"  {season}: aus Cache")
        return json.loads(cache.read_text(encoding='utf-8'))

    print(f"  {season}: fetche...")
    result = {
        'season': season,
        'teams': {},
        'regular_season': [],
        'postseason': [],
        'champion_id': None,
        'runner_up_id': None,
    }

    # Standings -> teams + owners + division ranks
    try:
        standings = fetch_api("FetchLeagueStandings", league_id=LEAGUE_ID, season=season)
    except urllib.error.HTTPError as e:
        print(f"    HTTP {e.code} bei Standings")
        return result

    for div in standings.get('divisions', []) or []:
        for team in g(div, 'teams') or []:
            tid = g(team, 'id')
            name = g(team, 'name')
            owners = g(team, 'owners') or []
            owner_name = g(owners[0], 'displayName', 'display_name') if owners else None
            result['teams'][str(tid)] = {
                'team_id': tid,
                'name': name,
                'owner': owner_name,
                'division': g(div, 'name'),
            }

    # Scoreboards pro Woche, mit Playoff-Detection
    playoff_weeks = []
    all_games = []

    for week in range(1, 18):
        try:
            sb = fetch_api("FetchLeagueScoreboard",
                           league_id=LEAGUE_ID, season=season, scoring_period=week)
        except urllib.error.HTTPError:
            break

        games = g(sb, 'games') or []
        if not games:
            continue

        for game in games:
            is_final = g(game, 'isFinalScore', 'is_final_score')
            if not is_final:
                continue

            home = g(game, 'home') or {}
            away = g(game, 'away') or {}
            h_score = get_score(g(game, 'homeScore', 'home_score'))
            a_score = get_score(g(game, 'awayScore', 'away_score'))

            if h_score is None or a_score is None:
                continue

            entry = {
                'week': week,
                'game_id': g(game, 'id'),
                't1_id': g(home, 'id'),
                't1_name': g(home, 'name'),
                't1_score': h_score,
                't2_id': g(away, 'id'),
                't2_name': g(away, 'name'),
                't2_score': a_score,
                'raw': game,
            }
            all_games.append(entry)

            if g(game, 'isPlayoffs', 'is_playoffs') and not g(game, 'isConsolation', 'is_consolation'):
                if week not in playoff_weeks:
                    playoff_weeks.append(week)

    playoff_weeks.sort()
    first_po = playoff_weeks[0] if playoff_weeks else None
    last_po = playoff_weeks[-1] if playoff_weeks else None

    # Klassifikation
    for entry in all_games:
        game = entry.pop('raw')
        week = entry['week']
        round_name = classify_round(game, week, first_po, last_po)
        if round_name:
            entry['round'] = round_name
            result['postseason'].append(entry)
        elif first_po is None or week < first_po:
            # Echte Regular Season: nur Spiele VOR der ersten Playoff-Woche
            result['regular_season'].append(entry)
        # Andere Games (Consolation, 3rd-place, etc.) ignorieren

    # Champion: Gewinner des Championship-Spiels
    for g_entry in result['postseason']:
        if g_entry['round'] == 'Championship':
            if g_entry['t1_score'] > g_entry['t2_score']:
                result['champion_id'] = g_entry['t1_id']
                result['runner_up_id'] = g_entry['t2_id']
            else:
                result['champion_id'] = g_entry['t2_id']
                result['runner_up_id'] = g_entry['t1_id']

    # Cache
    FLEA_DIR.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')

    return result


def main():
    print(f"Fleaflicker fetchen: League {LEAGUE_ID}")
    print(f"Saisons: {SEASONS}\n")

    for season in SEASONS:
        data = fetch_season(season)
        n_rs = len(data['regular_season'])
        n_po = len(data['postseason'])
        n_teams = len(data['teams'])
        champ = data['teams'].get(str(data['champion_id']), {}).get('name', '?') \
                if data['champion_id'] else '? (Saison laeuft noch?)'
        runner = data['teams'].get(str(data['runner_up_id']), {}).get('name', '?') \
                if data['runner_up_id'] else '?'
        print(f"  {season}: {n_teams} Teams, {n_rs} RS, {n_po} PO")
        print(f"        Champion: {champ}  |  Runner-up: {runner}")
        print()


if __name__ == "__main__":
    main()
