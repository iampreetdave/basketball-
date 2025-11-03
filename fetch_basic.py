import requests
import pandas as pd
import time


API_KEY = "51d6613b3fa12b59a598b1ebf967427d"
BASE_URL = "https://v1.basketball.api-sports.io"
HEADERS = {'x-apisports-key': API_KEY}


def get_games(season):
    response = requests.get(
        f"{BASE_URL}/games",
        headers=HEADERS,
        params={'league': 12, 'season': season},
        timeout=30
    )
    if response.status_code == 200:
        return response.json().get('response', [])
    return []


def get_stats(game_id):
    time.sleep(1.5)
    response = requests.get(
        f"{BASE_URL}/games/statistics/teams",
        headers=HEADERS,
        params={'id': game_id},
        timeout=30
    )
    if response.status_code == 200:
        return response.json().get('response', [])
    return []


def determine_winner(home_score, away_score):
    """Determine the winner based on scores"""
    if home_score > away_score:
        return 'Home'
    elif away_score > home_score:
        return 'Away'
    else:
        return 'Draw'


# Try multiple season formats
seasons = ['2024-2025', '2024', '2023-2024', '2023', '2022-2023', '2022', '2021-2022', '2021', '2020-2021', '2020', '2019-2020']


all_games = []
for season in seasons:
    print(f"Trying season: {season}")
    games = get_games(season)
    print(f"  Found: {len(games)} games")
    
    if games:
        finished = [g for g in games if g.get('status', {}).get('short') == 'FT']
        print(f"  Finished: {len(finished)} games")
        all_games.extend(finished[:100])
        if len(all_games) >= 100:
            break


print(f"\nTotal games collected: {len(all_games)}")


if not all_games:
    print("NO GAMES FOUND! Check:")
    print("1. API key valid")
    print("2. NBA league ID = 12")
    print("3. Try: https://v1.basketball.api-sports.io/games?league=12&season=2023-2024")
    exit()


# Process games
data = []
for i, game in enumerate(all_games[:100], 1):
    print(f"[{i}/100] Game {game['id']}")
    
    stats = get_stats(game['id'])
    
    # Extract scores
    home_score = game['scores']['home']['total']
    away_score = game['scores']['away']['total']
    
    row = {
        'game_id': game['id'],
        'date': game['date'],
        'home_team_id': game['teams']['home']['id'],
        'home_team': game['teams']['home']['name'],
        'away_team_id': game['teams']['away']['id'],
        'away_team': game['teams']['away']['name'],
        'home_score': home_score,
        'away_score': away_score,
        'winner': determine_winner(home_score, away_score),  # ADDED
    }
    
    if stats and len(stats) >= 2:
        home_stats = stats[0]
        away_stats = stats[1]
        
        row.update({
            'home_fg_made': home_stats.get('field_goals', {}).get('total'),
            'home_fg_att': home_stats.get('field_goals', {}).get('attempts'),
            'home_fg_pct': home_stats.get('field_goals', {}).get('percentage'),
            'home_3p_made': home_stats.get('threepoint_goals', {}).get('total'),
            'home_3p_att': home_stats.get('threepoint_goals', {}).get('attempts'),
            'home_3p_pct': home_stats.get('threepoint_goals', {}).get('percentage'),
            'home_ft_made': home_stats.get('freethrows_goals', {}).get('total'),
            'home_ft_att': home_stats.get('freethrows_goals', {}).get('attempts'),
            'home_ft_pct': home_stats.get('freethrows_goals', {}).get('percentage'),
            'home_reb': home_stats.get('rebounds', {}).get('total'),
            'home_ast': home_stats.get('assists'),
            'home_stl': home_stats.get('steals'),
            'home_blk': home_stats.get('blocks'),
            'home_tov': home_stats.get('turnovers'),
            'away_fg_made': away_stats.get('field_goals', {}).get('total'),
            'away_fg_att': away_stats.get('field_goals', {}).get('attempts'),
            'away_fg_pct': away_stats.get('field_goals', {}).get('percentage'),
            'away_3p_made': away_stats.get('threepoint_goals', {}).get('total'),
            'away_3p_att': away_stats.get('threepoint_goals', {}).get('attempts'),
            'away_3p_pct': away_stats.get('threepoint_goals', {}).get('percentage'),
            'away_ft_made': away_stats.get('freethrows_goals', {}).get('total'),
            'away_ft_att': away_stats.get('freethrows_goals', {}).get('attempts'),
            'away_ft_pct': away_stats.get('freethrows_goals', {}).get('percentage'),
            'away_reb': away_stats.get('rebounds', {}).get('total'),
            'away_ast': away_stats.get('assists'),
            'away_stl': away_stats.get('steals'),
            'away_blk': away_stats.get('blocks'),
            'away_tov': away_stats.get('turnovers'),
        })
    
    data.append(row)


df = pd.DataFrame(data)
df.to_csv('NBA_data_FINAL.csv', index=False)
print(f"\nDONE! Saved {len(df)} games to NBA_best.csv")
print(f"Columns: {len(df.columns)}")
print(f"\nWinner Distribution:")
print(df['winner'].value_counts())
