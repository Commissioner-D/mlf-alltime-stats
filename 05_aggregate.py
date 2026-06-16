"""
Step 5: Stats aggregieren
==========================

Liest alle Saison-JSONs + team_mapping.json und baut die finale stats.json,
die das Frontend laedt.

Output: stats.json
"""

import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent
NFL_DIR = SCRIPT_DIR / "data" / "nfl"
FLEA_DIR = SCRIPT_DIR / "data" / "fleaflicker"
MAPPING_FILE = SCRIPT_DIR / "team_mapping.json"
OUTPUT_FILE = SCRIPT_DIR / "stats.json"


def load_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def load_seasons(directory):
    seasons = {}
    for f in sorted(directory.glob("*.json")):
        if f.stem.isdigit():
            seasons[int(f.stem)] = load_json(f)
    return seasons


def is_championship_round(round_name):
    if not round_name:
        return False
    r = round_name.lower()
    return 'championship' in r or 'fantasy super bowl' in r


# ============================================================
# Stats-Berechnungen
# ============================================================

def team_table(games, mapping):
    """Pro Canonical-Team: Games, Wins, Losses, Points, Seasons."""
    acc = defaultdict(lambda: {
        'games': 0, 'wins': 0, 'losses': 0, 'ties': 0,
        'points': 0.0, 'points_against': 0.0, 'seasons': set()
    })
    for g in games:
        for name, sf, sa in [(g['t1'], g['t1_score'], g['t2_score']),
                              (g['t2'], g['t2_score'], g['t1_score'])]:
            d = acc[name]
            d['games'] += 1
            d['points'] += sf
            d['points_against'] += sa
            d['seasons'].add(g['season'])
            if sf > sa:
                d['wins'] += 1
            elif sf < sa:
                d['losses'] += 1
            else:
                d['ties'] += 1

    rows = []
    for team in mapping['canonical_teams']:
        name = team['name']
        d = acc.get(name)
        if not d or d['games'] == 0:
            continue
        seasons = len(d['seasons'])
        rows.append({
            'team': name,
            'active': team['active'],
            'seasons': seasons,
            'games': d['games'],
            'wins': d['wins'],
            'losses': d['losses'],
            'ties': d['ties'],
            'pct': round(d['wins'] / d['games'], 3) if d['games'] else 0,
            'points': round(d['points'], 2),
            'points_against': round(d['points_against'], 2),
            'avg_pg': round(d['points'] / d['games'], 2) if d['games'] else 0,
            'avg_ps': round(d['points'] / seasons, 2) if seasons else 0,
        })
    return rows


def compute_top_scores(games, n=10):
    rows = []
    for g in games:
        rows.append({'team': g['t1'], 'team_id': g['t1_id'], 'opponent': g['t2'],
                     'score': g['t1_score'], 'opp_score': g['t2_score'],
                     'season': g['season'], 'week': g['week'],
                     'type': g['type'], 'round': g.get('round'),
                     'game_id': g.get('game_id')})
        rows.append({'team': g['t2'], 'team_id': g['t2_id'], 'opponent': g['t1'],
                     'score': g['t2_score'], 'opp_score': g['t1_score'],
                     'season': g['season'], 'week': g['week'],
                     'type': g['type'], 'round': g.get('round'),
                     'game_id': g.get('game_id')})
    rows.sort(key=lambda x: -x['score'])
    return rows[:n]


def compute_champions(nfl_seasons, flea_seasons, lookup):
    champs = []
    for year in sorted(set(nfl_seasons) | set(flea_seasons)):
        if year in nfl_seasons:
            data = nfl_seasons[year]
            platform = 'nfl'
        else:
            data = flea_seasons[year]
            platform = 'fleaflicker'
        cid = data.get('champion_id')
        rid = data.get('runner_up_id')
        champ = lookup.get((platform, cid, year)) if cid else None
        runner = lookup.get((platform, rid, year)) if rid else None
        score = None
        for g in data.get('postseason', []):
            if is_championship_round(g.get('round')) and {g['t1_id'], g['t2_id']} == {cid, rid}:
                if g['t1_id'] == cid:
                    score = [round(g['t1_score'], 2), round(g['t2_score'], 2)]
                else:
                    score = [round(g['t2_score'], 2), round(g['t1_score'], 2)]
                break
        champs.append({
            'season': year, 'champion': champ, 'runner_up': runner, 'score': score
        })
    return champs


def compute_postseason_perf(all_games, mapping, nfl_seasons, flea_seasons, lookup):
    """Pro Team: Seasons, Playoffs, Div Titles, 1st Round Bye, 1st Overall."""

    # Sammle: pro Saison + Team -> teilgenommen, playoff, division_rank=1, overall_rank=1, hatte_bye
    team_season_data = defaultdict(lambda: defaultdict(lambda: {
        'in_league': False, 'playoffs': False, 'div_title': False,
        'overall_1': False, 'bye': False
    }))

    # in_league + playoffs aus Games
    for g in all_games:
        for name in (g['t1'], g['t2']):
            d = team_season_data[name][g['season']]
            d['in_league'] = True
            if g['type'] == 'postseason':
                d['playoffs'] = True

    # Bye: hatte Postseason-Games aber kein Quarterfinal
    by_team_season_round = defaultdict(set)
    for g in all_games:
        if g['type'] != 'postseason':
            continue
        for name in (g['t1'], g['t2']):
            by_team_season_round[(name, g['season'])].add(g.get('round'))
    for (name, season), rounds in by_team_season_round.items():
        had_qf = any(r and 'quarterfinal' in r.lower() for r in rounds)
        if not had_qf and rounds:
            team_season_data[name][season]['bye'] = True

    # NFL.com: Div-Title + Overall-1 direkt aus den geparsten teams[].division_rank/overall_rank
    for year, data in nfl_seasons.items():
        for tid_str, tinfo in data.get('teams', {}).items():
            tid = int(tid_str)
            canonical = lookup.get(('nfl', tid, year))
            if not canonical:
                continue
            if tinfo.get('division_rank') == 1:
                team_season_data[canonical][year]['div_title'] = True
            if tinfo.get('overall_rank') == 1:
                team_season_data[canonical][year]['overall_1'] = True

    # Fleaflicker: berechne Div-Rank + Overall-Rank aus den Regular-Season-Records
    for year, data in flea_seasons.items():
        # W-L-PF pro team_id (regular season only)
        records = defaultdict(lambda: {'w': 0, 'l': 0, 'pf': 0.0})
        for g in data.get('regular_season', []):
            for tid, sf, sa in [(g['t1_id'], g['t1_score'], g['t2_score']),
                                 (g['t2_id'], g['t2_score'], g['t1_score'])]:
                r = records[tid]
                r['pf'] += sf
                if sf > sa:
                    r['w'] += 1
                elif sf < sa:
                    r['l'] += 1

        # Gruppiere nach Division
        divs = defaultdict(list)
        for tid_str, tinfo in data.get('teams', {}).items():
            div = tinfo.get('division')
            if div:
                divs[div].append(int(tid_str))

        # Pro Division: sort by (-w, l, -pf), top = Winner
        for div_name, tids in divs.items():
            tids.sort(key=lambda t: (-records[t]['w'], records[t]['l'], -records[t]['pf']))
            if tids:
                top_tid = tids[0]
                canonical = lookup.get(('fleaflicker', top_tid, year))
                if canonical:
                    team_season_data[canonical][year]['div_title'] = True

        # Overall #1
        all_tids = list(records.keys())
        all_tids.sort(key=lambda t: (-records[t]['w'], records[t]['l'], -records[t]['pf']))
        if all_tids:
            top_tid = all_tids[0]
            canonical = lookup.get(('fleaflicker', top_tid, year))
            if canonical:
                team_season_data[canonical][year]['overall_1'] = True

    # Aggregiere pro Team
    rows = []
    for team in mapping['canonical_teams']:
        name = team['name']
        seasons_data = team_season_data.get(name, {})
        if not seasons_data:
            continue
        seasons = sum(1 for d in seasons_data.values() if d['in_league'])
        playoffs = sum(1 for d in seasons_data.values() if d['playoffs'])
        div_titles = sum(1 for d in seasons_data.values() if d['div_title'])
        byes = sum(1 for d in seasons_data.values() if d['bye'])
        ov1 = sum(1 for d in seasons_data.values() if d['overall_1'])

        def pct(x):
            return round(x / seasons, 3) if seasons else 0

        rows.append({
            'team': name,
            'active': team['active'],
            'seasons': seasons,
            'playoffs': playoffs,
            'playoffs_pct': pct(playoffs),
            'division_titles': div_titles,
            'division_titles_pct': pct(div_titles),
            'first_bye': byes,
            'first_bye_pct': pct(byes),
            'first_overall': ov1,
            'first_overall_pct': pct(ov1),
        })
    return rows


def compute_h2h(all_games):
    """Pro Team-Paar: Wins/Losses/Points + Game-Liste."""
    h2h = defaultdict(lambda: defaultdict(lambda: {
        'wins': 0, 'losses': 0, 'ties': 0,
        'pf': 0.0, 'pa': 0.0, 'games': []
    }))
    for g in all_games:
        for a, a_id, sa, b, sb in [(g['t1'], g['t1_id'], g['t1_score'], g['t2'], g['t2_score']),
                                    (g['t2'], g['t2_id'], g['t2_score'], g['t1'], g['t1_score'])]:
            h = h2h[a][b]
            h['pf'] += sa
            h['pa'] += sb
            if sa > sb:
                h['wins'] += 1
            elif sa < sb:
                h['losses'] += 1
            else:
                h['ties'] += 1
            h['games'].append({
                'season': g['season'], 'week': g['week'],
                'type': g['type'], 'round': g.get('round'),
                'sf': sa, 'sa': sb,
                'team_id': a_id, 'game_id': g.get('game_id'),
            })
    out = {}
    for a, b_dict in h2h.items():
        out[a] = {}
        for b, h in b_dict.items():
            h['pf'] = round(h['pf'], 2)
            h['pa'] = round(h['pa'], 2)
            h['games'].sort(key=lambda x: (x['season'], x['week']))
            out[a][b] = h
    return out


def compute_records(all_games, n=10):
    per_team_scores = []
    for g in all_games:
        per_team_scores.append({
            'team': g['t1'], 'team_id': g['t1_id'], 'opponent': g['t2'],
            'score': g['t1_score'], 'opp_score': g['t2_score'],
            'season': g['season'], 'week': g['week'],
            'type': g['type'], 'round': g.get('round'),
            'game_id': g.get('game_id')
        })
        per_team_scores.append({
            'team': g['t2'], 'team_id': g['t2_id'], 'opponent': g['t1'],
            'score': g['t2_score'], 'opp_score': g['t1_score'],
            'season': g['season'], 'week': g['week'],
            'type': g['type'], 'round': g.get('round'),
            'game_id': g.get('game_id')
        })

    highest = sorted(per_team_scores, key=lambda x: -x['score'])[:n]
    lowest = sorted(per_team_scores, key=lambda x: x['score'])[:n]

    margins = []
    for g in all_games:
        if g['t1_score'] == g['t2_score']:
            continue
        if g['t1_score'] > g['t2_score']:
            w, w_id, ws = g['t1'], g['t1_id'], g['t1_score']
            l, l_id, ls = g['t2'], g['t2_id'], g['t2_score']
        else:
            w, w_id, ws = g['t2'], g['t2_id'], g['t2_score']
            l, l_id, ls = g['t1'], g['t1_id'], g['t1_score']
        margins.append({
            'winner': w, 'winner_id': w_id, 'loser': l, 'loser_id': l_id,
            'winner_score': ws, 'loser_score': ls,
            'margin': round(ws - ls, 2),
            'season': g['season'], 'week': g['week'],
            'type': g['type'], 'round': g.get('round'),
            'game_id': g.get('game_id')
        })
    blowouts = sorted(margins, key=lambda x: -x['margin'])[:n]
    closest = sorted(margins, key=lambda x: x['margin'])[:n]

    return {
        'highest': highest,
        'lowest': lowest,
        'blowouts': blowouts,
        'closest': closest,
    }


def compute_streaks(all_games, mapping, n=10):
    """Laengste Win/Loss Streak pro Team. Spiele chronologisch ueber alle Saisons."""
    team_chronos = defaultdict(list)
    for g in sorted(all_games, key=lambda x: (x['season'], x['week'])):
        for name, sf, sa in [(g['t1'], g['t1_score'], g['t2_score']),
                              (g['t2'], g['t2_score'], g['t1_score'])]:
            outcome = 'W' if sf > sa else ('L' if sf < sa else 'T')
            team_chronos[name].append({
                'outcome': outcome,
                'season': g['season'],
                'week': g['week'],
            })

    def longest_with_range(seq, target):
        """Returns (length, start_entry, end_entry) of longest streak."""
        best = 0
        best_start = best_end = None
        cur = 0
        cur_start = None
        for entry in seq:
            if entry['outcome'] == target:
                if cur == 0:
                    cur_start = entry
                cur += 1
                if cur > best:
                    best = cur
                    best_start = cur_start
                    best_end = entry
            else:
                cur = 0
        return best, best_start, best_end

    wins = []
    losses = []
    for team in mapping['canonical_teams']:
        name = team['name']
        seq = team_chronos.get(name, [])
        if not seq:
            continue
        for kind, dest in [('W', wins), ('L', losses)]:
            length, start, end = longest_with_range(seq, kind)
            if length == 0:
                continue
            dest.append({
                'team': name,
                'streak': length,
                'from': f"{start['season']} Wk {start['week']}",
                'to': f"{end['season']} Wk {end['week']}",
            })
    wins.sort(key=lambda x: -x['streak'])
    losses.sort(key=lambda x: -x['streak'])
    return {'win': wins[:n], 'loss': losses[:n]}


# ============================================================
# Main
# ============================================================

def main():
    print("Lade Daten...")
    mapping = load_json(MAPPING_FILE)
    nfl_seasons = load_seasons(NFL_DIR)
    flea_seasons = load_seasons(FLEA_DIR)
    print(f"  {len(nfl_seasons)} NFL Saisons, {len(flea_seasons)} Flea Saisons")

    # Canonical-Lookup: (platform, team_id, season) -> canonical_name
    lookup = {}
    for team in mapping['canonical_teams']:
        for m in team['memberships']:
            for s in m['seasons']:
                lookup[(m['platform'], m['team_id'], s)] = team['name']

    # Flatten alle Spiele mit Canonical-Namen
    all_games = []
    unmapped = 0
    for src_seasons, platform in [(nfl_seasons, 'nfl'), (flea_seasons, 'fleaflicker')]:
        for year, data in src_seasons.items():
            for type_name, key in [('regular', 'regular_season'),
                                    ('postseason', 'postseason')]:
                for g in data.get(key, []):
                    t1 = lookup.get((platform, g['t1_id'], year))
                    t2 = lookup.get((platform, g['t2_id'], year))
                    if not t1 or not t2:
                        unmapped += 1
                        continue
                    all_games.append({
                        'season': year, 'week': g['week'],
                        'type': type_name, 'round': g.get('round'),
                        'platform': platform,
                        'game_id': g.get('game_id'),
                        't1': t1, 't1_id': g['t1_id'], 't1_score': g['t1_score'],
                        't2': t2, 't2_id': g['t2_id'], 't2_score': g['t2_score'],
                    })
    print(f"  {len(all_games)} Spiele insgesamt, {unmapped} unzugeordnet")

    # Subsets
    rs_games = [g for g in all_games if g['type'] == 'regular']
    po_games = [g for g in all_games if g['type'] == 'postseason']
    fb_games = [g for g in po_games if is_championship_round(g.get('round'))]

    print("Berechne Stats...")

    output = {
        'meta': {
            'generated': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
            'seasons': sorted(set(nfl_seasons) | set(flea_seasons)),
            'total_games': len(all_games),
        },
        'teams': [
            {'name': t['name'], 'active': t['active'], 'owner': t.get('owner_label', '')}
            for t in mapping['canonical_teams']
        ],
        'stats': {
            'overall': team_table(all_games, mapping),
            'regular_season': team_table(rs_games, mapping),
            'postseason': team_table(po_games, mapping),
            'fantasy_bowl': team_table(fb_games, mapping),
        },
        'top_scores': compute_top_scores(all_games),
        'champions': compute_champions(nfl_seasons, flea_seasons, lookup),
        'postseason_perf': compute_postseason_perf(
            all_games, mapping, nfl_seasons, flea_seasons, lookup
        ),
        'h2h': compute_h2h(all_games),
        'records': compute_records(all_games),
        'streaks': compute_streaks(all_games, mapping),
    }

    OUTPUT_FILE.write_text(
        json.dumps(output, indent=2, ensure_ascii=False), encoding='utf-8'
    )
    print(f"\nGeschrieben: {OUTPUT_FILE.name}")
    print(f"  {len(output['teams'])} Canonical Teams")
    print(f"  {len(output['stats']['overall'])} Teams mit Stats")
    print(f"  {len(output['champions'])} Champion-Eintraege")
    print()
    print("Champions (chronologisch):")
    for c in output['champions']:
        s = f"{c['score'][0]}-{c['score'][1]}" if c['score'] else '?'
        print(f"  {c['season']}: {c['champion']:32s} bezwingt {c['runner_up']:32s}  ({s})")


if __name__ == "__main__":
    main()
